import json
import logging
import asyncio
import inspect

from tg_bot import TelegramBot
from parse import ArbitoidAPI


async def main() -> None:
    func_name = inspect.currentframe().f_code.co_name

    try:
        logger = logging.getLogger("BusinessLogic")
        logger.setLevel(logging.ERROR)
        file_handler = logging.FileHandler('arbitoid.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        cfg = json.load(open('cfg.json', 'r'))
        arbitoid = ArbitoidAPI(cfg['FastAPI']['params'], logger)

        aio_bot = TelegramBot(cfg['telegram']['bot']['api_token'], arbitoid, logger)
        await aio_bot.dp.skip_updates()

        tasks = [
            asyncio.create_task(aio_bot.dp.start_polling()),
            asyncio.create_task(update_req(arbitoid, 60, logger))
        ]

        await asyncio.gather(*tasks)

    except Exception as error:
        logging.error(f"{func_name}/{error.__class__}||{error.args[0]}")
        quit()


async def update_req(arbitoid: ArbitoidAPI, interval: int = 60, logger=None):
    func_name = inspect.currentframe().f_code.co_name

    try:
        while 1:
            await asyncio.sleep(interval)
            arbitoid.reset_req()

    except Exception as error:
        logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if logger else 0
        return ''

    finally:
        logger.info(f"{func_name}") if logger else 0


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())

    finally:
        loop.close()
