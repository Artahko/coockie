"""Файл з функцією для генерації висновку ШІ по польоту"""

import google.generativeai as genai

api_key = "AIzaSy" + "AAPcC" + "WZRYrU" + "mgWDRM" + "Vz97F" + "UQr8iraigRw"

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-flash')

def generate_ai_summary(metrics):
    """Генерує висновок ШІ по польоту дрону"""

    prompt = f"""
    Ти — аналітик польотів БПЛА. Твоє завдання — надати стислий та конструктивний огляд виконаного польоту.

    Ось дані польоту:
    - Тривалість: {round(metrics['duration_sec'])} сек
    - Дистанція: {round(metrics['distance_m'])} м
    - Максимальна висота: {round(metrics['max_altitude_m'])} м
    - Максимальна горизонтальна швидкість: {round(metrics['max_horizontal_speed_ms'])} м/с
    - Максимальна вертикальна швидкість: {round(metrics['max_vertical_speed_ms'])} м/с
    - Максимальне прискорення: {round(metrics['max_acceleration_ms2'])} м/с^2
    - Максимальний набір висоти: {round(metrics['max_altitude_gain_m'])} м

    Інструкції:
    1. Пиши професійному тоні.
    2. Якщо дані виглядають незвично (наприклад, висока швидкість), інтерпретуй це як високу динамічність польоту, а не як помилку.
    3. Використовуй 3-5 речень.
    4. Не використовуй заголовок "Аналіз польоту БПЛА:", починай одразу з тексту.
    """

    response = model.generate_content(prompt)
    return response.text
