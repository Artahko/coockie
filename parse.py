import tempfile
import pandas as pd
from pymavlink import mavutil

def parse_log(uploaded_file):
    """Парсить файл і видає інформацію для аналітики"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    log = mavutil.mavlink_connection(
        tmp_path,
        dialect="ardupilotmega"
    )

    gps_data = []
    imu_data = []
    att_data = []

    while True:
        msg = log.recv_match(blocking=False)
        if msg is None:
            break

        msg_type = msg.get_type()

        # GPS
        if msg_type == "GPS":
            gps_data.append({
                "time": msg.TimeUS,
                "lat": msg.Lat,
                "lon": msg.Lng,
                "alt": msg.Alt,
                "speed": getattr(msg, "Spd", None)
            })

        # IMU
        elif msg_type == "IMU":
            imu_data.append({
                "time": msg.TimeUS,
                "acc_x": msg.AccX,
                "acc_y": msg.AccY,
                "acc_z": msg.AccZ
            })

        # ATT
        elif msg_type == "ATT":
            att_data.append({
                "time": msg.TimeUS,
                "roll": msg.Roll,
                "pitch": msg.Pitch,
                "yaw": msg.Yaw
            })

    gps_df = pd.DataFrame(gps_data)
    imu_df = pd.DataFrame(imu_data)
    att_df = pd.DataFrame(att_data)

    df = gps_df.copy()

    if not imu_df.empty:
        df = pd.merge_asof(df.sort_values("time"),
                           imu_df.sort_values("time"),
                           on="time")

    if not att_df.empty:
        df = pd.merge_asof(df.sort_values("time"),
                           att_df.sort_values("time"),
                           on="time")

    return df
