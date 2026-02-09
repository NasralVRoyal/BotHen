import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

TOKEN = "8568717574:AAEFMhqvccnZ6u0Go_BDyppSK0Ph9Maraho"
GROUP_ID = 8580261363

print("🚀 Бот стартует...")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

@router.message(Command("test_admin"))
async def test_admin(message: Message):
    print(f"🧪 КОМАНДА /test_admin ОТ {message.from_user.id}")
    await message.answer("✅ /test_admin РАБОТАЕТ!")

@router.message(Command("start"))
async def start_cmd(message: Message):
    print(f"✅ /start ОТ {message.from_user.id}")
    await message.answer("🔐 Капча: 3 + 4 = ?")

@router.message()
async def any_message(message: Message):
    print(f"📨 ЛЮБОЕ сообщение: '{message.text}' от {message.from_user.id}")
    await message.answer("👋 Получил сообщение!")

async def main():
    print("🎯 ПОЛЛИНГ СТАРТУЕТ...")
    me = await bot.get_me()
    print(f"🤖 Бот: @{me.username} ID: {me.id}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
