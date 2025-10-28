import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from telethon import TelegramClient

# agar auto_nick.py yangi signature bilan turgan bo'lsa import qilamiz
from auto_nick import auto_change_nick  # bu funksiya clientni qabul qiladi

# --- Telegram API ma’lumotlari ---
API_ID = 27877995
API_HASH = "f69a4c454706d10fea9f0e99cc91b353"
SESSION_NAME = "user_session"   # e'tibor: .session kengaytmasiz
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
    # agar foydalanuvchi interval kiritgan bo'lsa keyingi bosqichga o'tamiz
    if user_id in user_data and user_data[user_id].get("step") == "set_interval":
        interval = int(message.text)
        user_data[user_id] = {"interval": interval, "step": "set_nicknames"}
        await message.answer("💬 Endi niklarni yuboring, har birini yangi qatordan yozing:")
        return

    # agar foydalanuvchi niklarni yuborgan bo'lsa:
    if user_id in user_data and user_data[user_id].get("step") == "set_nicknames":
        nicknames = message.text.split("\n")
        interval = user_data[user_id]["interval"]
        await message.answer(f"✅ {len(nicknames)} ta nik qabul qilindi.\nHar {interval} daqiqada o‘zgaradi.")
        # auto_change_nick funktsiyasiga clientni beramiz (shunda input so'ralmaydi)
        asyncio.create_task(auto_change_nick(client, nicknames, interval))

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
    # 1) Telethon sessiyasini 'connect' orqali bog'laymiz (bu input() so'ramaydi)
    await client.connect()
    if not await client.is_user_authorized():
        # Agar sessiya authorized bo'lmasa, bu holatda server sessiyani yaratolmaydi.
        # Siz bu xabarni logda ko'rasiz — lokal mashinada sessiyani yaratish kerak.
        print("⚠️ E'tibor: Telethon sessiyasi authorizatsiyadan o'tmagan. "
              "Avval lokalda sessiyani yaratib (user_session.session) GitHub/Renderga qo'ying.")
        # Botga davom etamiz — faqat aiogram ishlaydi (nik o'zgartirish boshlanmaydi)
    else:
        print("✅ Telethon sessiyasi ulandi (user_session).")

    # 2) HTTP server (Render uchun) va keyin aiogram polling
    await run_http_server()
    try:
        print("🔁 Bot polling boshlandi...")
        await dp.start_polling(bot)
    except Exception as e:
        print("Bot ishlashida xato:", e)
    finally:
        # Bot to'xtaganda Telethonni uzamiz
        await client.disconnect()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
