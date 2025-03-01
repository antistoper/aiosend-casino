from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils import func
import main, copy

async def cb_mine(call: CallbackQuery):
    kb = copy.deepcopy(call.message.reply_markup)
    if main.db.mines_exist(call.from_user.id):
        mines_data = main.db.get_data_mines(call.from_user.id)
        id = int(call.data.split('_')[1])
        index = int(call.data.split('_')[2])
        amount = mines_data['amount']
        username = mines_data['username']
        asset = mines_data['asset']
        c = int(call.message.text.split('\n')[1].split()[2])
        coef = float(call.message.text.split('\n')[2].split()[1].removesuffix('X'))
        print(coef)
        mines_n = len(main.db.get_bad_mines(call.from_user.id))
        remaining_slots = func.remaining_slots(kb.inline_keyboard, call.from_user.id) - 1 
        if id == call.from_user.id:
            if index in main.db.get_bad_mines(call.from_user.id):
                new_kb = InlineKeyboardMarkup(5)
                for keyboards in kb.inline_keyboard:
                    for button in keyboards:
                        if button.text == "Забрать":
                            pass
                        elif int(float(button.callback_data.split('_')[2])) not in main.db.get_bad_mines(call.from_user.id):
                            new_kb.insert(InlineKeyboardButton('💎', callback_data='finish'))
                        else:
                            new_kb.insert(InlineKeyboardButton('❌', callback_data='finish'))
                await call.message.edit_text("Поражение!", reply_markup=new_kb)
                main.db.remove_mines(call.from_user.id)
            else:
                stop=False
                for keyboard in kb.inline_keyboard:
                    if not stop:
                        x = kb.inline_keyboard.index(keyboard) 
                    for button in keyboard:
                        if button.callback_data == call.data:
                            y = keyboard.index(button)
                            stop=True
                            break
                new_kb = copy.deepcopy(kb.inline_keyboard)
                new_kb[x][y] = InlineKeyboardButton('💎', callback_data=f'ready_empty_-1')
                markup = InlineKeyboardMarkup(inline_keyboard=new_kb)
                if func.check_button_back(markup.inline_keyboard):
                    if remaining_slots != 0:
                        coef = coef + (mines_n * 0.5) * (1/remaining_slots)
                    else:
                        coef = coef + (mines_n * 0.5) * (1/0.5)
                    markup.insert(InlineKeyboardButton("🎁 Забрать", callback_data=f"stop_{call.from_user.id}_{round(coef, 3)}"))             
                else:
                    if remaining_slots != 0:
                        coef = coef + (mines_n * 0.25) * (1/remaining_slots)
                    else:
                        coef = coef + (mines_n * 0.25) * (1/0.5)
                    markup.inline_keyboard[5].pop(0)
                    markup.insert(InlineKeyboardButton("🎁 Забрать", callback_data=f"stop_{call.from_user.id}_{round(coef, 3)}"))
                if not func.check_winning(call.from_user.id, markup.inline_keyboard):
                    await call.message.edit_text(text=f"*⚡Выберете любой слот*\n*Клеток открыто:* {c+1}\n*Коэффицент:* {round(coef, 2)}X\n*Выигрыш:* {round(amount * coef, 2)} {asset}", parse_mode='markdown',
                                            reply_markup=markup)
                else:
                    main.db.remove_mines(call.from_user.id)
                    await call.message.edit_text("*🔥Пустые клетки закончились!*", 'markdown')
                    await func.get_price_mine(call.message, amount, asset, coef, id, call.from_user.username)
                    main.db.remove_mines(call.from_user.id)
    else:
        await call.answer("Это не ваше поле!", show_alert=True)

async def cb_stop_mine(call: CallbackQuery):
    data = call.data.split('_')
    coef = float(data[2])
    id = int(data[1])
    mines_data = main.db.get_data_mines(call.from_user.id)
    amount = mines_data['amount']
    asset = mines_data['asset']
    if call.from_user.id == id:
        await func.get_price_mine(call.message, amount, asset, coef, id, call.from_user.username)
        main.db.remove_mines(call.from_user.id)
    else:
        await call.answer("⚠️Это не ваше поле!", True)
        
def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cb_mine, text_contains="mines_")
    dp.register_callback_query_handler(cb_stop_mine, text_contains="stop_")

