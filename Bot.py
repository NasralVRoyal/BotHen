import asyncio
import logging
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router

TOKEN = "8568717574:AAEFMhqvccnZ6u0Go_BDyppSK0Ph9Maraho"
GROUP_ID = 8580261363

logging.basicConfig(level=logging.INFO)
print("🚀 КАПЧА-БОТ СТАРТУЕТ...")

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
            f"🔍 <b>СТАТУС ПРАВ:</b>\n\n"
            f"👤 @{me.username}\n"
            f"📊 Статус: {status}\n"
            f"🔗 Приглашения: {'✅ ДА' if can_invite_users else '❌ НЕТ'}\n"
            f"🆔 Группа: {GROUP_ID}"
        )
        print(f"✅ Права: {status}, приглашения: {can_invite_users}")
    except Exception as e:
        await message.answer(f"❌ Ошибка проверки: {str(e)}")

@router.message(CommandStart(), Command("start"))
async def start_captcha(message: Message):
    print(f"✅ /start от {message.from_user.id}")
    a, b = random.randint(1, 20), random.randint(1, 20)
    answer = a + b
    
    user_captchas[message.from_user.id] = {
        "answer": answer, 
        "time": datetime.now()
    }
    
    await message.answer(
        f"🔐 <b>КАПЧА ДЛЯ ГРУППЫ</b>\n\n"
        f"<code>{a} + {b} = ?</code>\n\n"
        f"⏰ 5 минут на ответ"
    )
    print(f"🔢 Капча {message.from_user.id}: {a}+{b}={answer}")

@router.message(F.text & ~F.text.startswith("/"))
async def check_captcha(message: Message):
    print(f"💭 Ответ '{message.text}' от {message.from_user.id}")
    
    user_id = message.from_user.id
    if user_id not in user_captchas:
        await message.answer("❌ Сначала /start!")
        return
    
    captcha = user_captchas[user_id]
    
    # Таймаут 5 минут
    if (datetime.now() - captcha["time"]).seconds > 300:
        del user_captchas[user_id]
        await message.answer("⏰ Время истекло! /start")
        return
    
    try:
        user_answer = int(message.text.strip())
        
        if user_answer == captcha["answer"]:
            print(f"🎉 КАПЧА ПРОЙДЕНА {user_id}")
            
            # Создаём временную ссылку
            expire_date = int((datetime.now() + timedelta(minutes=5)).timestamp())
            link_data = await bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                name=f"captcha_{user_id}",
                expire_date=expire_date,
                member_limit=1
            )
            
            await message.answer(
                f"🎉 <b>КАПЧА ПРОЙДЕНА!</b>\n\n"
                f"🔗 <b>ВРЕМЕННАЯ ССЫЛКА:</b>\n"
                f"<code>{link_data.invite_link}</code>\n\n"
                f"⏰ <b>5 минут • 1 использование</b>"
            )
            del user_captchas[user_id]
            
        else:
            await message.answer("❌ Неверный ответ! Попробуйте ещё.")
            print(f"❌ {user_answer} != {captcha['answer']}")
            
    except ValueError:
        await message.answer("❌ Введите ЧИСЛО!")
    except Exception as e:
        await message.answer("❌ Ошибка создания ссылки.\n🔧 Проверьте /test_admin")
        print(f"❌ Ошибка ссылки: {e}")

async def main():
    print("🎯 БОТ ГОТОВ! Тест: /test_admin")
    me = await bot.get_me()
    print(f"🤖 @{me.username} запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
