"""Web застосунок"""

import streamlit as st

from parse import parse_log
from analytics import analyze
from visualization import plot_flight
from ai_summary import generate_ai_summary

# UI
st.set_page_config(layout="wide")
st.title("Analysis Dashboard")
st.markdown("Made by: coockie team 🍪")

uploaded_file = st.file_uploader("Завантажте лог-файл", type=["bin"])

if uploaded_file:

    with st.spinner("Обробка файлу..."):
        df = parse_log(uploaded_file)
        metrics = analyze(df)
        fig = plot_flight(df)
        try:
            summary = generate_ai_summary(metrics)
        except:
            summary = "ШІ висновку не було згенеровано"

    st.success("Файл оброблено")

    # Метрики
    st.header("Основні метрики")

    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7 = st.columns(3)

    col1.metric("Тривалість", f"{round(metrics['duration_sec'])} c")
    col2.metric("Дистанція", f"{round(metrics['distance_m'])} м")
    col3.metric("Макс. висота", f"{round(metrics['max_altitude_m'])} м")
    col4.metric("Макс. горизонтальна швидкість", f"{round(metrics['max_horizontal_speed_ms'])} м/с")

    col5.metric("Макс. вертикальна швидкість", f"{round(metrics['max_vertical_speed_ms'])} м/с")
    col6.metric("Макс. прискорення", f"{round(metrics['max_acceleration_ms2'])} м/c^2")
    col7.metric("Макс. набір висоти", f"{round(metrics['max_altitude_gain_m'])} м")

    # Візуалізація
    st.header("Траєкторія польоту")
    st.write('Натисніть кнопку "Візуалізувати", щоб запустити анімацію.')
    st.write('Перші кілька секунд дрон може лишатися на місці.')
    st.write('Після завершення анімації графік можна масштабувати та обертати.')

    with st.spinner("Візуалізація..."):
        fig.update_layout(height=900, width=1000)
        st.plotly_chart(fig, use_container_width=True)

    # ШІ висновок
    st.header("Аналіз польоту")
    st.info(summary)

else:
    st.info("Завантажте файл, щоб почати аналіз")
