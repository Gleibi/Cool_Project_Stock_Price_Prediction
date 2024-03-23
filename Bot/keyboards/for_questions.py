from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardMarkup


# def get_chart_or_pred() -> InlineKeyboardMarkup:
#     kb = ReplyKeyboardBuilder()
#     kb.button(text="Хочу посмотреть стоимость в динамике!")
#     kb.button(text="Хочу получить предсказание!")
#     kb.adjust(2)
#     return kb.as_markup(resize_keyboard=True)


def get_company() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Apple")
    kb.button(text="Tesla")
    kb.button(text="Netflix")
    kb.button(text="Amazon")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
