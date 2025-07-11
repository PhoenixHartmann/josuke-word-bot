import os
import logging
import asyncio
from dotenv import load_dotenv
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile

# ✅ Загружаем переменные окружения
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN не задан в переменных окружения")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

FORBIDDEN_WORDS = ["хуй", "пример", "плохое_слово3"]

# Проверка и удаление сообщений с запрещёнными словами
async def check_forbidden_words(message: types.Message) -> None:
    if not message.text:
        return

    text_lower = message.text.lower()
    if any(word in text_lower for word in FORBIDDEN_WORDS):
        try:
            await message.delete()
            warn_gif = FSInputFile("josuke_angry.git add main.pygif")
            target = message.from_user
            username = f"@{target.username}" if target.username else target.full_name
            warn = await message.answer_animation(
                 warn_gif, caption=f"Пред"
            )
            await message.reply("Предупреждение")
            await asyncio.sleep(10)
            await warn.delete()
        except Exception as e:
            if "retry after" in str(e).lower():
                retry = int(str(e).split("retry after")[1].split()[0])
                await asyncio.sleep(retry)
            else:
                logging.error("⚠️ %s", e)

@dp.message()
async def on_new_msg(message: types.Message) -> None:
    await check_forbidden_words(message)

@dp.edited_message()
async def on_edit_msg(message: types.Message) -> None:
    await check_forbidden_words(message)

# HTTP‑сервер для Render
async def index(_: web.Request) -> web.Response:
    return web.Response(text="Бот работает ✅")

async def start_http_server() -> None:
    app = web.Application()
    app.router.add_get("/", index)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logging.info("🌐 HTTP server started on port %d", port)

# 🔄 Пинг на свой URL, чтобы не засыпал Render
async def ping_self():
    url = os.getenv("PING_URL") or "http://localhost:10000"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    logging.info(f"🔄 Пинг на {url} → статус {resp.status}")
        except Exception as e:
            logging.warning(f"⚠️ Ошибка пинга: {e}")
        await asyncio.sleep(600)  # каждые 10 минут

# Главная асинхронная точка входа
async def main() -> None:
    await asyncio.gather(
        start_http_server(),
        dp.start_polling(bot),
        ping_self(),
    )

if __name__ == "__main__":
    asyncio.run(main())