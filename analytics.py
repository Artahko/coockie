import numpy as np
from math import radians, sin, cos, sqrt, atan2


EARTH_RADIUS_M = 6_371_000


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns distance between two GPS points in meters."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(a), sqrt(1 - a))


def total_distance(df) -> float:
    """Returns total distance traveled in meters along the GPS track."""
    lats = df["lat"].values
    lons = df["lon"].values
    return sum(
        haversine(lats[i], lons[i], lats[i + 1], lons[i + 1])
        for i in range(len(lats) - 1)
    )


def trapezoid_integrate(values: np.ndarray, times: np.ndarray) -> np.ndarray:
    """
    Numerically integrates values over time using the trapezoidal method.

    Args:
        values: array of measurements (e.g. acceleration along one axis)
        times:  corresponding timestamps in seconds

    Returns:
        array of accumulated values (e.g. velocity)
    """
    result = np.zeros(len(values))
    for i in range(1, len(values)):
        dt = times[i] - times[i - 1]
        result[i] = result[i - 1] + (values[i - 1] + values[i]) / 2 * dt
    return result


def compute_velocity_from_imu(df):
    """
    Integrates IMU accelerations to produce velocity components.
    Adds columns vx_imu, vy_imu, vz_imu to the DataFrame.
    """
    t = df["time"].values
    df = df.copy()
    df["vx_imu"] = trapezoid_integrate(df["acc_x"].values, t)
    df["vy_imu"] = trapezoid_integrate(df["acc_y"].values, t)
    df["vz_imu"] = trapezoid_integrate(df["acc_z"].values, t)
    return df


def compute_metrics(df) -> dict:
    """
    Computes all flight metrics from a cleaned DataFrame.

    Uses GPS-derived speed if available, otherwise falls back to IMU integration.
    """
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
    result["max_vertical_speed_ms"] = float(v_vertical.max())

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
