from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import decode_payload
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import keyboards
from bot.utils import text
from bot.utils.cryptopay import crypto
from bot.handlers import game
from bot.states import states_groups
import main, config, asyncio
import logging

async def start_bet(call: CallbackQuery):
    await states_groups.BalanceBetState.bet.set()
    await call.message.answer("<code>Введите сумму ставки:</code>", parse_mode="HTML")

async def process_bet(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['bet'] = message.text
    
    if data["bet"] == "/cancel":
        await message.answer("Отменено.")
        await state.finish()
        return

    try:
        bet = float(data["bet"])
        static_balance = main.db.get_balance(message.from_user.id)
        balance = float(static_balance) if static_balance != None else 0

        if bet > balance:
            await states_groups.BalanceBetState.bet.set()
            await message.answer(f"<code>Недостаточный баланс. Ваш баланс: {balance}$\n/cancel чтобы отменить</code>", parse_mode="HTML")
            return
        
        await states_groups.BalanceBetState.comment.set()
        await message.answer("<code>Введите комментарий для игры:</code>", parse_mode="HTML")
    except Exception:
        await states_groups.BalanceBetState.bet.set()
        await message.answer("<code>Неверная сумма ставки. Введите верную сумму\n/cancel чтобы отменить</code>", parse_mode="HTML")
        return

async def process_comment(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
    
    if data["comment"] == "/cancel":
        await message.answer("Отменено.")
        await state.finish()
        return

    await message.answer(f"<b>Ставка: <code>{data['bet']}$</code>\nКомментарий: <code>{data['comment']}</code></b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("♠️ Сделать ставку", callback_data="bet_balance_finish")]]))
    await states_groups.BalanceBetState.finish.set()

async def finish_bet(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        bet = data["bet"]
        comment = data["comment"]
    
    static_balance = main.db.get_balance(call.from_user.id)
    balance = float(static_balance) if static_balance != None else 0

    main.db.set_balance(call.from_user.id, float(balance) - float(bet))
    success_message = await call.message.answer("💸")
    await asyncio.sleep(3)
    await success_message.edit_text("👌")

    formated_bet = '{:.2f}'.format(float(bet)) if float(bet) != int(float(bet)) else int(float(bet))
    formated_name = f"{call.from_user.first_name} {call.from_user.last_name}" if call.from_user.last_name else call.from_user.first_name
    user_link = f"tg://user?id={call.from_user.id}"

    bet_message = await main.bot.send_message(config.MAIN_CHANNEL, f"<b><a href='{user_link}'>{formated_name}</a></b> <a href='{config.CHECK_URL}'>отправил(а)</a><b> 🪙 {formated_bet} USDT (${formated_bet})</b>\n\n💬 {comment}", parse_mode="HTML", disable_web_page_preview=True)
    await game.getter(msg_query=bet_message)


    await state.finish()

async def cmd_start(message: Message):
    """Обработчик команды /start"""
    args = message.get_args()  # Получаем аргументы из сообщения
    
    # Проверяем, есть ли пользователь в базе
    user_exists = main.db.users_exists(message.from_user.id)
    
    if not user_exists:  # Если пользователь новый
        if args.startswith("ref"):
            referer_id = args[3:]
            main.db.add_user(message.from_user.id, referer_id)
            referals = int(main.db.get_referals(referer_id) or 0) + 1
            main.db.set_referals(referer_id, referals)
        else:
            main.db.add_user(message.from_user.id, "NULL")
    
    # Активируем пользователя
    main.db.set_active(message.from_user.id)
    
    # Проверяем наличие аргументов (например, check или ref)
    if args and not args.startswith("ref") and args != "bet":
        id = decode_payload(args)  # Расшифровываем аргумент
        if int(id) == message.from_user.id:
            # Если аргумент относится к текущему пользователю
            if main.db.have_check(message.from_user.id):
                check_id = main.db.get_check_id(message.from_user.id)
                check = await crypto.get_checks(check_ids=check_id)
    
                if check and hasattr(check, "bot_check_url"):  # Проверяем, что check не None и имеет атрибут bot_check_url
                    await message.answer(
                        "🎁 | Получите ваши средства.",
                        reply_markup=keyboards.functional.create_double_button(check.bot_check_url)
                    )
                    main.db.remove_check(check_id)
                else:
                    logging.error(f"Чек не найден или некорректный: check_id={check_id}, check={check}")
                    await message.answer("⚠️ | Произошла ошибка при обработке вашего чека.")

    elif args == "bet":
       await message.answer("<b>Чтобы сделать ставку с баланса, нажмите на кнопку ниже:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("♠️ Сделать ставку с баланса", callback_data="bet_balance_start")]]))

    else:
        # Обработка реферальных ссылок
        if not user_exists and args.startswith("ref"):  # Только для новых пользователей
            referer_id = args[3:]
            if str(referer_id) != str(message.from_user.id):  # Исключаем саморефералы
                ref_markup = InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton("🥷 Реферер", url=f"tg://user?id={referer_id}")]]
                )
                await main.bot.send_message(
                    message.from_user.id, 
                    f"<b>Вас пригласил пользователь </b> <code>{referer_id}</code>\n<b>Отменить это действие нельзя</b>", 
                    parse_mode="HTML", 
                    reply_markup=ref_markup
                )

        # Отправляем фото профиля и информацию пользователю
        await message.answer_photo(
            open("imgs/menu.jpg", 'rb'), 
            text.main_text, 
            reply_markup=keyboards.functional.bet_channel_button(), 
            parse_mode='HTML'
        )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(process_bet, state=states_groups.BalanceBetState.bet)
    dp.register_message_handler(process_comment, state=states_groups.BalanceBetState.comment)
    dp.register_callback_query_handler(start_bet, text='bet_balance_start')
    dp.register_callback_query_handler(finish_bet, text='bet_balance_finish', state=states_groups.BalanceBetState.finish)