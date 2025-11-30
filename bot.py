import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMIN_ID
from database import init_db, append_value, get_user_stats

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

active_chats = {}

def get_support_phrase():
    try:
        with open("data/support_phrases.txt", "r", encoding="utf-8") as f:
            return random.choice(f.readlines()).strip()
    except:
        return "Ты не один. Всё будет хорошо."

end_chat_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Завершить общение ❌", callback_data="end_chat")]
    ]
)

rate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"rate_{i}") for i in range(1,6)]
    ]
)

# ------------------------ Команды ------------------------

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🌙 Добро пожаловать в Night Word!\n"
        "Тихое пространство для мыслей, поддержки и историй.\n\n"
        "Введи /help чтобы узнать все возможности."
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "/help — описание всех функций\n"
        "/about — о проекте\n"
        "/thought — случайная мысль\n"
        "/quote — поддерживающая фраза\n"
        "/my_story — отправить свою историю\n"
        "/feel — оценка состояния\n"
        "/feedback — оставить отзыв\n"
        "/support — связь с поддержкой\n"
        "/human_support — общение с живым человеком\n"
        "/ai — AI-компаньон (в разработке)\n"
        "/ai_support — AI-поддержка (в разработке)"
    )

@dp.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer(
        "🌘 Night Word — пространство, где каждый может поделиться собой.\n"
        "Мы создаём место для историй, поддержки и безопасного общения."
    )

@dp.message(Command("thought"))
async def thought_cmd(message: types.Message):
    await message.answer("💭 Мысль дня:\n" + get_support_phrase())

@dp.message(Command("quote"))
async def quote_cmd(message: types.Message):
    await message.answer("✨ " + get_support_phrase())

@dp.message(Command("my_story"))
async def story_cmd(message: types.Message):
    await message.answer(
        "📝 Отправь свою историю одним сообщением.\n"
        "Мы сохраним её в тишине Night Word."
    )

@dp.message(Command("feel"))
async def feel_cmd(message: types.Message):
    await message.answer("Как ты себя чувствуешь от 1 до 10?")

@dp.message(Command("feedback"))
async def feedback_cmd(message: types.Message):
    await message.answer("✍ Напиши свой отзыв. Он важен.")

@dp.message(Command("support"))
async def support_cmd(message: types.Message):
    await message.answer("Связь с поддержкой: @your_support_username")

@dp.message(Command("ai"))
async def ai_cmd(message: types.Message):
    await message.answer("🤖 AI-компаньон пока находится в разработке.")

@dp.message(Command("ai_support"))
async def ai_s_cmd(message: types.Message):
    await message.answer("🤖 AI-поддержка скоро появится.")

@dp.message(Command("human_support"))
async def human_support(message: types.Message):
    user_id = message.from_user.id
    active_chats[user_id] = ADMIN_ID
    await message.answer(
        "🔗 Ты подключён к живому человеку.\n"
        "Можешь писать. Я передам сообщение оператору.",
        reply_markup=end_chat_kb,
    )
    await bot.send_message(ADMIN_ID, f"🟢 Новый диалог с пользователем {user_id}.")

@dp.message()
async def relay_messages(message: types.Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        await bot.send_message(ADMIN_ID, f"Сообщение от {user_id}:\n{message.text}")
        return
    if user_id == ADMIN_ID and message.reply_to_message:
        text = message.text
        try:
            reply_user = int(message.reply_to_message.text.split()[3])
            await bot.send_message(reply_user, "💬 Ответ оператора:\n" + text)
        except:
            pass

@dp.callback_query(lambda c: c.data == "end_chat")
async def end_chat(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id in active_chats:
        del active_chats[user_id]
    await call.message.answer("❌ Общение завершено.\nПоставьте оценку:", reply_markup=rate_kb)
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("rate_"))
async def rating(call: types.CallbackQuery):
    user_id = call.from_user.id
    rating = call.data.split("_")[1]
    append_value(user_id, "ratings", rating)
    await call.message.answer("Спасибо! Напиши отзыв:")
    await call.answer()

# ------------------------ Старт бота ------------------------

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
