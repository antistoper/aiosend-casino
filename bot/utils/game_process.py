from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import types

from settings import coefs
from bot.utils import func, text
import asyncio, random
import config
import random

class GameProcess:
    def __init__(self, amount, asset, coef, user_id, username, name = "antistoper") -> None:
        self.amount = amount
        self.asset = asset
        self.coef = coef
        self.id = user_id
        self.username = username
        self.name = name

    async def basketball_process(self, message: Message, type = "goal"):
        msg = await message.answer_dice('🏀')
        await asyncio.sleep(4)
        v=msg.dice.value
        if type == "goal":
            if v==4 or v==5:
                self.coef += coefs.BASKET
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "баскетбол попал")
            else:
                await func.looser(message, "баскетбол не попал", amount=self.amount, user_id=self.id,)
        else:
            self.coef += coefs.BASKET_MISS
            if v==3 or v==1 or v==2:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "баскетбол не попал")
            else:
                await func.looser(message, "баскетбол попал", amount=self.amount, user_id=self.id, name = self.name)
    
    async def footaball_process(self, message: Message, type = "goal"):
        msg = await message.answer_dice('⚽')
        await asyncio.sleep(5)
        v=msg.dice.value
        if type == "goal":
            self.coef += coefs.FOOTBALL
            if v==4 or v==5 or v==3:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "футбол попал")
            else:
                await func.looser(message, "футбол не попал", amount=self.amount, user_id=self.id, name = self.name)
        else:
            self.coef += coefs.FOOTBALL_MISS
            if v==1 or v==2:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "футбол попал")
            else:
                await func.looser(message, "футбол не попал", amount=self.amount, user_id=self.id, name = self.name)

    async def darts_procces(self, message: Message, type = 'center'):
        msg = await message.answer_dice('🎯')
        await asyncio.sleep(4)
        v=msg.dice.value
        if type == "w":
            self.coef += coefs.DARTS_COLOR
            if v==3 or v==5:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "дартс белое")
            elif v == 6:
                await func.looser(message, "дартс центр", amount=self.amount, user_id=self.id, name = self.name)
            elif v == 1:
                await func.looser(message, "дартс мимо", amount=self.amount, user_id=self.id, name = self.name)
            else:
                await func.looser(message, "дартс красное", amount=self.amount, user_id=self.id, name = self.name)
        elif type == "r":
            self.coef += coefs.DARTS_COLOR
            if v==4 or v==2:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "дартс красное")
            elif v == 6:
                await func.looser(message, "дартс центр", amount=self.amount, user_id=self.id, name = self.name)
            elif v == 1:
                await func.looser(message, "дартс мимо", amount=self.amount, user_id=self.id, name = self.name)
            else:
                await func.looser(message, "дартс белое", amount=self.amount, user_id=self.id, name = self.name)
        elif type == "miss":
            self.coef += coefs.DARTS
            if v == 1:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "дартс мимо")
            elif v==3 or v==5:
                await func.looser(message, "дартс белое", amount=self.amount, user_id=self.id, name = self.name,)
            elif v==4 or v==2:
                await func.looser(message, "дартс красное", amount=self.amount, user_id=self.id, name = self.name)
            else:
                await func.looser(message, "дартс центр", amount=self.amount, user_id=self.id, name = self.name)
        else:
            self.coef += coefs.DARTS
            if v==6:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, "дартс центр")
            elif v==3 or v==5:
                await func.looser(message, "дартс белое", amount=self.amount, user_id=self.id, name = self.name)
            elif v==4 or v==2:
                await func.looser(message, "дартс красное", amount=self.amount, user_id=self.id, name = self.name)
            elif v == 1:
                await func.looser(message, "дартс мимо", amount=self.amount, user_id=self.id, name = self.name)

    async def dice_procces(self, message: Message, type, n = None):
        await asyncio.sleep(1)
        msg = await message.answer_dice("🎲")
        v = msg.dice.value
        await asyncio.sleep(6)
        if type == "number":
            self.coef += coefs.DICE_NUMBER
            if n == v:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, f"❤️‍🩹 | Вы победили! Выпало число {v}.", photo="dice_guesed.jpg", type='c')
            else:
                await func.looser(message, f"Проигрыш! Выпало число {v}. Вы не угадали!", amount=self.amount, user_id=self.id, name = self.name, photo="lose.jpg", type='c')
        elif type == "even":
            self.coef += coefs.DICE
            if v == 2 or v == 4 or v==6:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, f"️‍❤️‍🩹 | Вы победили! Выпало число {v}.", photo="win.jpg", type='c')
            else:
                await func.looser(message, f"Проигрыш! Выпало число {v}.", amount=self.amount, user_id=self.id, name = self.name, photo="lose.jpg", type='c')
        elif type == "odd":
            self.coef += coefs.DICE
            if v == 1 or v == 3 or v==5:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name, f"❤️‍🩹 | Вы победили! Выпало число {v}.", photo="win.jpg", type='c')
            else:
                await func.looser(message, f"Проигрыш! Выпало число {v}.", amount=self.amount, user_id=self.id,name = self.name, photo="lose.jpg", type='c')
        elif type == "more":
            self.coef += coefs.DICE_MORE_LESS
            if v == 4 or v == 5 or v==6:
                await func.winner(message,  self.amount, self.asset, self.coef, self.id, self.username,self.name, f"❤️‍🩹 | Вы победили! Выпало число {v}.", photo="win.jpg", type='c')
            else:
                await func.looser(message, f"Проигрыш! Выпало число {v}.", amount=self.amount, user_id=self.id,name = self.name, photo="lose.jpg", type='c')
        elif type == "less":
            self.coef += coefs.DICE_MORE_LESS
            if v == 1 or v == 2 or v==3:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, f"❤️‍🩹 | Вы победили! Выпало число {v}.", photo="win.jpg", type='c')
            else:
                await func.looser(message, f"Проигрыш! Выпало число {v}.", amount=self.amount, user_id=self.id,name = self.name, photo="lose.jpg", type='c')
        elif type == "sector":
            self.coef += coefs.DICE_SECTOR
            if n == 1: right_nums = [1, 2]
            elif n == 2: right_nums = [3, 4]
            else: right_nums = [5, 6]

            if v in right_nums:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, f"❤️‍🩹 | Вы победили! Выпало число {v}.", photo="win.jpg", type='c')
            else:
                await func.looser(message, f"Проигрыш! Выпало число {v} которое не попадает в сектор {n}.", amount=self.amount,name = self.name, user_id=self.id, photo="lose.jpg", type='c')


    async def duel_number_process(self, message: Message, num, game = '🎲', textes = ["Победа 1", "Победа 2"]):
        self.coef += coefs.DUEL
        while True:
            cub1 = await message.answer_dice(game)
            cub2 = await message.answer_dice(game)
            if num == 1: 
                msguser = cub1
                msgbot = cub2
            else:
                msguser = cub2
                msgbot = cub1
            await asyncio.sleep(4)
            if msguser.dice.value > msgbot.dice.value:
                if num == 1:
                    photo = 'win.jpg' if game == '🎲' else "win.jpg"
                    await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, f"❤️‍🩹 | Вы победили! Игра прошла со счётом [{msguser.dice.value}:{msgbot.dice.value}] в пользу {textes[0]}.", photo, 'c')
                else:
                    photo = 'win.jpg' if game == '🎲' else "win.jpg"
                    await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, f"❤️‍🩹 | Вы победили! Игра прошла со счётом [{msgbot.dice.value}:{msguser.dice.value}] в пользу {textes[1]}.", photo, 'c')
                break
            elif msguser.dice.value == msgbot.dice.value:
                await message.reply("*⚡ Ничья! Играем ещё раз!*", 'markdown')
                await asyncio.sleep(2)
            elif msguser.dice.value < msgbot.dice.value:
                if num == 1:
                    photo = 'lose.jpg' if game == '🎲' else "lose.jpg"
                    await func.looser(message,f"Проигрыш! Игра прошла со счётом [{msguser.dice.value}:{msgbot.dice.value}] в пользу {textes[1]}.", amount=self.amount, user_id=self.id,name = self.name, photo=photo, type='c')
                else:
                    photo = 'lose.jpg' if game == '🎲' else "lose.jpg"
                    await func.looser(message, f"Проигрыш! Игра прошла со счётом [{msgbot.dice.value}:{msguser.dice.value}] в пользу {textes[0]}.", amount=self.amount, user_id=self.id,name = self.name, photo=photo, type='c')
                break
    
    async def duel_proccess(self, message: Message, game = '🎲', textes = ["Победа 1", "Победа 2"], win_photos = ['dice_1.jpg','dice_2.jpg']):
        self.coef += coefs.DUEL
        while True:
            msgbot = await message.answer_dice(game)
            msguser = await message.answer_dice(game)
            await asyncio.sleep(4)
            if msguser.dice.value > msgbot.dice.value:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username, self.name,f"❤️‍🩹 | Вы победили! Игра прошла со счётом [{msgbot.dice.value}:{msguser.dice.value}] в пользу {textes[1]}.", win_photos[1], 'c')
                break
            elif msguser.dice.value == msgbot.dice.value:
                await message.reply("*⚡Ничья! Играем ещё раз!*", 'markdown')
                await asyncio.sleep(2)
            elif msguser.dice.value < msgbot.dice.value:
                await func.looser(message, f"Проигрыш! Игра прошла со счётом [{msgbot.dice.value}:{msguser.dice.value}] в пользу {textes[0]}.", amount=self.amount, user_id=self.id,name = self.name,  photo=win_photos[0], type='c')
                break
    
    async def bowling_process(self, message: Message, stake):
        msg = await message.answer_dice('🎳')
        v=msg.dice.value
        self.coef += coefs.BOWLING
        await asyncio.sleep(5)
        if stake == 0:
            if v==6:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, "боулинг 0")
            else:
                await func.looser(message, text.get_bowling_text(v), amount=self.amount, user_id=self.id,name = self.name,)
        elif stake == 1:
            if v==5:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, "боулинг 1")
            else:
                await func.looser(message, text.get_bowling_text(v), amount=self.amount, user_id=self.id,name = self.name,)
        elif stake == 2:
            if v == 4:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, "боулинг 2")
            else:
                await func.looser(message, text.get_bowling_text(v), amount=self.amount, user_id=self.id,name = self.name,)
        elif stake == 3:
            if v == 3:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, "боулинг 3")
            else:
                await func.looser(message, text.get_bowling_text(v), amount=self.amount, user_id=self.id,name = self.name,)
        elif stake == 5:
            if v == 2:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, "боулинг 5")
            else:
                await func.looser(message, text.get_bowling_text(v), amount=self.amount, user_id=self.id,name = self.name,)
        elif stake == 6:
            if v == 1:
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, "боулинг страйк")
            else:
                await func.looser(message, text.get_bowling_text(v), amount=self.amount, user_id=self.id,name = self.name,)
        
    async def rock_paper_sizer_proccess(self, message: Message, value = 'paper', textes = ["Победа 1", "Победа 2"], win_photos = ['win-rzp.jpg', "win-rzp.jpg"]):
        self.coef += coefs.DUEL
        while True:

            emojis_dict = {
                "paper": "✋",
                "sizer": "✂️",
                "rock": "✊",
            }
            randomized_value = random.choice(["paper", "sizer", "rock"])
            player_value_msg = await message.answer(emojis_dict[value])
            bot_value_msg = await message.answer(emojis_dict[randomized_value])
            await asyncio.sleep(4)

            if value == "paper":
                if randomized_value == "paper": status = "draw"
                elif randomized_value == "rock": status = "win"
                else: status = "lose"

            elif value == "rock":
                if randomized_value == "rock": status = "draw"
                elif randomized_value == "sizer": status = "win"
                else: status = "lose"

            elif value == "sizer":
                if randomized_value == "sizer": status = "draw"
                elif randomized_value == "paper": status = "win"
                else: status = "lose"

            if status == "win":
                await func.winner(message, self.amount, self.asset, self.coef, self.id, self.username,self.name, f"❤️‍🩹 | Вы победили! Игра в пользу игрока.", win_photos[1], 'c')
                break
            elif status == "draw":
                await message.reply("*⚡Ничья! Играем ещё раз!*", 'markdown')
                await asyncio.sleep(2)
            elif status == "lose":
                await func.looser(message, f"Проигрыш! Игра в пользу бота.", amount=self.amount, user_id=self.id,name = self.name,  photo="lose-rzp.jpg", type='c')
                break