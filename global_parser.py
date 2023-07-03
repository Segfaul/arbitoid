import time
import json
import inspect
import logging
from concurrent.futures.thread import ThreadPoolExecutor

from telebot import TeleBot
import aiogram.utils.markdown as md

from parse import CoinGeckoAPI, ArbitoidAPI


def main():
    func_name = inspect.currentframe().f_code.co_name

    try:
        logger = logging.getLogger("Global_Parser")
        logger.setLevel(logging.ERROR)
        file_handler = logging.FileHandler('arbitoid.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        cfg = json.load(open('cfg.json', 'r'))

        gecko_api = CoinGeckoAPI(
            cfg['CoinGecko']['link'], cfg['CoinGecko']['network_fees'], cfg['CoinGecko']['market_fees'],
            cfg['parse']['headers'], {"https": f"http://{cfg['parse']['proxy']['proxy1']}"}, logger
        )

        tele_bot = TeleBot(cfg['telegram']['bot']['api_token'])

        arbitoid = ArbitoidAPI(cfg['FastAPI']['params'], logger)

        parser_top_coins(arbitoid, gecko_api, tele_bot, logger)

    except Exception as error:
        logging.error(f"{func_name}/{error.__class__}||{error.args[0]}")
        quit()


def parser_top_coins(arbitoid: ArbitoidAPI, gecko_api: CoinGeckoAPI, tele_bot: TeleBot, logger=None):
    func_name = inspect.currentframe().f_code.co_name

    try:
        loc = gecko_api.gecko_loc(2)

        for step in range(0, len(loc), 10):
            time.sleep(90)
            for coin in loc[step:step + 10]:
                with ThreadPoolExecutor() as executor:
                    executor.submit(announce, arbitoid, gecko_api, tele_bot, coin, logger)

    except Exception as error:
        logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if logger else 0
        return ''

    finally:
        logger.info(f"{func_name}") if logger else 0


def announce(arbitoid: ArbitoidAPI, gecko_api: CoinGeckoAPI, tele_bot: TeleBot, coin: str, logger=None):
    func_name = inspect.currentframe().f_code.co_name

    try:
        arb_case = gecko_api.gecko_pairs(coin)

        if len(arb_case) == 4:
            market_buy, buy_price, link_buy = \
                arb_case[0]['market']['name'], arb_case[0]['converted_last']['usd'], arb_case[0]['trade_url']
            market_sell, sell_price, link_sell = \
                arb_case[1]['market']['name'], arb_case[1]['converted_last']['usd'], arb_case[1]['trade_url']
            network, market_fees = arb_case[-1], arb_case[2]
            total_profit = arbitoid.profit_between_markets(
                market_buy, arbitoid.reform_float(buy_price),
                market_sell, arbitoid.reform_float(sell_price),
                network[-1], market_fees
            )

            ready_users = arbitoid.get_ready_users['Response']

            for user in ready_users:

                if (user['percent'] and total_profit[0] >= user['percent']) or \
                        (user['percent'] is None and total_profit[0] >= 3.5):
                    try:
                        tele_bot.send_message(
                            user['id'],
                            md.text(
                                f"FOUND ARBITRAGE CASE\n"
                                f"⸻⸻⸻⸻⸻⸻⸻\n\n"
                                + md.hitalic("Link to check: ") +
                                f"https://www.coingecko.com/en/coins/{coin.lower()}#markets" + ' &#9989'
                                + '\n\n' + "Parameters &#128229/&#128228\n"
                                + '├Market to buy: ' + md.hbold(market_buy)
                                + '\n├Market link: \n'
                                + link_buy[:link_buy.index('?') if '?' in link_buy else len(link_buy)]
                                + "\n├Price to buy: " + md.hitalic(buy_price)
                                + '\n├\n├Market to sell: ' + md.hbold(market_sell)
                                + '\n├Market link: \n'
                                + link_sell[:link_sell.index('?') if '?' in link_sell else len(link_sell)]
                                + '\n├Price to sell: ' + md.hitalic(sell_price)
                                + '\n\nTotal profit &#128184' + "\n├Without fees: " + md.hcode(total_profit[0])
                                + "\n├Minimal profit: " + md.hcode(total_profit[1])
                                + "\n├Maximum profit: " + md.hcode(total_profit[-1])
                                + "\nNetwork: " + md.hbold(network[0])
                                + "\nFinal result might be lower according to network fees"
                                + "\n\nData collected by " + "@Arbitroid_bot",
                                sep='\n',
                            ),
                            parse_mode='html',
                            disable_web_page_preview=True
                        )

                    except Exception as error:
                        logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}") if logger else 0

                    finally:
                        logger.info(f"{func_name}") if logger else 0

    except Exception as error:
        logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if logger else 0

    finally:
        logger.info(f"{func_name}") if logger else 0


if __name__ == '__main__':
    main()
