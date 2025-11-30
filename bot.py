import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
import io

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Сессии пользователей
user_sessions = {}  # chat_id: {"messages": [], "mood_scores": [], "emotions": []}

# Простейший словарь эмоций для анализа текста
emotion_keywords = {
    "грусть": "😢",
    "печаль": "😢",
    "тревога": "😟",
    "страх": "😨",
    "радость": "😊",
    "счастье": "😁",
    "устал": "😴",
    "злость": "😠",
    "раздражение": "😤",
}

# Ответы на эмоции
emotion_responses = {
    "😢": "Я вижу, тебе грустно. Держись, я рядом.",
    "😟": "Тревога понятна. Попробуй глубоко вдохнуть и выдохнуть.",
    "😨": "Страхи бывают у всех. Всё будет хорошо.",
    "😊": "Радость — здорово! Продолжай в том же духе.",
    "😁": "Супер! Ты сегодня в отличном настроении.",
    "😴": "Усталость понятна. Отдохни немного.",
    "😠": "Злость — нормальная эмоция. Давай успокоимся вместе.",
    "😤": "Раздражение есть у всех. Попробуй расслабиться."
}

# ===== Функции =====

def detect_emotions(text: str):
    """Простейший анализ эмоций по ключевым словам"""
    text_lower = text.lower()
    detected = []
    for word, emoji in emotion_keywords.items():
        if word in text_lower:
            detected.append(emoji)
    return detected if detected else ["😐"]  # 😐 - нейтральное

def add_to_session(chat_id, text, detected_emotions):
    session = user_sessions.setdefault(chat_id, {"messages": [], "mood_scores": [], "emotions": []})
    session["messages"].append(text)
    # Для простоты настроение = количество положительных - количество отрицательных
    mood_score = sum([1 if e in ["😊", "😁"] else -1 if e in ["😢", "😟", "😨", "😠", "😤"] else 0 for e in detected_emotions])
    session["mood_scores"].append(mood_score)
    session["emotions"].extend(detected_emotions)

# ===== Команды =====
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я Night Word. Расскажи, как твои дела, и я постараюсь помочь и поддержать.")

@dp.message_handler(commands=['stats'])
async def cmd_stats(message: types.Message):
    session = user_sessions.get(message.chat.id)
    if not session:
        await message.reply("Пока нет статистики. Попробуй написать что-то, и я буду отслеживать твои эмоции.")
        return
    # График настроения
    fig, ax = plt.subplots()
    ax.plot(range(1, len(session["mood_scores"])+1), session["mood_scores"], marker='o', color='blue')
    ax.set_title("Динамика настроения")
    ax.set_xlabel("Сообщения")
    ax.set_ylabel("Оценка настроения")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await bot.send_photo(message.chat.id, buf)
    buf.close()
    # Текстовая статистика
    total_msgs = len(session["messages"])
    emotions_count = {e: session["emotions"].count(e) for e in set(session["emotions"])}
    emotions_text = "\n".join([f"{e}: {count}" for e, count in emotions_count.items()])
    await message.reply(f"Всего сообщений: {total_msgs}\nЭмоции:\n{emotions_text}")

# ===== Основной обработчик сообщений =====
@dp.message_handler()
async def handle_message(message: types.Message):
    detected = detect_emotions(message.text)
    add_to_session(message.chat.id, message.text, detected)
    # Отвечаем на эмоции
    responses = [emotion_responses[e] for e in detected if e in emotion_responses]
    await message.reply("\n".join(responses))

# ===== Автосоветы =====
async def daily_tip_sender():
    await bot.wait_until_ready()
    tz = pytz.timezone('Europe/Kiev')
    daily_tips = [
        "Сделай короткую прогулку на свежем воздухе.",
        "Попробуй 5 минут медитации.",
        "Запиши 3 вещи, за которые благодарен сегодня.",
        "Дыхательное упражнение: вдох 4 сек, выдох 6 сек.",
    ]
    while True:
        now = datetime.now(tz)
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        for chat_id in user_sessions.keys():
            await bot.send_message(chat_id, f"Доброе утро! Совет дня: {random.choice(daily_tips)}")

# ===== Запуск бота =====
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(daily_tip_sender())
    executor.start_polling(dp, skip_updates=True)
