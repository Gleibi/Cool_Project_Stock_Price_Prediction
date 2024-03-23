from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from Bot.keyboards.for_questions import get_company


class GetInfo(StatesGroup):
    waiting_for_company_name = State()
    waiting_for_other_company_name = State()
    waiting_for_period = State()


router = Router()


@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    name = message.from_user.first_name

    mess = [
        f'Привет\, {name}\! Я \- Stock Wizard 🔮\.',
        'Умею гадать на кофейной гуще\. Люблю читать новости на YahooFinance\.',
        'В последнее время решил совместить приятное с полезным\.',
        'Теперь любой может получить прогноз и рекомендацию относительно акций зарубежных компаний\.'
        '\nКакая компания тебя интересует\?'
    ]

    await message.answer('\n'.join(mess),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_company())
    await state.set_state(GetInfo.waiting_for_company_name)
