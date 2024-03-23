from aiogram.filters.command import Command
from aiogram.enums import ParseMode

from Bot.models import main_models
from Bot.charts import get_company_info

from handlers import routes, chart_state

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):


# @dp.chain_head

@dp.message(Command("get_prediction"))
async def cmd_prediction(message: types.Message):

