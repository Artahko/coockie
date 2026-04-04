import pandas as pd
import numpy as np
import pymap3d as pm
import plotly.graph_objects as go

# Дані

df = pd.read_csv("your_data.csv")
# df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
# df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
# df["alt"] = pd.to_numeric(df["alt"], errors="coerce")
# df["speed"] = pd.to_numeric(df["speed"], errors="coerce")
# df["time"] = pd.to_numeric(df["time"], errors="coerce")

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
                    colorbar=dict(title="Speed (m/s)")
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
            # ),
            # go.Scatter3d(
            #     x=[df["x"][i-1]],
            #     y=[df["y"][i-1]],
            #     z=[df["z"][i-1]],
            #     mode='markers',
            #     marker=dict(
            #         size=8,
            #         color=df["speed"][i-1],
            #         colorscale='Turbo',
            #         cmin=df["speed"].min(),
            #         cmax=df["speed"].max(),
            #         showscale=False
            #     ),
            #     customdata=[[df["speed"][i-1], df["time_sec"][i-1]]],
            #     hovertemplate=
            #     "CURRENT POINT<br>" +
            #     "Speed: %{customdata[0]:.2f} m/s<br>" +
                # "Time: %{customdata[1]} s<extra></extra>"
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
    title="Drone Flight",
    scene=dict(
        # uirevision='constant',
        xaxis=dict(title='East відносно старту (м)', range=x_range),
        yaxis=dict(title='North відносно старту (м)', range=y_range),
        zaxis=dict(title='Висота відносно старту (м)', range=z_range),
    ),
    updatemenus=[{
        "type": "buttons",
        "buttons": [{
            "label": "▶ Play",
            "method": "animate",
            "args": [None, {
                "frame": {"duration": 100, "redraw": True},
                "fromcurrent": True
            }]
        }]
    }]
)

fig.show()
