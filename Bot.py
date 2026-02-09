import asyncio
import logging
import random
from datetime import datetime, timedelta
import sys

# ВАШИ ДАННЫЕ
TOKEN = "8568717574:AAEFMhqvccnZ6u0Go_BDyppSK0Ph9Maraho"
GROUP_ID = 8580261363

# ЛОГИ В КОНСОЛЬ (видно в Bothost)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 ИНИЦИАЛИЗАЦИЯ БОТА...")

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router

print("📥 Импорты загружены")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_captchas = {}

print("🔧 Хендлеры регистрируются...")

@router.message(Command("test_admin"))
async def test_admin(message: Message):
    print(f"🧪 /test_admin от {message.from_user.id}")
    try:
        me = await bot.get_me()
        print(f"🤖 Бот: @{me.username}")
        
        bot_info = await bot.get_chat_member(GROUP_ID, me.id)
        status = bot_info.status
        can_invite_users = getattr(bot_info, 'can_invite_users', False)
        
        print(f"📊 Статус в группе: {status}, Приглашения: {can_invite_users}")
        
        await message.answer(
            f"🔍 <b>ПРОВЕРКА:</b>\n\n"
            f"👤 @{me.username}\n"
            f"📊 Статус: {status}\n"
            f"🔗 Приглашения: {'✅' if can_invite_users else '❌'}\n"
            f"🆔 Группа: {GROUP_ID}"
        )
    except Exception as e:
        print(f"❌ Ошибка test_admin: {e}")
        await message.answer(f"❌ {str(e)}")

@router.message(CommandStart(), Command("start"))
async def start_captcha(message: Message):
    print(f"✅ /start от {message.from_user.id}")
    a, b = random.randint(1, 20), random.randint(1, 20)
    answer = a + b
    
    user_captchas[message.from_user.id] = {
        "answer": answer, 
        "time": datetime.now()
    }
    
    print(f"🔢 Капча {message.from_user.id}: {a}+{b}={answer}")
    await message.answer(f"🔐 <b>Капча:</b>\n\n<code>{a} + {b} = ?</code>")

@router.message(F.text & ~F.text.startswith("/"))
async def check_captcha(message: Message):
    print(f"💭 Ответ от {message.from_user.id}: '{message.text}'")
    
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
            print(f"🎉 КАПЧА ПРОЙДЕНА {user_id}")
            
            expire_date = int((datetime.now() + timedelta(minutes=5)).timestamp())
            link_data = await bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                name=f"captcha_{user_id}",
                expire_date=expire_date,
                member_limit=1
            )
            
            await message.answer(
                f"🎉 <b>УСПЕХ!</b>\n\n"
                f"🔗 <code>{link_
