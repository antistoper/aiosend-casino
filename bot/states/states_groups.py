from aiogram.dispatcher.filters.state import State, StatesGroup

class AdminState(StatesGroup):
    add_money = State()
    take_money = State()
    ad = State()
    add_button = State()

class UserState(StatesGroup):
    withdraw = State()

class BalanceBetState(StatesGroup):
    bet = State()
    comment = State()
    finish = State()