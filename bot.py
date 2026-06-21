from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.db.base import engine, init_db, session_factory
from app.handlers import setup_routers
from app.middlewares.db import DbSessionMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.services.seed import seed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("innobot")


async def on_startup() -> None:
    await init_db()
    async with session_factory() as session:
        await seed(session)
    log.info("Startup complete.")


async def on_shutdown(bot: Bot) -> None:
    await bot.session.close()
    await engine.dispose()
    log.info("Shutdown complete.")


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Outer middlewares: DB session is on dp.update so it's available to filters.
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.message.outer_middleware(ThrottlingMiddleware(settings.throttle_rate))
    dp.callback_query.outer_middleware(ThrottlingMiddleware(settings.throttle_rate))

    setup_routers(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Bot starting (long polling)...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
