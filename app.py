"""Web application"""

import streamlit as st
from openai import OpenAI
import numpy as np
import plotly.express as px
from analytics import analyze
from parse import parse_log

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def detect_events(df):
    """Detects if there was any events during flight """
    events = []

    if df["alt"].diff().min() < -20:
        events.append("Різке падіння висоти")

    if df["speed"].max() > 25:
        events.append("Перевищення швидкості")

    return events

def generate_ai_summary(metrics, df):
    """Generates AI summary of drone's flight"""
    prompt = f"""
    Ти аналітик польотів БПЛА.

    Ось дані польоту:
    - Тривалість: {metrics['duration']} сек
    - Дистанція: {metrics['distance']} м
    - Макс швидкість: {metrics['max_speed']} м/с
    - Макс висота: {metrics['max_altitude']} м

    Зроби короткий аналіз (3-5 речень):
    - чи стабільний політ
    - чи є аномалії
    - потенційні проблеми
    """

    events = detect_events(df)

    prompt += f"\nАномалії: {",".join(events)}"

    completion = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content

# UI

st.title("Analysis Dashboard")
st.markdown("Made by: coockie team 🍪")

uploaded_file = st.file_uploader("Завантажте лог-файл", type=["bin"])

if uploaded_file:

    with st.spinner("Обробка файлу..."):
        df = parse_log(uploaded_file)
        metrics = analyze(df)
        # st.write(str(metrics))
        # fig = plot_3d(df)
        # summary = generate_summary(metrics)

    st.success("Файл оброблено")

    # Metrics
    st.header("Основні метрики")

    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)
    col6, col7 = st.columns(2)

    col1.metric("Тривалість", f"{round(metrics['duration_sec'])} c")
    col2.metric("Дистанція", f"{round(metrics['distance_m'])} м")
    col3.metric("Макс. висота", f"{round(metrics['max_altitude_m'])} м")

    col4.metric("Макс. горизонтальна швидкість", f"{round(metrics['max_horizontal_speed_ms'])} м/с")
    col5.metric("Макс. вертикальна швидкість", f"{round(metrics['max_vertical_speed_ms'])} м/с")

    col6.metric("Макс. прискорення", f"{round(metrics['max_acceleration_ms2'])} м/c^2")
    col7.metric("Макс. набір висоти", f"{round(metrics['max_altitude_gain_m'])} м")

    # Visualisation
    st.header("Траєкторія польоту")
    with st.spinner("Візуалізація..."):
        # Дані
        np.random.seed(42)
        n_points = 100
        x = np.random.rand(n_points)
        y = np.random.rand(n_points)
        z = np.random.rand(n_points)

        # 3D графік
        fig = px.scatter_3d(
            x=x,
            y=y,
            z=z,
            title="3D Flight Path",
        )

        fig.update_layout(height=800)

        # 🔥 Вивід у Streamlit
        st.plotly_chart(fig, use_container_width=True)

    # st.plotly_chart(fig, use_container_width=True)

    # AI summary

    st.header("Аналіз польоту")
    # with st.spinner("AI аналізує політ..."):
    #     summary = generate_ai_summary(metrics,df)
    # st.info(summary)
else:
    st.info("Завантажте файл, щоб почати аналіз")
