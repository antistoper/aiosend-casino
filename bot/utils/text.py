from bot.utils import cryptopay
from config import bot_username

import string, random, main

links = f"""<b><a href="https://t.me/bananacasNews">Как сделать ставку?</a> | <a href="https://t.me/BananacasNEWS">Новостной канал</a> | <a href="https://t.me/bananacasBot">Бот</a> | <a href="https://t.me/vklocked">Тех.Поддержка</a></b>"""
referal_info = """
💾 Информация 💾\n\nЗа каждую проиграную игру рефералла, вы будете получать 25% от суммы ставки.\n\nНапример: ваш рефералл ставит 10$ и проигрывает, вы получаете 2.50$
"""
main_text = """
👋 <i>Приветствую тебя в нашем казино, мы очень старались и готовили для тебя удобного бота, где ты сможешь расслабиться играя в игры с возможностью умножить или потерять деньги, не стоит казино воспринимать как заработок.</i>

  👀 <blockquote>Наши каналы :</blockquote>
  
 <b><i>@Micecas</i> - Техническая поддержка (которая сможет в любой момент помочь тебе с любым вопросом.)</b>
 <b><i>@MicecasNEWS</i> - Новостной канал (где мы проводим розыгрыши и публикуем новости о боте.)</b>
 <b><i>@MiceCasino</i> - Канал со ставками (где и проходят все ставки и игры.)</b>

👉 <i>Желаем вам удачи в играх, и приятной игры.</i> 👈

💎 <i>С уважением!</i> 💎
<i><b>Команда Mice casino</b></i> 🐭
"""
async def get_admin_menu_text():
    return f"""💸 Админ меню:
<blockquote><b>USDT</b></blockquote>
<b>Доступно:</b> <code>{round(dict(await cryptopay.get_balance())['USDT'], 3)}</code>
<b>В ожидании:</b> <code>{round(dict(await cryptopay.get_hold())['USDT'], 3)}</code>
    """

def get_admin_given(amount, asset):
    return f"""<b>💸 Сумма в размере <i>{amount} {asset}</i> будет зачислена администрацией вручную!</b>

<blockquote><b>"Хорошая ставка — это когда выигрыш вероятнее проигрыша"</b></blockquote>

<b>♠️ Играй заново и испытай свою удачу!</b>"""

def get_button_given(amount, asset):
    return f"""<b>💸 Победитель выиграл <i>{amount} {asset}</i> Заберите выигрыш по кнопке ниже!</b>

<blockquote><b>"Хорошая ставка — это когда выигрыш вероятнее проигрыша"</b></blockquote>

<b>♠️ Играй заново и испытай свою удачу!</b>"""

def get_transfer_given(amount, asset):
    return f"""<b>💸 На баланс победителя была зачислена сумма в размере <i>{amount} {asset}!</i></b>

<blockquote><b>"Хорошая ставка — это когда выигрыш вероятнее проигрыша"</b></blockquote>

<b>♠️ Играй заново и испытай свою удачу!</b>"""

def rnd_id():
    al = string.ascii_letters
    txt = ""
    for i in range(1, 10):
        txt += random.choice(al)
    return txt

def get_stake(amount, asset, comment, name):
    return f"""<blockquote><b>[ 🎉 New Bet! ]</b></blockquote>
    
<b>Mice Casino !</b>
<blockquote><b>👤 Игрок: {name}</b>
<b>🚀 Ставит на: {comment}</b>
<b>💸 Сумма ставки: {round(amount, 3)} {asset}</b></blockquote>

<b><i>Желаем удачи!</i></b>""" + f"\n\n{links}"

def get_win_text(amount, asset, type, additional_comment = None, is_less_dol = False, is_less = False):
    if type != 'def':
        start = "<b>" + additional_comment + "</b>"
    else:
        start = f"<b>🎉 Победа! Ваша ставка оказалась выигрышной!</b>"
    if is_less:
        return start + "\n\n" + get_admin_given(amount, asset) + f"\n\n{links}"
    
    if is_less_dol:
        return start + "\n\n" + get_button_given(amount, asset) + f"\n\n{links}"
    else:
        return start + "\n\n" + get_transfer_given(amount, asset) + f"\n\n{links}"
    
def get_lose_text(additional_comment, type):
    if type != 'def':
        start = "<b>" + additional_comment + "</b>" + "\n\n" + "<b>♠️ Играй заново и испытай свою удачу!</b>" + f"\n\n{links}" 
        return start
    return f"""<b>😕 Проигрыш! Ваша ставка оказалась проигрышной!.

♠️ Играй заново и испытай свою удачу!</b>""" + f"\n\n{links}"

def get_invalid_text(name, type = 'default'):
    if type == 'admin': addiction = "🚀 Возврат денежных средств будет выполнен администрацией вручную."
    elif type == "button": addiction = "💸 Заберите деньги по кнопке ниже."
    else: addiction = "Был совершён возврат денежных средств."
    return f"""<b>[❌] Ошибка!</b>

<b>{name} - Вы</b> забыли дописать комментарий к оплате или ошиблись при его написании.
<i><b><u>{addiction}</u></b></i>

💸 Комиссия составляет: <blockquote>10%.</blockquote>
""" + f"\n\n{links}"

def get_bowling_text(v):
    if v == 6: return "боулинг страйк"
    elif v == 5: return "боулинг 1"
    elif v == 4: return "боулинг 2"
    elif v == 3: return "боулинг 3"
    elif v == 2: return "боулинг 5"
    elif v == 1: return "боулинг 6"

def get_profile(id, name):
    return f"""<b>🐭 Mice CASINO 🐭
👨‍💻Личный кабинет:</b>

<b>👤 UN:</b><i> @{name}</i>
<code><u>Баланс: {"{:.2f}".format(main.db.get_balance(id) if main.db.get_balance(id) != None else 0)}$</u></code>
<blockquote>
<b>💳 ID:</b><i> <code>{id}</code></i>
<b>🎰 Выигрышей</b><i>: {main.db.get_win(id) if main.db.get_win(id) != None else 0}</i>
<b>❌ Поражений</b><i>: {main.db.get_lose(id) if main.db.get_lose(id) != None else 0}</i>
<b>💸 Максимальный выигрыш</b><i>: {"{:.2f}".format(main.db.get_maxwin(id) if main.db.get_maxwin(id) != None else 0)}$</i>
<b>💰 Оборот</b><i>: {"{:.2f}".format(main.db.get_oborot(id) if main.db.get_oborot(id) != None else 0)}$</i>
<b>🗓️ Оборот за месяц</b><i>: {"{:.2f}".format(main.db.get_oborot_month(id) if main.db.get_oborot_month(id) != None else 0)}</i>$
<b>🪙 Всего игр</b><i>: {main.db.get_total(id) if main.db.get_total(id) != None else 0}</i></blockquote>"""
def get_referal(id, money, referals, referer, link):
    return f"""<b>🐭 Mice CASINO 🐭
🫂Реферальная система:</b>

<blockquote><b>🧾 ID: </b> <code>{id}</code>
<b>💸 Реферальный баланс:</b> <code>{"{:.2f}".format(money)}$</code>
<b>👤 Всего рефералов</b>: <code>{referals}</code>
<b>🥷 Реферер</b>: <code>{referer}</code>
</blockquote>
<b>🔗 Ссылка</b>: <code>{link}</code>
"""