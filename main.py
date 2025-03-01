from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, LOG_CHANNEL
from db_worker import DBINIT
from bot.utils.cryptopay import crypto
import bot.handlers as h
import bot.keyboards as k
import settings.keywords as keywords
import sys

import aioschedule
import asyncio
import config
import json

arguments = sys.argv

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = DBINIT('db.db')

if len(arguments) > 1:
    if arguments[1] in ["migrate", "--migrate"]:
        db.migrate()
    elif arguments[1] in ["delete-new", "--delete-new"]:
        db.delete_new_column()
        print("Столбцы удалены успешно")
    elif arguments[1].startswith("--test"):
        db.remove_mines(5297121761)
        print(keywords.ROCK_SIZER_PAPER_COMBINE)

async def maxbet_of_the_day():
    day_maxbet = db.get_all_maxbet()[0]
    day_maxbet_user_id = db.get_all_maxbet()[1]
    day_maxbet_name = db.get_all_maxbet()[2]
    db.set_all_maxbet(nums=0, user_id=5297121761, name="life")
    await bot.send_message(config.MAIN_CHANNEL, f'<b>Самая большая ставка за день: <b>{day_maxbet}$</b> от <b><a href="tg://user?id={day_maxbet_user_id}">{day_maxbet_name}</a></b>\n<b>Статистика обновлена. Ждем ваших ставок!</b>\n<blockquote>Пользователь получил 5$ в боте @{config.bot_username}</blockquote>', parse_mode="HTML")

    check_url = await crypto.create_check("USDT", 5)
    check_url = check_url.bot_check_url
    await bot.send_message(day_maxbet_user_id, 'Поздравляю! Вы победили в ежедневном конкурсе "Самая большая ставка"! Заберите 5$ кнопкой ниже!', reply_markup=k.functional.create_double_button(check_url))
    with open('metadata.json') as f:
        json_query = json.load(f)
        old_maxbet_message_id = json_query["maxbet_message_id"]
    await bot.edit_message_text(chat_id=config.MAIN_CHANNEL, message_id=old_maxbet_message_id, text=f"Максимальная ставка за сегодня: <b>0$</b> от\n<b>Победитель получит 5$ в конце дня!</b>", parse_mode="HTML")


async def schedule():
    aioschedule.every().day.at("21:00").do(maxbet_of_the_day)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)

async def on_startup(_):
    asyncio.create_task(schedule())
    await bot.send_message(LOG_CHANNEL, "🚀 Bot start!")
    print("The bot has been started")


def register_handlers():
    h.cmds.register_handlers(dp)
    h.admin.register_handlers(dp)
    h.game.register_handlers(dp)
    h.mines.register_handlers(dp)
    h.replenish.register_handlers(dp)
    k.functional.register_handlers(dp)

if __name__ == "__main__":
    register_handlers()
    executor.start_polling(dp, on_startup=on_startup)