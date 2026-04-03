"""Web application"""

import streamlit as st
from openai import OpenAI
import numpy as np
import plotly.express as px

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

    # with st.spinner("Обробка файлу..."):
        # df = parse_log(uploaded_file)
        # metrics = compute_metrics(df)
        # fig = plot_3d(df)
        # summary = generate_summary(metrics)

    st.success("Файл оброблено")

    # Metrics
    st.header("Основні метрики")

    # col1, col2, col3, col4 = st.columns(4)

    # col1.metric("⏱️ Тривалість", f"{metrics['duration']} c")
    # col2.metric("📏 Дистанція", f"{metrics['distance']} м")
    # col3.metric("🚀 Макс. швидкість", f"{metrics['max_speed']} м/с")
    # col4.metric("🏔️ Макс. висота", f"{metrics['max_altitude']} м")

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
