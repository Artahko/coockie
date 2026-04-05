"""Файл з функцією для візуалізації"""

import numpy as np
import pymap3d as pm
import plotly.graph_objects as go

def plot_flight(df):
    """Повертає графік для візуалізації"""
    df["time_sec"] = df["time_sec"] * 10e5
    df["time_sec"].round()

    # ENU
    lat0, lon0, alt0 = df["lat"].iloc[0], df["lon"].iloc[0], df["alt"].iloc[0]

    x, y, z = pm.geodetic2enu(
        df["lat"], df["lon"], df["alt"],
        lat0, lon0, alt0
    )

    df["x"], df["y"], df["z"] = x, y, z

    x_range = [df["x"].min() - 10, df["x"].max() + 10]
    y_range = [df["y"].min() - 10, df["y"].max() + 10]
    z_range = [df["z"].min() - 10, df["z"].max() + 10]

    # Frames
    frames = []

    for i in range(1, len(df)+1):
        frames.append(go.Frame(
            data=[
                go.Scatter3d(
                    x=df["x"][:i],
                    y=df["y"][:i],
                    z=df["z"][:i],
                    mode='lines+markers',
                    marker=dict(
                        size=4,
                        color=df["speed"][:i],
                        colorscale='Turbo',
                        cmin=df["speed"].min(),
                        cmax=df["speed"].max(),
                        colorbar=dict(title="Швидкість (м/с)")
                    ),
                    customdata=np.stack([
                        df["speed"][:i],
                        df["time_sec"][:i],
                        df["lat"][:i],
                        df["lon"][:i],
                        df["alt"][:i],
                    ], axis=-1),
                    hovertemplate=
                    "Speed: %{customdata[0]:.2f} m/s<br>" +
                    "Time: %{customdata[1]:.2f} s<br>" +
                    "Lat: %{customdata[2]:.6f}<br>" +
                    "Lon: %{customdata[3]:.6f}<br>" +
                    "Alt: %{customdata[4]:.1f} m<extra></extra>"
                )
            ],
            name=str(i)
        ))

    # Figure
    fig = go.Figure(
        data=[
            go.Scatter3d()
        ],
        frames=frames
    )

    fig.update_layout(
        title="Політ дрону",
        scene=dict(
            # uirevision='constant',
            xaxis=dict(title='Схід відносно старту (м)', range=x_range),
            yaxis=dict(title='Північ відносно старту (м)', range=y_range),
            zaxis=dict(title='Висота відносно старту (м)', range=z_range),
        ),
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "Візуалізувати",
                "method": "animate",
                "args": [None, {
                    "frame": {"duration": 100, "redraw": True},
                    "fromcurrent": True
                }]
            }]
        }]
    )

    return fig
