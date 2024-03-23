from aiogram.filters import Command, StateFilter
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from Bot.models import main_models
from Bot.charts import get_company_info, get_data, plot_total_data, plot_candelstick_chart
from Bot.keyboards.for_questions import get_company
from Bot.handlers.main_state import GetInfo
from Bot.handlers.company_name import cmd_save_company_name
import os

import re

router = Router()

from aiogram.types.input_file import InputFile
from PIL import Image
import io

def convert_to_grayscale(image_path="ozon.png"):
    img = Image.open(image_path).convert('L')

    buf = io.BytesIO()
    img.save(buf, format='png')
    buf.seek(0)
    return buf


@router.message(StateFilter(None), Command("prediction"))
async def cmd_prediction(message: Message, state: FSMContext):
    data = await state.get_data()

    company_name = data['company_name']
    await message.answer('Гадание займет какое-то время🪄 Подожди немного!')

    pred = main_models(company_name)

    sign = -1 if pred < 0 else 1
    m = 'упадет' if pred < 0 else 'вырастет'

    company_info = get_company_info(company_name=company_name, param_info='total')
    fullname = company_info['shortName']
    currency = company_info['financialCurrency']

    mess = [
      f'Стоимость акции компании {fullname} {m} на {round(pred[0], 2) * sign} {currency}.\n',
        'Но помни, я всего лишь котик с лапками. Не все мои прогнозы точны.'
    ]
    await message.answer(''.join(mess),
                         reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(None), Command("recommendation"))
async def cmd_recommendation(message: Message, state: FSMContext):
    data = await state.get_data()

    company_name = data['company_name']
    await message.answer('Гадание займет какое-то время🪄 Подожди немного!')

    company_info = get_company_info(company_name=company_name, param_info='total')

    rec = 'купи больше акций, дружочек. ' if company_info[
                'recommendationKey'] == 'buy' else 'продавай акции, дружочек. Сейчас самое время.'

    mess = [f'Моя рекомендация - {rec}\n',
            'Но помни, я всего лишь котик с лапками. Не все мои прогнозы точны.']

    await message.answer(''.join(mess),
                         reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(None), Command("news"))
async def cmd_news(message: Message, state: FSMContext):
    data = await state.get_data()

    company_name = data['company_name']
    await message.answer('Поиск займет какое-то время🪄 Подожди немного!')

    news = get_company_info(company_name=company_name, param_info='news')

    mess = ''

    for n in news:
        mess += 'Издание: ' + n['publisher'] + '\n'
        mess += 'Название статьи: ' + n['title'] + '\n'
        mess += 'Ссылка: ' + n['link'] + '\n'

    await message.answer(''.join(mess),
                         reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(None), Command("clear_company"))
async def cmd_clear_company(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Какая компания тебя интересует?',
                         reply_markup=get_company())
    await state.set_state(GetInfo.waiting_for_company_name)
    await cmd_save_company_name(message, state)


@router.message(StateFilter(None), Command("dynamics_chart", "candlestick_chart"))
async def cmd_get_period(message: Message, state: FSMContext):
    await state.update_data(command=message.text)

    mess = [
        'За какой период ты хочешь посмотреть динамику\? :з\n',
        'Но у меня есть просьба\: введи период в формате \- `"c XXXX-XX-XX по XXXX-XX-XX"`\.\n',
        'Пока я понимаю только такой формат\, но это временно и совсем скоро я буду уметь еще больше\!'
    ]
    await message.answer(''.join(mess),
                         parse_mode=ParseMode.MARKDOWN_V2,
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(GetInfo.waiting_for_period)


def get_picture(start, end, company_name, file_path, plot='total'):

    hist = get_data(company_name, start=start, end=end)
    if plot == 'total':
        plot_total_data(hist)
    else:
        plot_candelstick_chart(hist)

    return os.path.exists(file_path)


@router.message(StateFilter(GetInfo.waiting_for_period))
async def cmd_dynamics_chart(message: Message, state: FSMContext):

    mess = message.text

    data = await state.get_data()
    company_name = data['company_name']
    file_path = './handlers/pics/'
    command = data['command']

    file_path += 'total_data.png' if command == '/dynamics_chart' else 'candelstick_data.png'
    plot_param = 'total' if command == '/dynamics_chart' else 'candelstick'

    path = re.compile('\d{4}-\d{2}-\d{2}')

    dates = re.findall(path, mess)

    if len(dates) == 2:
        start, end = dates[0], dates[1]
        plot_flag = get_picture(start, end, company_name, file_path, plot=plot_param)
        company_info = get_company_info(company_name=company_name, param_info='total')
        fullname = company_info['shortName']
        if plot_flag:

            await message.answer_photo(photo=FSInputFile(path=file_path),
                                       caption=f"Изменение стоимости акций компании {fullname} в динамике")

        else:
            await message.answer('Извини, у меня не получилось построить график. Попробуй еще раз.')

        await state.set_state(None)
    else:
        await message.answer('Извини, не смог разобрать твое сообщение. Попробуй ввести период еще раз.')


@router.message(StateFilter(None), Command("end_conversation"))
async def cmd_end_conversation(message: Message, state: FSMContext):
    await message.reply('Если что, обращайся!')
    await state.clear()

