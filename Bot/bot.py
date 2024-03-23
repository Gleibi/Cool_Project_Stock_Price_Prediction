import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from Bot.handlers import main_state, company_name, routes

from config_reader import config

async def main():

    # Объект бота
    bot = Bot(token=config.bot_token.get_secret_value())
    # Диспетчер
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(main_state.router)
    main_state.router.include_router(company_name.router)
    company_name.router.include_router(routes.router)
    # company_name.router.include_router(prediction_state.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
