import asyncio
import logging
import random
from datetime import datetime, timedelta
import sys

TOKEN = "8568717574:AAEFMhqvccnZ6u0Go_BDyppSK0Ph9Maraho"
GROUP_ID = 8580261363

logging.basicConfig(level=logging.INFO)
print(f"✅ BOT START: GROUP_ID={GROUP_ID}")

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_captchas = {}

@router.message(Command("test_admin"))
async def test_admin(message: Message):
    print(f"🧪 /test_admin от {message.from_user.id}")
    try:
        me = await bot.get_me()
        bot_info = await bot.get_chat_member(GROUP_ID, me.id)
        status = bot_info.status
        can_invite_users = getattr(bot_info, 'can_invite_users', False)
        
        await message.answer(
            f"🔍 ПРОВЕРКА ПРАВ:\n\n"
            f"👤 @{me.username}\n"
            f"📊 Статус: {status}\n"
            f"🔗 Приглашения: {'✅ ДА' if can_invite_users else '❌ НЕТ'}\n"
            f"🆔 Группа: {GROUP_ID}\n\n"
            f"{'🎉 ОК!' if status in ['administrator', 'creator'] and can_invite_users else '❌ Нужны права!'}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

@router.message(CommandStart(), Command("start"))
async def start_captcha(message: Message):
    print(f"✅ /start от {message.from_user.id}")
    a, b = random.randint(1, 20), random.randint(1, 20)
    answer = a + b
    
    user_captchas[message.from_user.id] = {
        "answer": answer, 
        "time": datetime.now()
    }
    
    await message.answer(f"🔐 Капча:\n\n<code>{a} + {b} = ?</code>")

@router.message(F.text & ~F.text.startswith("/"))
async def check_captcha(message: Message):
    print(f"💭 Ответ: '{message.text}' от {message.from_user.id}")
    
    user_id = message.from_user.id
    if user_id not in user_captchas:
        await message.answer("❌ Сначала /start!")
        return
    
    captcha = user_captchas[user_id]
    if (datetime.now() - captcha["time"]).seconds > 300:
        del user_captchas[user_id]
        await message.answer("⏰ Время вышло! /start")
        return
    
    try:
        user_answer = int(message.text.strip())
        if user_answer == captcha["answer"]:
            expire_date = int((datetime.now() + timedelta(minutes=5)).timestamp())
            link_data = await bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                name=f"captcha_{user_id}",
                expire_date=expire_date,
                member_limit=1
            )
            await message.answer(
                f"🎉 УСПЕХ!\n\n"
                f"🔗 <code>{link_data.invite_link}</code>\n\n"
                f"⏰ 5 мин • 1 чел."
            )
            del user_captchas[user_id]
            print(f"✅ Ссылка выдана {user_id}")
        else:
            await message.answer("❌ Неверно!")
    except ValueError:
        await message.answer("❌ Только число!")
    except Exception as e:
        await message.answer("❌ Ошибка ссылки. Проверьте /test_admin")
        print(f"❌ Ошибка: {e}")

async def main():
    print("🎯 Бот запущен! Тестируйте: /test_admin")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
