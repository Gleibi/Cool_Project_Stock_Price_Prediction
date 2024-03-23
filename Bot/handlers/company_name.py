from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from charts import get_data
from keyboards.for_questions import get_company
from handlers.main_state import GetInfo

router = Router()


@router.message(GetInfo.waiting_for_company_name, F.text.in_(['Apple', 'Tesla', 'Netflix', 'Amazon']))
async def cmd_save_company_name(message: Message, state: FSMContext):

    mess = message.text

    d = {'Apple': 'AAPL',
         'Netflix': 'NFLX',
         'Amazon': 'AMZN',
         'Tesla': 'TSLA'}

    company_name = d[mess]

    await state.update_data(company_name=company_name)

    mess = [
        'Спасибо, принял в обработку\!\n',
        'А теперь выбери, что бы ты хотел попробовать\?\n',
        '`/prediction` \- ты получишь магическое предсказание по изменению стоимости акции сегодня',
        '\n`/dynamics_chart` \- ты сможешь посмотреть изменение стоимости акций в динамике',
        '\n`/candlestick_chart` \- ты сможешь посмотреть изменение стоимости акций на японских свечах',
        '\n`/recommendation` \- ты получишь рекомендаю по покупке/продаже акций',
        '\n`/news` \- скину тебе интересные новостные ссылки по интересующей тебя компании',
        '\n`/clear_company` \- на тот случай, если хочешь сменить компанию',
        '\n`/end_conversation` \- если ты устал и хочешь закончить разговор на сегодня'
    ]
    await message.reply(''.join(mess),
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=ReplyKeyboardRemove())

    await state.set_state(None)


@router.message(GetInfo.waiting_for_company_name, ~F.text.in_(['Apple', 'Tesla', 'Netflix', 'Amazon']))
async def cmd_save_other_company_name(message: Message, state: FSMContext):

    mess = [
       'Если хочешь прогноз для другой компании\, введи известное тебе название символа\.',
       'Правильные символы ты можешь найти вот [здесь](https://finance.yahoo.com/)\.'
    ]

    await message.answer('\n'.join(mess),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_company())

    await state.set_state(GetInfo.waiting_for_other_company_name)


@router.message(GetInfo.waiting_for_other_company_name, F.text)
async def cmd_write_other_company_name(message: Message, state: FSMContext):

    company_name = message.text

    d = {'Apple': 'AAPL',
         'Netflix': 'NFLX',
         'Amazon': 'AMZN',
         'Tesla': 'TSLA'}

    if company_name in d.keys():
        company_name = d[company_name]

    await message.reply('Проверяю выбранную компанию!')
    try:
        res = get_data(company_name)

        await state.update_data(company_name=company_name)

        mess = [
            'Спасибо, принял в обработку\!\n',
            'А теперь выбери, что бы ты хотел попробовать\?\n',
            '`/prediction` \- ты получишь магическое предсказание по изменению стоимости акции сегодня',
            '\n`/dynamics_chart` \- ты сможешь посмотреть изменение стоимости акций в динамике',
            '\n`/candlestick_chart` \- ты сможешь посмотреть изменение стоимости акций на японских свечах',
            '\n`/recommendation` \- ты получишь рекомендаю по покупке/продаже акций',
            '\n`/news` \- скину тебе интересные новостные ссылки по интересующей тебя компании',
            '\n`/clear_company` \- на тот случай, если хочешь сменить компанию',
            '\n`/end_conversation` \- если ты устал и хочешь закончить разговор на сегодня'
        ]

        await message.reply(''.join(mess),
                            parse_mode=ParseMode.MARKDOWN_V2,
                            reply_markup=ReplyKeyboardRemove())

        await state.set_state(None)


    except:
        await message.answer(
            "Извини, дружочек. Я не смог ничего найти. Попробуй выбрать один из вариантов ответа.",
            reply_markup=get_company()
        )
