import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
import sys

# Настройки ЛОГГИРОВАНИЯ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ВАШИ ДАННЫЕ (уже подставлены!)
TOKEN = "8568717574:AAEFMhqvccnZ6u0Go_BDyppSK0Ph9Maraho"
GROUP_ID = "8580261363"

# Проверка
if not TOKEN:
    print("❌ ОШИБКА: TOKEN не установлен!")
    sys.exit(1)

try:
    GROUP_ID = int(GROUP_ID)
    print(f"✅ BOT START: TOKEN=OK, GROUP_ID={GROUP_ID}")
except ValueError:
    print(f"❌ ОШИБКА: GROUP_ID должен быть числом!")
    sys.exit(1)

# Хранилище капч пользователей
user_captchas = {}

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

@router.message(CommandStart())
async def start_captcha(message: Message):
    """Генерация капчи"""
    a, b = random.randint(1, 20), random.randint(1, 20)
    answer = a + b
    task = f"🔐 Капча для вступления в группу:\n\n{a} + {b} = ?"
    
    user_captchas[message.from_user.id] = {
        "answer": answer, 
        "time": datetime.now()
    }
    
    await message.answer(task)
    print(f"Капча для {message.from_user.id}: {answer}")

@router.message(F.text)
async def check_captcha(message: Message):
    """Проверка капчи"""
    user_id = message.from_user.id
    
    if user_id not in user_captchas:
        await message.answer("❌ Сначала выполните /start!")
        return
    
    captcha = user_captchas[user_id]
    
    # Таймаут 5 минут
    if (datetime.now() - captcha["time"]).seconds > 300:
        del user_captchas[user_id]
        await message.answer("⏰ Время истекло! Используйте /start")
        return
    
    # Проверка ответа
    if message.text.strip().isdigit():
        user_answer = int(message.text)
        
        if user_answer == captcha["answer"]:
            try:
                # Создание временной ссылки
                expire_date = int((datetime.now() + timedelta(minutes=5)).timestamp())
                
                link_data = await bot.create_chat_invite_link(
                    chat_id=GROUP_ID,
                    name=f"captcha_{user_id}",
                    expire_date=expire_date,
                    member_limit=1
                )
                
                await message.answer(
                    f"🎉 Капча пройдена успешно!\n\n"
                    f"🔗 <b>Временная ссылка:</b>\n"
                    f"<code>{link_data.invite_link}</code>\n\n"
                    f"⏰ Действует: 5 минут\n"
                    f"👤 1 использование"
                )
                print(f"✅ Ссылка выдана пользователю {user_id}")
                
            except Exception as e:
                await message.answer("❌ Ошибка создания ссылки. Убедитесь, что бот - админ в группе.")
                print(f"❌ Ошибка API: {e}")
            finally:
                del user_captchas[user_id]
    else:
        await message.answer("❌ Введите только число!")

async def main():
    """Запуск бота"""
    print("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен")
