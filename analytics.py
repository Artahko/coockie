"""File with methods for calculations."""
import numpy as np
from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_M = 6_371_000

def filter_physical_limits(df):
    MAX_H_SPEED = 60
    MAX_V_SPEED = 40
    MAX_ACCEL = 40
    MIN_DT = 0.05

    df = df.copy()

    dt = df["time"].diff()

    valid_dt = dt > MIN_DT

    v_vertical = df["alt"].diff().abs() / dt

    df["v_vertical"] = v_vertical

    if "speed" in df.columns:
        v_horizontal = df["speed"]
    elif "vx" in df.columns and "vy" in df.columns:
        v_horizontal = np.sqrt(df["vx"]**2 + df["vy"]**2)
    else:
        v_horizontal = None

    if v_horizontal is not None:
        df["v_horizontal"] = v_horizontal

    accel = np.sqrt(
        df["acc_x"]**2 +
        df["acc_y"]**2 +
        df["acc_z"]**2
    )

    df["accel_mag"] = accel

    mask = valid_dt

    mask &= df["v_vertical"] < MAX_V_SPEED

    if "v_horizontal" in df:
        mask &= df["v_horizontal"] < MAX_H_SPEED

    mask &= df["accel_mag"] < MAX_ACCEL

    return df[mask]

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Unlike simple Euclidean distance, Haversine accounts for Earth's spherical shape.
    a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
    d = 2R · atan2(√a, √(1−a))

    Args:
        lat1, lon1: Latitude and longitude of the first point in decimal degrees.
        lat2, lon2: Latitude and longitude of the second point.
    Returns:
        Distance in meters.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(a), sqrt(1 - a))


def total_distance(df) -> float:
    """
    Computes the total path length of the flight by summing Haversine distances
    between all consecutive GPS points.
    """
    lats = df["lat"].values
    lons = df["lon"].values
    return sum(
        haversine(lats[i], lons[i], lats[i + 1], lons[i + 1])
        for i in range(len(lats) - 1)
    )


def trapezoid_integrate(values: np.ndarray, times: np.ndarray) -> np.ndarray:
    """
    Numerically integrates a signal over time using the trapezoidal rule
    which approximates the area under the curve by treating
    each interval as a trapezoid rather than a rectangle, achieving O(h²)
    accuracy vs O(h) for the rectangle method.

    result[i] = result[i-1] + (values[i-1] + values[i]) / 2 · Δt

    Note on IMU drift: when integrating accelerations twice to get position,
    errors accumulate quadratically over time. This is why GPS data is
    preferred as the primary source when available.
    """
    result = np.zeros(len(values))
    for i in range(1, len(values)):
        dt = times[i] - times[i - 1]
        result[i] = result[i - 1] + (values[i - 1] + values[i]) / 2 * dt
    return result


def compute_velocity_from_imu(df):
    """
    Derives velocity components by integrating IMU accelerometer readings
    along each axis using the trapezoidal method.
    Used as a fallback when GPS-derived speed data is unavailable.
    Results are subject to drift due to cumulative integration error.

    Adds columns to the DataFrame: vx_imu, vy_imu, vz_imu (all in m/s).

    Args:
        df: DataFrame with columns 'time', 'acc_x', 'acc_y', 'acc_z'.
    Returns:
        Copy of the DataFrame with velocity columns appended.
    """
    t = df["time"].values
    df = df.copy()
    df["vx_imu"] = trapezoid_integrate(df["acc_x"].values, t)
    df["vy_imu"] = trapezoid_integrate(df["acc_y"].values, t)
    df["vz_imu"] = trapezoid_integrate(df["acc_z"].values, t)
    return df


def compute_metrics(df) -> dict:
    """
    Computes all summary flight metrics from a cleaned and merged DataFrame.

    Velocity source priority:
        1. GPS 'speed' column (most accurate, no drift).
        2. GPS velocity components 'vx', 'vy', 'vz' if available.
        3. IMU integration fallback via trapezoid_integrate (prone to drift).

    Vertical speed (when GPS speed is available but 'vz' is missing) is derived
    as the numerical derivative of altitude: v_z = |Δalt / Δt|.
    """
    df = filter_physical_limits(df)

    result = {}

    result["duration_sec"] = float(df["time"].iloc[-1] - df["time"].iloc[0])
    result["distance_m"] = total_distance(df)

    if "speed" in df.columns:
        v_horizontal = df["speed"]
        if "vz" in df.columns:
            v_vertical = df["vz"].abs()
        else:
            dt = df["time"].diff().replace(0, np.nan)
            v_vertical = df["alt"].diff().abs() / dt
            v_vertical = v_vertical.fillna(0)
    elif "vx" in df.columns and "vy" in df.columns:
        v_horizontal = np.sqrt(df["vx"] ** 2 + df["vy"] ** 2)
        v_vertical = df["vz"].abs()
    else:
        df = compute_velocity_from_imu(df)
        v_horizontal = np.sqrt(df["vx_imu"] ** 2 + df["vy_imu"] ** 2)
        v_vertical = df["vz_imu"].abs()

    result["max_horizontal_speed_ms"] = float(v_horizontal.max())
    result["max_vertical_speed_ms"] = float(v_vertical.quantile(0.99))

    accel_magnitude = np.sqrt(df["acc_x"] ** 2 + df["acc_y"] ** 2 + df["acc_z"] ** 2)
    result["max_acceleration_ms2"] = float(accel_magnitude.max())

    result["max_altitude_m"] = float(df["alt"].max())
    result["min_altitude_m"] = float(df["alt"].min())
    result["max_altitude_gain_m"] = float((df["alt"].diff().clip(lower=0)).sum())

    return result


def analyze(df) -> dict:
    """
    Main entry point for the analytics module.

    Args:
        df: DataFrame with columns time, lat, lon, alt, acc_x, acc_y, acc_z

    Returns:
        dict containing all computed flight metrics
    """
    return compute_metrics(df)
