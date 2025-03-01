from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto, InputFile
from aiogram import Dispatcher

import random
from config import CHECK_URL
from bot.utils import text
from bot.utils.cryptopay import get_balance, crypto
import config
import main

def create_double_button(url, text="🎁 Забрать приз"):
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text, url)], [InlineKeyboardButton("♠️ Сделать cтавку", CHECK_URL)]])

def create_url_button(url, text="🎁 Забрать приз"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text, url)]])

def create_mine_keyboards(num: int, id: int, amount: float, asset: str, username: str):
    markup = InlineKeyboardMarkup(5)
    mines = random.sample(range(0, 25), num)
    main.db.add_mines(id, mines, amount, asset, username)
    for i in range(25):
        markup.insert(InlineKeyboardButton('⬜️', callback_data=f"mines_{id}_{i}"))
    return markup

def bet_channel_button(url=f"{config.CHECK_URL}", text="♠️ Сделать ставку"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text, callback_data="bet"), InlineKeyboardButton("🆘 Тех. Поддержка", url="https://t.me/micecas")], [InlineKeyboardButton("🙎‍♂️ Профиль", callback_data="profile")], [InlineKeyboardButton("💵 Реферальная система", callback_data="referal_system")]])

def back_channel_button(url="https://t.me/lonocas", text="🎲 Вернуться в канал"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text, url=url)]])

def replenish_markup():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("Пополнить баланс", url=config.REPLENISH_CHECK_URL)]])

async def bet(callback):
    await main.bot.send_message(callback.from_user.id, "<code>Выберите через что вы хотите сделать ставку:</code>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🦋 CryptoBot", url=config.CHECK_URL)], [InlineKeyboardButton("💰 Ставка с баланса", url=f"https://t.me/{config.bot_username}?start=bet")]]))

async def referal_info(callback):
    await main.bot.answer_callback_query(
        callback.id,
        text=text.referal_info, show_alert=True
    )

async def referal_get_money(callback):
    if main.db.get_money(callback.from_user.id) != None:
        amount = round(main.db.get_money(callback.from_user.id), 2)
        if amount < float(3):
            await main.bot.answer_callback_query(
                callback.id,
                text="Вывод доступен только от 3$", 
                show_alert=True
            )
            return 0
        elif amount > float(5):
            await main.bot.send_message(callback.from_user.id, f"<b>Создана заявка на вывод</b> <code>{amount}$</code>\n<b>Перешлите это сообщение администрации, и скоро администрация выведет деньги</b>", parse_mode="HTML")
            main.db.set_money(callback.from_user.id, 0)
            return 0
        else:
            check = await crypto.create_check("USDT", amount)
            main.db.add_check(callback.from_user.id, check.check_id)
            main.db.set_money(callback.from_user.id, 0)

            get_referal_money_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(f"🎁 Получить {amount}$", url=f"{check.bot_check_url}")]])
            await main.bot.send_message(callback.from_user.id, f"<b>Поздравляем! вы получили {'{:.2f}'.format(amount)}$!\nНажмите на кнопку ниже чтобы забрать их.</b>", parse_mode="HTML", reply_markup=get_referal_money_markup)
    else:
        await main.bot.answer_callback_query(
            callback.id,
            text="Вывод доступен только от 3$", 
            show_alert=True
        )
        return 0

async def withdraw(callback):
    if main.db.get_balance(callback.from_user.id) != None:
        amount = round(main.db.get_balance(callback.from_user.id), 2)
        if amount < float(0.20):
            await main.bot.answer_callback_query(
                callback.id,
                text="Вывод доступен только от 0.20$", 
                show_alert=True
            )
            return 0
        elif amount > dict(await get_balance())["USDT"]:
            await main.bot.send_message(callback.from_user.id, f"<b>Создана заявка на вывод</b> <code>{'{:.2f}'.format(amount)}$</code>\n<b>Перешлите это сообщение администрации, и скоро администрация выведет деньги\n<i>PID: <code>{callback.from_user.id}</code></i></b>", parse_mode="HTML")
            main.db.set_balance(callback.from_user.id, 0)
            return 0
        else:
            check = await crypto.create_check("USDT", amount)
            main.db.add_check(callback.from_user.id, check.check_id)
            main.db.set_balance(callback.from_user.id, 0)

            get_referal_money_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(f"🎁 Получить {amount}$", url=f"{check.bot_check_url}")]])
            await main.bot.send_message(callback.from_user.id, f"<b>Поздравляем! вы получили {'{:.2f}'.format(amount)}$!\nНажмите на кнопку ниже чтобы забрать их.</b>", parse_mode="HTML", reply_markup=get_referal_money_markup)
    else:
        await main.bot.answer_callback_query(
            callback.id,
            text="Вывод доступен только от 0.20$", 
            show_alert=True
        )
        return 0

async def replenish(callback):
    await callback.bot.send_message(
        callback.from_user.id,
        "<b>Для пополнения баланса через CryptoBot перейдите по кнопке ниже.</b>",
        parse_mode="HTML",
        reply_markup=replenish_markup()
    )

async def profile(callback):
    back_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("💰 Вывести баланс", callback_data=f"withdraw"), InlineKeyboardButton("✚ Пополнить баланс", callback_data=f"replenish")], [InlineKeyboardButton("⏪ Назад", callback_data=f"back_to_main_menu")]])
    await main.bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message["message_id"], media=InputMediaPhoto(type="photo", media=InputFile(path_or_bytesio="imgs/profile.jpg", filename="profile.jpg")))
    await main.bot.edit_message_caption(callback.from_user.id, callback.message["message_id"], caption=text.get_profile(callback.from_user.id, callback.from_user.username), parse_mode="HTML", reply_markup=back_markup)

async def referal(callback):
    money = main.db.get_money(callback.from_user.id) if main.db.get_money(callback.from_user.id) != None else 0
    referals = main.db.get_referals(callback.from_user.id) if main.db.get_referals(callback.from_user.id) != None else 0
    referal_url = f"https://t.me/{config.bot_username}?start=ref{callback.from_user.id}"
    referer = main.db.get_referer(callback.from_user.id)

    if referer != None:
        ref_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("⚠︎ Информация", callback_data="referal_info"), InlineKeyboardButton("🥷 Реферер", url=f"tg://user?id={referer}")], [InlineKeyboardButton("Вывести деньги 💵", callback_data=f"referal_get_money")], [InlineKeyboardButton("⏪ Назад", callback_data=f"back_to_main_menu")]])
    else:
        referer = "Нету"
        ref_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("⚠︎ Информация", callback_data="referal_info")], [InlineKeyboardButton("Вывести деньги 💵", callback_data=f"referal_get_money")], [InlineKeyboardButton("⏪ Назад", callback_data=f"back_to_main_menu")]])
    await main.bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message["message_id"], media=InputMediaPhoto(type="photo", media=InputFile(path_or_bytesio="imgs/refs.jpg", filename="refs.jpg")))
    await main.bot.edit_message_caption(callback.from_user.id, callback.message["message_id"], caption=text.get_referal(callback.from_user.id, money, referals, referer, referal_url), parse_mode="HTML", reply_markup=ref_markup)

async def back_to_main_menu(callback):
    await main.bot.edit_message_media(chat_id=callback.from_user.id, message_id=callback.message["message_id"], media=InputMediaPhoto(type="photo", media=InputFile(path_or_bytesio="imgs/menu.jpg", filename="menu.jpg")))
    await main.bot.edit_message_caption(callback.from_user.id, callback.message["message_id"], caption=text.main_text, parse_mode="HTML", reply_markup=bet_channel_button())

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(profile, text="profile")
    dp.register_callback_query_handler(referal, text="referal_system")
    dp.register_callback_query_handler(referal_info, text="referal_info")
    dp.register_callback_query_handler(referal_get_money, text="referal_get_money")
    dp.register_callback_query_handler(withdraw, text="withdraw")
    dp.register_callback_query_handler(replenish, text="replenish")
    dp.register_callback_query_handler(bet, text="bet")
    dp.register_callback_query_handler(back_to_main_menu, text="back_to_main_menu")