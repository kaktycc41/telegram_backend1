import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from telethon import TelegramClient

from auto_nick import auto_change_nick

# --- Telegram API ma’lumotlari ---
API_ID = 27877995
API_HASH = "f69a4c454706d10fea9f0e99cc91b353"
SESSION_NAME = "user_session"
API_TOKEN = "7590353937:AAFpDqPYb5HtWiVyQIDV1B8TLp8Abvc-L0E"

# --- Client va Bot yaratamiz ---
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}

# === Commands ===
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌀 Nikni avtomatik o‘zgartirish")],
            [KeyboardButton(text="💬 Kanal kommentariyasiga yozish")],
        ],
        resize_keyboard=True
    )
    await message.answer("👋 Xush kelibsiz!\nXizmatni tanlang:", reply_markup=keyboard)

# === Nik o‘zgartirish ===
@dp.message(lambda msg: msg.text == "🌀 Nikni avtomatik o‘zgartirish")
async def set_nick_timer(message: Message):
    await message.answer("⏱ Nik har necha daqiqada o‘zgarishini kiriting (masalan: 30):")
    user_data[message.from_user.id] = {"step": "set_interval"}

@dp.message(lambda msg: msg.text.isdigit())
async def set_nicknames(message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get("step") == "set_interval":
        interval = int(message.text)
        user_data[user_id] = {"interval": interval, "step": "set_nicknames"}
        await message.answer("💬 Endi niklarni yuboring, har birini yangi qatordan yozing:")
    elif user_id in user_data and user_data[user_id].get("step") == "set_nicknames":
        nicknames = message.text.split("\n")
        interval = user_data[user_id]["interval"]
        await message.answer(f"✅ {len(nicknames)} ta nik qabul qilindi.\nHar {interval} daqiqada o‘zgaradi.")
        asyncio.create_task(auto_change_nick(nicknames, interval))

# === HTTP server (Render uchun zarur) ===
async def handle(request):
    return web.Response(text="✅ Bot is running!")

async def run_http_server():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# === Botni ishga tushirish ===
async def main():
    await client.start()
    await run_http_server()  # 🔹 Render uchun kerak
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
