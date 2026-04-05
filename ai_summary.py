"""Файл з функцією для генерації висновку ШІ по польоту"""

import google.generativeai as genai

genai.configure(api_key="AIzaSyCMhqC5VGc4oaJkzqZ34pNSzzd0x1qcfjQ")
model = genai.GenerativeModel('models/gemini-2.5-flash')

def generate_ai_summary(metrics, df):
    """Генерує висновок ШІ по польоту дрону"""

    prompt = f"""
    Ти аналітик польотів БПЛА.

    Ось дані польоту:
    - Тривалість: {round(metrics['duration_sec'])} сек
    - Дистанція: {round(metrics['distance_m'])} м
    - Максимальна висота: {round(metrics['max_altitude_m'])} м
    - Максимальна горизонтальна швидкість: {round(metrics['max_horizontal_speed_ms'])} м/с
    - Максимальна вертикальна швидкість: {round(metrics['max_vertical_speed_ms'])} м/с
    - Максимальне прискорення: {round(metrics['max_acceleration_ms2'])} м/с^2
    - Максимальний набір висоти: {round(metrics['max_altitude_gain_m'])} м

    Зроби короткий аналіз (3-5 речень):
    - чи стабільний політ
    - чи є аномалії
    - потенційні проблеми

    Пиши без слів 'Аналіз польоту БПЛА:' на початку, просто речення
    """

    response = model.generate_content(prompt)
    return response.text
