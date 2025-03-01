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
    """...."""
    if msg_query.chat.id == config.CHANNEL_BROKER: #проверка чтобы сообщение было в канале посреднике
        if msg_query.entities: #проверяем на наличие entities
            #amount_text = msg_query.text.split("отправил(а)")[1]
            #amount_match = re.search(r"([\d.]+)\s*USDT", amount_text)
            #if amount_match:
                #amount = float(amount_match.group(1).replace(',', '.')) 
            amount = float(msg_query.text.split("отправил(а) 🪙")[1].split()[0].replace(',', "")) #получаем сумму ставки
            name = msg_query.text.split("отправил(а) 🪙")[0] #получаем имя чела
            if msg_query.entities[0].user and msg_query.entities[0].user != "Некто": #проверяем есть ли ссылка на чела
                user = msg_query.entities[0].user
                username = f"@{user.username}" if user.username else user.full_name
                name = user.full_name #снова получаем имя более надежным способом
                if "отправил(а)" in name:
                    return
                msg_text = msg_query.text.removeprefix(name) #удаляем имя из сообщения от греха подальше
                user_id = int(user.id)

                if not main.db.users_exists(user_id): main.db.add_user(user_id, "NULL")
                #asset =  msg_text.split("отправил(а)  🪙 ")[1].split()[1]
                asset = "USDT"
                #amount_text = msg_query.text.split("отправил(а)")[1]
                #amount_match = re.search(r"([\d.]+)\s*USDT", amount_text)
                #if amount_match:
                    #amount = float(amount_match.group(1).replace(',', '.')) 
                if user_id not in main.db.get_bannned(): #провека чтобы чел не был в бане
                    if "💬 " in msg_query.text: #проверяме на наличие комента
                        coef = 0
                        if f"@{config.bot_username.lower()}" in name.lower(): #увеличиваем кэф если у чела в нике MafiaCasinoTG
                            coef += 0.05
                        old_comment = msg_query.text.split("💬 ")[1]
                        comment = old_comment.lower()
                        comment = comment.replace('ё', 'е') 
                        await asyncio.sleep(4)
                        new_text = msg_query.html_text + "\n\n✅ • Ваша ставка принята в работу!"
                        await main.bot.edit_message_text(chat_id=config.CHANNEL_BROKER, message_id=msg_query.message_id, text=new_text, parse_mode="HTML", disable_web_page_preview=True)
                        if amount > config.max:
                            try:
                                check = await crypto.create_check(asset, amount - amount * 0.5)
                                main.db.add_check(user_id, check.check_id)
                                await main.bot_send_message(config.MAIN_CHANNEL, f"<b>❗ • Максимальная ставка {config.max} USDT.</b>\n\n<blockquote><b>Нажмите на кнопку ниже, чтобы вернуть деньги c комиссией 50%!</b></blockquote>", 'html', reply_markup=keyboards.functional.create_url_button(await get_start_link(user_id, True), "💸 • Вернуть"))
                                return
                            except:
                                await main.bot.send_message(config.MAIN_CHANNEL, f"<b>❗ •  Максимальная ставка {config.max} USDT.\n\n<blockquote>Сумма с комиссией 50% будет зачислена администрацией вручную.</blockquote></b>" + "\n\n"+ text.links, 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "Сделать Ставку"), disable_web_page_preview=True)
                                await main.bot.send_message(config.LOG_CHANNEL, f"❗{username} ({user_id}). {amount - amount * 0.5} ЗАДОЛЖЕННОСТЬ!")
                                return
                        #await main.bot.send_message(config.MAIN_CHANNEL, "[✅] Ваша ставка принята в работу!")
                        message = await main.bot.send_message(config.MAIN_CHANNEL, text.get_stake(amount, asset, comment, name), 'html', disable_web_page_preview=True)
                        gp = game_process.GameProcess(amount, asset, coef, user_id, username, name=name)
                        if not main.db.users_exists(user_id):
                            main.db.add_user(user_id)
                            main.db.set_active(user_id, 0)
                        main.db.edit_total(user_id, 1)
                        amount_for_moneyback = amount if asset == "USDT" else amount * 2.8
                        main.db.edit_moneyback(user_id, amount_for_moneyback*config.MONEYBACK)
                        if func.contains(keywords.DICE, comment):
                            new_com = func.remove_prefixes(keywords.DICE, comment)
                            print(new_com)
                            if func.equals(keywords.EVEN, new_com):
                                await gp.dice_procces(message, 'even')
                            elif func.equals(keywords.ODD, new_com):
                                await gp.dice_procces(message, 'odd')
                            elif func.equals(keywords.MORE, new_com):
                                await gp.dice_procces(message, 'more')
                            elif func.equals(keywords.LESS, new_com):
                                await gp.dice_procces(message, 'less')
                            elif new_com.isdigit() and new_com != "456" and new_com != "123" and new_com != "321" and new_com != "654" and new_com != "246" and new_com != "135":
                                    coef += coefs.DICE_NUMBER
                                    n = int(new_com)
                                    if 0 < n < 7:
                                       await gp.dice_procces(message, 'number', n)
                                    else:
                                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            elif "дуэль " in new_com:
     
                                num = new_com.split()[1]
                                if num.isdigit():
                                    num = int(num)
                                    if 0 < num < 3:
                                        await gp.duel_number_process(message, num)
                                    else:
                                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            elif new_com == "дуэль":
                                await gp.duel_proccess(message)
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            return
                        if func.contains(keywords.SECTOR, comment):
                            new_com = func.remove_prefixes(keywords.SECTOR, comment)
                            if new_com.isdigit() and new_com != "456" and new_com != "123" and new_com != "321" and new_com != "654" and new_com != "246" and new_com != "135":
                                coef += coefs.DICE_SECTOR
                                n = int(new_com)
                                if 0 < n < 4:
                                    pass
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                                    return 0
                                sector = n
                                await gp.dice_procces(message, 'sector', n=sector)
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.DARTS, comment):
                            new_com = func.remove_prefixes(keywords.DARTS, comment)
                            if func.equals(keywords.RED, new_com):
                                await gp.darts_procces(message, 'r')
                            elif func.equals(keywords.WHITE, new_com):
                                await gp.darts_procces(message, 'w')
                            elif func.equals(keywords.CENTER, new_com):
                                await gp.darts_procces(message)
                            elif func.equals(keywords.MISS, new_com):
                                await gp.darts_procces(message, 'miss')
                            elif "дуэль " in new_com:
                                coef += coefs.DUEL
                                num = new_com.split()[1]
                                if num.isdigit():
                                    num = int(num)
                                    if 0 < num < 3:
                                        await gp.duel_number_process(message, num, '🎯', ['первого дротика', 'второго дротика'])
                            elif new_com == "дуэль":
                                await gp.duel_proccess(message, '🎯', ['первого дротика', 'второго дротика'], ['lose.jpg', 'win.jpg'])
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.BASKET, comment):
                                new_com = func.remove_prefixes(keywords.BASKET, comment)
                                if func.equals(keywords.GOAL, new_com):
                                    await gp.basketball_process(message)
                                elif func.equals(keywords.MISS, new_com):
                                    await gp.basketball_process(message, 'miss')
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.FOOTBALL, comment):
                            new_com = func.remove_prefixes(keywords.FOOTBALL, comment)
                            if func.equals(keywords.GOAL, new_com):
                                await gp.footaball_process(message)
                            elif func.equals(keywords.MISS, new_com):
                                await gp.footaball_process(message, 'miss')
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.BOWLING, comment):
                            new_com = func.remove_prefixes(keywords.BOWLING, comment)
                            if new_com.isdigit():
                                stake = int(new_com)
                                if -1 < stake < 7:
                                    await gp.bowling_process(message, stake)
                            elif func.equals(keywords.STRIKE, new_com):
                                await gp.bowling_process(message, 0)
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.MINES, comment):
                            if not main.db.user_played_mines(user_id):
                                new_com = comment
                                new_com = new_com.removeprefix("мины ")
                                if new_com.isdigit():
                                    n = int(int(new_com))
                                    if 25 > n > 2:
                                        c = 0
                                        coef += 1
                                        await main.bot.send_message(user_id, f"*⚡ Выберете любой слот*\n*Клеток открыто:* 0\n*Коэффицент:* 1X\n*Выигрыш:* {round(amount * coef, 2)}  {asset}", 'markdown', reply_markup=keyboards.functional.create_mine_keyboards(n, user_id, amount, asset, username))
                                        await message.answer(f"<b>⚡ <a href='https://t.me/{username}'>{username}</a>, бот отправил вам сообщение в личный чат!</b>", "HTML")
                                    else:
                                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            else:
                                if amount < dict(await get_balance())[asset]:
                                    if amount < 1:
                                        check = await crypto.create_check(asset, amount - amount * 0.1)
                                        main.db.add_check(user_id, check.check_id)
                                        msag = await message.reply("<b>❗ Вы ещё не завершили предыдущую игру</b>\n\n<blockquote><b>Нажмите на кнопку ниже, чтобы вернуть деньги c комиссией 10%!</b></blockquote>", 'html', reply_markup=keyboards.functional.create_url_button(await get_start_link(user_id, True), "Вернуть💸"))
                                    else:
                                        await crypto.transfer(user_id, asset, amount - amount * 0.1, text.rnd_id())
                                        msag = await message.reply("<b>❗ Вы ещё не завершили предыдущую игру</b>\n\n<blockquote><b>Деньги возвращены на ваш баланс c комиссией 10%!</b></blockquote>", 'html')
                                else:
                                    msag = await message.reply("*❗ Вы ещё не завершили предыдущую игру*\n\n<blockquote>Напишите администрации для возвращения средств!</blockquote>", 'markdown')
                                await asyncio.sleep(20)
                                await msag.delete()
                        elif func.equals(keywords.ROCK_SIZER_PAPER_COMBINE, comment):
                            if func.equals(keywords.ROCK_SIZER_PAPER["paper"], comment): _value = "paper"
                            elif func.equals(keywords.ROCK_SIZER_PAPER["sizer"], comment): _value = "sizer"
                            else: _value = "rock"
                            
                            await gp.rock_paper_sizer_proccess(message, value=_value)
                        else:
                            if func.equals(keywords.EVEN, comment):
                                await gp.dice_procces(message, 'even')
                            elif func.equals(keywords.ODD, comment):
                                await gp.dice_procces(message, 'odd')
                            elif func.equals(keywords.RED, comment):
                                await gp.darts_procces(message, 'r')
                            elif func.equals(keywords.WHITE, comment):
                                await gp.darts_procces(message, 'w')
                            elif func.equals(keywords.DARTS, comment) or func.equals(keywords.CENTER, comment):
                                await gp.darts_procces(message)
                            elif func.equals(keywords.BASKET, comment):
                                await gp.basketball_process(message)
                            elif func.equals(keywords.FOOTBALL, comment):
                                await gp.footaball_process(message)
                            elif func.equals(keywords.BOWLING, comment) or func.equals(keywords.STRIKE, comment):
                                await gp.bowling_process(message, 0)
                            elif func.equals(keywords.SLOTS, comment):
                                msg = await message.answer_dice('🎰')
                                v = msg.dice.value
                                await asyncio.sleep(6)
                                if v == 64:
                                    await func.winner(message, amount, asset, coefs.SLOTS_777 + coef, user_id, username, "Победа! Вы выбили три в ряд!", type="cas") #777
                                elif v == 1 or v==22:
                                    await func.winner(message, amount, asset, coefs.SLOTS_GRAPE + coef, user_id,  username, "Победа! Вы выбили три в ряд!", type="cas") #bar and grape
                                elif v == 43:
                                    await func.winner(message, amount, asset, coefs.SLOTS_LEMON + coef, user_id, username, "Победа! Вы выбили три в ряд!", type="cas")
                                else:
                                    await func.looser(message, "Проигрыш! Вы не выбили три в ряд!", user_id=user_id, amount=amount, type="cas")
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                    else:
                        #если нет комента
                        message = await main.bot.send_message(config.MAIN_CHANNEL, text.get_stake(amount, asset, '❌ Нет комментария', name), 'html', disable_web_page_preview=True)
                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        await asyncio.sleep(20)
                        await message.delete()
                else:
                    #если бан
                    await main.bot.send_message(config.LOG_CHANNEL, f"Забанненый {username}({user_id}) отправил {amount} {asset}")
            else:
                #если нет ссылки на акк
                await main.bot.send_message(config.LOG_CHANNEL, f"Не удалось распознать пользователя с именем {name}! Его ставка {amount} {asset}", disable_web_page_preview=True)
                message = await main.bot.send_message(config.MAIN_CHANNEL, f"❗ Мы не смогли опознать человека с именем <b>{name}</b>! Пишите в личные сообщения админам\n\n⚠️ Проблема возможно возникла из-за ваших настроек приватности!", "html", disable_web_page_preview=True)

    elif msg_query.chat.id == config.REPLENISH_CHANNEL:
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
                    await main.bot.send_message(user_id, f"<b>Ваш баланс был пополнен на {amount}$</b>", parse_mode="HTML")
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
        return

    else:
        #если нет ссылки на акк
        await main.bot.send_message(config.LOG_CHANNEL, f"Не удалось распознать пользователя с именем {name}! Его ставка {amount} {asset}", disable_web_page_preview=True)
        message = await main.bot.send_message(config.MAIN_CHANNEL, f"❗ Мы не смогли опознать человека с именем <b>{name}</b>! Пишите в личные сообщения админам\n\n⚠️ Проблема возможно возникла из-за ваших настроек приватности!", "html", disable_web_page_preview=True)

async def anon_getter(msg_query: Message):
    amount = float(msg_query.text.split("отправил 🪙")[1].split()[0].replace(',', ""))
    name = msg_query.text.split("отправил 🪙")[0] 
    await main.bot.send_message(config.LOG_CHANNEL, f"Не удалось распознать пользователя с именем {name}! Его ставка {amount} USDT", disable_web_page_preview=True)
    message = await main.bot.send_message(config.MAIN_CHANNEL, f"❗ Мы не смогли опознать человека с именем <b>{name}</b>! Пишите в личные сообщения админам\n\n⚠️ Проблема возможно возникла из-за ваших настроек приватности!", "html", disable_web_page_preview=True)

def register_handlers(dp: Dispatcher):
    dp.register_channel_post_handler(getter, ChatTypeFilter(ChatType.CHANNEL), text_contains="отправил(а)")
    dp.register_channel_post_handler(anon_getter, ChatTypeFilter(ChatType.CHANNEL), text_contains="отправил")