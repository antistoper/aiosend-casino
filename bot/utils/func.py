from aiogram.utils.deep_linking import decode_payload, get_start_link
from aiogram.types import Message

import main as m
import config
from bot.utils.cryptopay import get_balance, crypto
from bot.utils import text
from bot import keyboards
import base64, datetime, asyncio, main

import json 

def check_button_back(buttons) -> bool:
    for keyboard in buttons:
        for button in keyboard:
            if button.text == "🎁 Забрать":
                return False
    return True
   
def check_winning(id, buttons) -> bool:
    for keyboard in buttons:
        for button in keyboard:
            if button.callback_data != "finish" and "stop_" not in button.callback_data:
                i = int(button.callback_data.split('_')[2])
                if i not in m.db.get_bad_mines(id) and i != -1:
                    return False
    return True

def remaining_slots(buttons: list, id: int) -> int:
    i = 0
    for keyboard in buttons:
        for button in keyboard:
            if "stop_" not in button.callback_data:
                if button.callback_data != "ready_empty_-1" and int(button.callback_data.split('_')[2]) not in m.db.get_bad_mines(id):
                    i = i + 1
    return i

def contains(l, item) -> bool:
    for el in l:
        if el + " " in item:
            return True
    return False

def equals(l, item) -> bool:
    for el in l:
        if el==item:
            return True
    return False

def remove_prefixes(l: list, item: str):
    for el in l:
        item = item.removeprefix(el + " ")
    return item

async def get_price_mine(message: Message, amount, asset, coef, user_id, username, win_img = "mines-win.jpg"):
    static_balance = main.db.get_balance(user_id)
    balance = float(static_balance) if static_balance != None else 0
    main.db.set_balance(user_id, balance + amount * coef)
    await message.edit_text(f"<b>Победа! На ваш баланс была зачислена сумма в размере {round(amount * coef, 3)} {asset}</b>", 'html',
                            keyboards.functional.create_url_button(config.CHECK_URL, "💸 Сделать ставку"), disable_web_page_preview=True)
        
async def winner(message: Message, amount, asset, coef, user_id, username, name, a_text, photo = "win.jpg", type = 'def'):
        print(name)
        day_maxbet = main.db.get_all_maxbet()[0]
        wins = main.db.get_win(user_id) if main.db.get_win(user_id) != None and main.db.get_win(user_id) != "None" else 0
        oborot = main.db.get_oborot(user_id) if main.db.get_oborot(user_id) != None and main.db.get_oborot(user_id) != "None" else 0.00
        oborot_month = main.db.get_oborot_month(user_id) if main.db.get_oborot_month(user_id) != None and main.db.get_oborot_month(user_id) != "None" else 0.00
        maxwin = main.db.get_maxwin(user_id) if main.db.get_maxwin(user_id) != None and main.db.get_maxwin(user_id) != "None" else 0.00
        biggest_stake = main.db.get_biggest_stake(user_id) if main.db.get_biggest_stake(user_id) != None and main.db.get_biggest_stake(user_id) != "None" else 0.00

        if amount > biggest_stake:
            main.db.set_biggest_stake(user_id, amount)
            
        if amount * coef > maxwin:
            main.db.set_maxwin(user_id, amount * coef)
        if amount > day_maxbet:
            main.db.set_all_maxbet(nums=amount, user_id=user_id, name=name)
            with open('metadata.json') as f:
                json_query = json.load(f)
                old_maxbet_message_id = json_query["maxbet_message_id"]
            await main.bot.edit_message_text(chat_id=config.MAIN_CHANNEL, message_id=old_maxbet_message_id, text=f"Максимальная ставка за сегодня: <b>{amount}$</b> от <a href='tg://user?id={user_id}'>{name}</a>\n<b>Победитель получит 5$ в конце дня!</b>", parse_mode="HTML")
        main.db.set_oborot(user_id, oborot + amount)
        main.db.set_oborot_month(user_id, oborot_month + amount)   

        referer = main.db.get_referer(user_id)

        if referer is not None and referer not in ["NULL", "None"]:
            money = main.db.get_money(referer) if main.db.get_money(referer) != None else 0
            if referer == 5893162572:  # Замените на нужный ID
                main.db.set_money(referer, money - float(amount * 0.35))
            else:
                main.db.set_money(referer, money - float(amount / 4))    

        main.db.set_win(user_id, wins + 1)
        photo = "imgs/" + photo
        #if amount*coef < dict(await get_balance())[asset]:
        static_balance = main.db.get_balance(user_id)
        balance = float(static_balance) if static_balance != None else 0
        main.db.set_balance(user_id, balance + amount * coef)
        await message.reply_photo(open(photo, 'rb'),text.get_win_text(round(amount * coef, 3), asset, type, a_text), 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "💸 Сделать ставку"))
        #else:
        #await m.bot.send_message(config.LOG_CHANNEL, f"{username} ({user_id}) выиграл {round(amount * coef, 3)} {asset}. ЗАДОЛЖЕННОСТЬ!")
        #await message.reply_photo(open(photo, 'rb'),text.get_win_text(round(amount * coef, 3), asset, type, a_text, is_less=True), 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "💸 Сделать ставку"))

async def looser(message: Message, a_text, photo = "lose.jpg", user_id = 7940409905, amount = 0.04, type = "def", name = "antistoper"):
    day_maxbet = main.db.get_all_maxbet()[0]
    referer = main.db.get_referer(user_id)
    loses = main.db.get_lose(user_id) if main.db.get_lose(user_id) != None and main.db.get_lose(user_id) != "None" else 0
    oborot = main.db.get_oborot(user_id) if main.db.get_oborot(user_id) != None and main.db.get_oborot(user_id) != "None" else 0.00
    oborot_month = main.db.get_oborot_month(user_id) if main.db.get_oborot_month(user_id) != None and main.db.get_oborot_month(user_id) != "None" else 0.00

    biggest_stake = main.db.get_biggest_stake(user_id) if main.db.get_biggest_stake(user_id) != None and main.db.get_biggest_stake(user_id) != "None" else 0.00

    if amount > biggest_stake:
        main.db.set_biggest_stake(user_id, amount)
    
    if amount > day_maxbet:
        main.db.set_all_maxbet(nums=amount, user_id=user_id, name=name)
        with open('metadata.json') as f:
            json_query = json.load(f)
            old_maxbet_message_id = json_query["maxbet_message_id"]
        await main.bot.edit_message_text(chat_id=config.MAIN_CHANNEL, message_id=old_maxbet_message_id, text=f"Максимальная ставка за сегодня: <b>{amount}$</b> от <a href='tg://user?id={user_id}'>{name}</a>\n<b>Победитель получит 5$ в конце дня!</b>", parse_mode="HTML")

    main.db.set_oborot(user_id, oborot + amount)
    main.db.set_oborot_month(user_id, oborot_month + amount)

    main.db.set_lose(user_id, loses + 1)
    if referer is not None and referer not in ["NULL", "None"]:
        money = main.db.get_money(referer) if main.db.get_money(referer) != None else 0
        if referer == 5893162572:  #id
            main.db.set_money(referer, money + float(amount * 0.45))
        else:
            main.db.set_money(referer, money + float(amount / 4))
    
    photo = "imgs/" + photo
    await message.reply_photo(open(photo, 'rb'), text.get_lose_text(a_text, type), 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "💸 Сделать ставку"))

async def invalid_syntax(message: Message, amount, asset, user_id, username, name):
    end_amount = (amount - amount * 0.1)
    main.db.edit_total(user_id, -1)
    main.db.edit_moneyback(user_id, -(amount*config.MONEYBACK))
    if end_amount < dict(await get_balance())[asset]:
        if end_amount > 1:
                await crypto.transfer(user_id, asset, end_amount, text.rnd_id())
                msg = await message.reply(text.get_invalid_text(name), 'html', disable_notification=True, disable_web_page_preview=True)
        else:
            check = await crypto.create_check(asset, end_amount)
            m.db.add_check(user_id, check.check_id)
            msg = await message.reply(text.get_invalid_text(name, 'button'), 'html', reply_markup=keyboards.functional.create_url_button(await get_start_link(user_id, True), "Вернуть 💸"), disable_notification=True, disable_web_page_preview=True)
    else:       
        await m.bot.send_message(config.LOG_CHANNEL, f"❗ {username} ({user_id}) ошибся в синтаксисе. {round(end_amount, 3)} {asset.upper()}. ЗАДОЛЖЕННОСТЬ!")
        msg = await message.reply(text.get_invalid_text(name, 'admin'), 'html', disable_notification=True, disable_web_page_preview=True)