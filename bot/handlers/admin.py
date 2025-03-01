from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from bot import keyboards
from bot.states import states_groups
from bot.utils import text, ad
from bot.utils.cryptopay import crypto, get_balance
import config, main, copy

import json

async def cmd_admin(message: Message):
    """Команда admin"""
    if message.from_user.id in config.ADMINS:
        await message.answer(await text.get_admin_menu_text(), reply_markup=keyboards.admink.admin_keyboard, parse_mode='HTML')

async def cb_back(call: CallbackQuery):
    """Кнопка назад"""
    await call.message.edit_text(await text.get_admin_menu_text(), reply_markup=keyboards.admink.admin_keyboard, parse_mode='HTML')  

async def cb_add_money(call: CallbackQuery):
    """Кнопка добавить деньги"""
    await call.message.edit_reply_markup(reply_markup=keyboards.admink.wallets_keyboard_add)

async def cb_cryptobot(call: CallbackQuery):
    """Кнопка криптобота"""
    if call.data.split("_")[1] == "adding":
        await call.message.edit_reply_markup(reply_markup=keyboards.admink.add_money_keyboard)
    else:
        await call.message.edit_reply_markup(reply_markup=keyboards.admink.take_money_keyboard)

async def cb_adding_money(call: CallbackQuery, state: FSMContext):
    """Кнопка валюты"""
    msg = await call.message.answer("Введите сумму пополнения, разделенную на 100", reply_markup=keyboards.admink.cancel_keyboard)
    await states_groups.AdminState.add_money.set()
    async with state.proxy() as data:
        data['asset'] = call.data.split('_')[1]
        data['message'] = call.message
        data['entering_message'] = msg

async def cb_taking_money(call: CallbackQuery, state: FSMContext):
    """Кнопка валюты"""
    msg = await call.message.answer("Введите сумму снятия, разделенную на 100", reply_markup=keyboards.admink.cancel_keyboard)
    await states_groups.AdminState.take_money.set()
    async with state.proxy() as data:
        data['asset'] = call.data.split('_')[1]
        data['message'] = call.message
        data['entering_message'] = msg

async def cb_take_money(call: CallbackQuery):
    """Кнопка взятия денег"""
    await call.message.edit_reply_markup(reply_markup=keyboards.admink.wallets_keyboard_take)
    
async def cb_cancel(call: CallbackQuery, state: FSMContext):
    """наташа отмена"""
    await call.message.delete()
    await state.finish()

async def publish_maxbet(call: CallbackQuery):
    with open('metadata.json') as f:
        json_query = json.load(f)
        old_maxbet_message_id = json_query["maxbet_message_id"] if json_query["maxbet_message_id"] != "id" else False
    if old_maxbet_message_id:
        await main.bot.unpin_chat_message(config.MAIN_CHANNEL, old_maxbet_message_id)
    old_maxbet = main.db.get_all_maxbet()
    new_message = await main.bot.send_message(config.MAIN_CHANNEL, f"Максимальная ставка за сегодня: <b>{old_maxbet[0]}$</b> от <a href='tg://user?id={old_maxbet[1]}'>{old_maxbet[2]}</a>\n<b>Победитель получит 5$ в конце дня!</b>", parse_mode="HTML")
    await main.bot.pin_chat_message(config.MAIN_CHANNEL, new_message.message_id)
    with open('metadata.json', "w") as f:
        data = {
            "maxbet_message_id": new_message.message_id
        }
        f.write(json.dumps(data, ensure_ascii=False))
    return 

async def cb_remchecks(call: CallbackQuery):
    """Удаляем все чеки"""
    checks = await crypto.get_checks()
    for check in checks:
        try:
            await crypto.delete_check(check.check_id)
            if main.db.check_exists(check.check_id):
                main.db.remove_check(check.check_id)
        except:
            if main.db.check_exists(check.check_id):
                main.db.remove_check(check.check_id)
    await call.message.answer("Чеки успешно удалены!")


async def adding_money_last_step(message: Message, state: FSMContext):
    """Добавка денег, обработка количества"""
    async with state.proxy() as data:
        asset = data['asset']
        msg = data['message']
        e_msg = data['entering_message']
    if message.text:
        if message.text.isdigit():
            amount = int(message.text) / 100
            if amount >= 0.05:
                invoice = await crypto.create_invoice(amount, asset)
                await message.answer(invoice.bot_invoice_url)
                await msg.edit_reply_markup(reply_markup=keyboards.admink.admin_keyboard)
                await e_msg.delete()
                await message.delete()
                await state.finish()
            else:
                await message.answer("Слишком маленькое значение.\nМинимальное значение - 5")
        else:
            await message.answer("Некоректное значение!")
            await state.finish()
    else:
        await state.finish()

async def take_money_last_step(message: Message, state: FSMContext):
    """Съёмка денег, обработка количества"""
    async with state.proxy() as data:
        asset = data['asset']
        msg = data['message']
        e_msg = data['entering_message']
    if message.text:
        if message.text.isdigit():
            amount = int(message.text) / 100
            if amount < dict(await get_balance())[asset]:
                if amount >= 0.05:
                    check = await crypto.create_check(asset, amount)
                    await message.answer(check.bot_check_url)
                    await msg.edit_reply_markup(reply_markup=keyboards.admink.admin_keyboard)
                    await e_msg.delete()
                    await message.delete()
                    await state.finish()
                else:
                    await message.answer("Слишком маленькое значение.\nМинимальное значение - 5")
            else:
                await message.answer("У нас нет таких денег :(")
        else:
            await message.answer("Некоректное значение!")
            await state.finish()
    else:
        await state.finish()
           
async def ban_user(message: Message):
    if message.from_user.id in config.ADMINS:
        id = message.text.split()[1]
        if id.isdigit():
            id = int(id)
            if id not in main.db.get_bannned():
                main.db.ban_user(id)
                await message.reply("Пользователь забанен!")
            else:
                await message.reply("Пользователь уже забанен")
        else:
            await message.reply("Неверный формат!")

async def deban_user(message: Message):
    if message.from_user.id in config.ADMINS:
        id = message.text.split()[1]
        if id.isdigit():
            id = int(id)
            if id in main.db.get_bannned():
                main.db.deban_user(id)
                await message.reply("Пользователь разбанен!")
            else:
                await message.reply("Пользователь не забанен")
        else:
            await message.reply("Неверный формат!")   

async def cb_Ad(call: CallbackQuery, state=FSMContext):
    await call.message.answer("Введите текст рассылки!", reply_markup=keyboards.admink.cancel_keyboard)
    await states_groups.AdminState.ad.set()

async def ad_handler(message: Message, state: FSMContext):
    try:
        await state.finish()
        await main.bot.copy_message(message.from_user.id, message.from_user.id, message.message_id, reply_markup=keyboards.admink.ad_constuctor)
    except Exception as e:
        await message.answer(f"Ошибка:\n{e}")
        await state.finish()

async def send_ad(call: CallbackQuery):
    msg = await call.message.answer("Старт рассылки...")
    if len(call.message.reply_markup.inline_keyboard) > 3:
        new_keyboard = copy.deepcopy(call.message.reply_markup)
        new_keyboard.inline_keyboard.pop(-1)
        new_keyboard.inline_keyboard.pop(-1)
        new_keyboard.inline_keyboard.pop(-1)
        await ad.send_ad(call, main.bot, new_keyboard)
    else:
        await ad.send_ad(call, main.bot, ReplyKeyboardRemove())
    await msg.edit_text("Рассылка успешно завершена")

from aiogram import Bot
from aiogram.types import ParseMode

from aiogram import types
from aiogram.types import ParseMode

async def cb_send_to_channel(callback_query: types.CallbackQuery):
    """Отправить сообщение о самой большой ставке в канал"""
    
    # Получаем channel_id из данных кнопки (если передан в callback_data)
    channel_id = -1002458898672  # Используйте свой channel_id, если хотите жестко задать

    # Получаем информацию о пользователе с самой большой ставкой
    user_data = db.get_user_with_max_stake()  # db - это ваш экземпляр DBINIT

    if user_data:
        user_id, biggest_stake = user_data
        # Формируем сообщение
        message = f"Пользователь с ID {user_id} сделал самую большую ставку: {biggest_stake} монет."

        # Отправляем сообщение в канал
        await callback_query.bot.send_message(channel_id, message, parse_mode=ParseMode.MARKDOWN)
        await callback_query.answer("Сообщение отправлено в канал!")
    else:
        # Если данных нет, отправляем сообщение о том, что нет ставок
        await callback_query.bot.send_message(channel_id, "Нет данных о самой большой ставке.")
        await callback_query.answer("Нет данных для отправки!")
    
async def add_button(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите:\nтекст\nurl", reply_markup=keyboards.admink.cancel_keyboard)
    await states_groups.AdminState.add_button.set()
    async with state.proxy() as data:
        data["msg"] = call.message
    
async def add_button_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        msg = data["msg"]
    text, url = message.text.split("\n")
    button = InlineKeyboardButton(text, url)
    NewMarkup = copy.deepcopy(msg.reply_markup)
    NewMarkup.inline_keyboard.insert(0, [button])
    await main.bot.edit_message_reply_markup(message.from_user.id, msg.message_id, reply_markup=NewMarkup)
    await message.delete()
    await state.finish()

async def cb_admin_menu_keyboard(call: CallbackQuery):
    await call.message.edit_text(f"Активных пользователей: *{len(main.db.get_active_users())}*\nВсего: *{len(main.db.get_users())}*", 'markdown', 
                                 reply_markup=keyboards.admink.admin_menu_keyboard)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_admin, commands=['admin'])
    dp.register_callback_query_handler(cb_back, text='back')
    dp.register_callback_query_handler(cb_add_money, text="add_money")
    dp.register_callback_query_handler(publish_maxbet, text="publish_maxbet")
    dp.register_callback_query_handler(cb_adding_money, text_contains="adding_")
    dp.register_callback_query_handler(cb_cryptobot, text_contains="CryptoBot_")
    dp.register_callback_query_handler(cb_taking_money, text_contains="taking_")
    dp.register_callback_query_handler(cb_take_money, text="take_money")
    dp.register_callback_query_handler(cb_cancel, text="cancel", state="*")
    dp.register_callback_query_handler(cb_remchecks, text="rem_checks")
    dp.register_message_handler(adding_money_last_step, state=states_groups.AdminState.add_money)
    dp.register_message_handler(take_money_last_step, state=states_groups.AdminState.take_money)
    dp.register_message_handler(ban_user,  lambda msg: str(msg.text).startswith("!ban"))
    dp.register_message_handler(deban_user,  lambda msg: str(msg.text).startswith("!unban"))
    dp.register_callback_query_handler(send_ad, text="Send_ad")
    dp.register_callback_query_handler(add_button, text="add_button")
    dp.register_message_handler(add_button_handler, state=states_groups.AdminState.add_button)
    dp.register_callback_query_handler(cb_Ad, text="ad", state="*")
    dp.register_message_handler(ad_handler, content_types=['text', 'photo', 'video', 'voice'], state=states_groups.AdminState.ad)
    dp.register_callback_query_handler(cb_admin_menu_keyboard, text="other")
    dp.register_callback_query_handler(cb_send_to_channel, text="send_to_channel")





