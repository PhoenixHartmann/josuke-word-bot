import os
import logging
import asyncio
from dotenv import load_dotenv
load_dotenv()
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile

# ✅ Загружаем токен из переменной окружения
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN не задан в переменных окружения")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

FORBIDDEN_WORDS = ["хуй", "пример", "плохое_слово3"]

async def check_forbidden_words(message: types.Message) -> None:
    if not message.text:
        return

    text_lower = message.text.lower()
    if any(word in text_lower for word in FORBIDDEN_WORDS):
        try:
            await message.delete()
            warn_gif = FSInputFile("josuke_angry.gif")
            warn = await message.answer_animation(
                warn_gif, caption="Пред\nЧто ты сказал про мою прическу?"
            )
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

# HTTP endpoint
async def index(_: web.Request) -> web.Response:
    return web.Response(text="Бот работает ✅")

async def start_http_server() -> None:
    app = web.Application()
    app.router.add_get("/", index)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))  # Render задаёт PORT
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logging.info("🌐  HTTP server started on port %d", port)

async def main() -> None:
    await asyncio.gather(
        start_http_server(),
        dp.start_polling(bot),
    )

if __name__ == "__main__":
    asyncio.run(main())