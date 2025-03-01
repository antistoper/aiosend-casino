from aiogram.types import Message, ChatType
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram import Dispatcher
from aiogram.utils.deep_linking import decode_payload, get_start_link
import re
import config
from settings import keywords, coefs
from bot.utils import func, text, game_process
from bot.utils.cryptopay import get_balance, crypto
import asyncio, config, main, random
from bot import keyboards

async def getter(msg_query: Message):
    print('s')
    if msg_query.chat.id == config.REPLENISH_CHANNEL:
        if msg_query.entities:
            amount = float(msg_query.text.split("отправил(а)")[1].split()[0].replace(',', "")) #получаем сумму ставки
            name = msg_query.text.split("отправил(а)")[0] #получаем имя чела
            if msg_query.entities[0].user and msg_query.entities[0].user != "Некто": #проверяем есть ли ссылка на чела
                user = msg_query.entities[0].user
                username = f"@{user.username}" if user.username else user.full_name
                name = user.full_name #снова получаем имя более надежным способом
                if "отправил(а)" in name:
                    return
                msg_text = msg_query.text.removeprefix(name) #удаляем имя из сообщения от греха подальше
                user_id = int(user.id)

                if not main.db.users_exists(user_id): main.db.add_user(user_id, "NULL")
                asset = "USDT"
                if user_id not in main.db.get_bannned():
                    static_balance = main.db.get_balance(user_id)
                    balance = float(static_balance) if static_balance != None else 0
                    main.db.set_balance(user_id, balance + amount)
                    main.bot.send_message(user_id, f"<b>Ваш баланс был пополнен на {amount}$</b>", parse_mode="HTML")
                else:
                    #если бан
                    await main.bot.send_message(config.LOG_CHANNEL, f"Забанненый {username}({user_id}) отправил {amount} {asset}")
            else:
                #если нет ссылки на акк
                await main.bot.send_message(config.LOG_CHANNEL, f"Не удалось распознать пользователя! Его ставка {amount} {asset}", disable_web_page_preview=True)
                message = await main.bot.send_message(config.MAIN_CHANNEL, f"❗ Мы не смогли опознать человека! Пишите в личные сообщения админам\n\n⚠️ Проблема возможно возникла из-за ваших настроек приватности!", "html", disable_web_page_preview=True)

        else:
            #если нет ссылки на акк
            await main.bot.send_message(config.LOG_CHANNEL, f"Не удалось распознать пользователя! Его пополнение {amount} {asset}", disable_web_page_preview=True)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(getter, text_contains="отправил(а)")