from aiogram.utils.exceptions import BotBlocked
from aiogram.utils.exceptions import ChatNotFound, UserDeactivated, CantInitiateConversation
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from config import ADMINS
import asyncio
import main

async def send_ad(call: CallbackQuery, bot: Bot, markup):
    users_list = main.db.get_active_users()
    i = 0
    for user in users_list:
        if i==4:
            i=0
            await asyncio.sleep(1.1)
        i=i+1
        try:
            try:
                if user[0] not in ADMINS:
                    await bot.copy_message(user[0], call.from_user.id, call.message.message_id, reply_markup=markup, caption_entities=call.message.entities) 
            except (BotBlocked, ChatNotFound, UserDeactivated, CantInitiateConversation):
                main.db.set_active(user[0], 0)
                await call.message.answer(f"Пользователь {user[0]} заблокировал бота")
        except IndexError:
            break