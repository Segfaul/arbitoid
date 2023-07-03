import json
import inspect
from random import choice
from concurrent.futures import ThreadPoolExecutor

import requests


class CoinGeckoAPI:

    def __init__(self, link: str, network_fees: dict, market_fees: dict, headers: dict = None, proxy: dict = None,
                 logger=None):
        self.link = link
        self.headers = headers
        self.proxy = proxy

        # all network fees were represented in percentage form except TRC20 cuz it provides usually a 1$ fee withdrawals
        # Data was collected from ---> https://ycharts.com/indicators/
        self.network_fees = network_fees

        # all these fees contain percentage for withdraw(32 fee checks btw)
        self.market_fees = market_fees

        self.logger = logger

    @classmethod
    def get_response(cls, link: str, req_type: str = "GET", data: dict = None,
                     headers: dict = None, proxy: dict = None) -> requests.Request or int:

        if proxy is None:
            proxy = {}

        if headers is None:
            headers = {}

        if data is None:
            data = {}

        try:

            if req_type.upper() == "POST":
                request = requests.post(
                    link, params=data,
                    headers={'user-agent': choice(headers['user_agents'])} if headers else {}, proxies=proxy
                )

            elif req_type.upper() == "PUT":
                request = requests.put(
                    link, params=data,
                    headers={'user-agent': choice(headers['user_agents'])} if headers else {}, proxies=proxy
                )

            else:
                request = requests.get(
                    link,
                    headers={'user-agent': choice(headers['user_agents'])} if headers else {}, proxies=proxy
                )

            if request.status_code != 200:
                return -1

            return request

        except requests.exceptions.RequestException as error:
            return -1

    '''             
    ----------------------------------------------
                    Client logic             
    ----------------------------------------------
    '''

    def get_coin_link(self, coin: str) -> str:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = self.link
            link_to_parse = link_to_parse.replace("___", coin)

            return link_to_parse

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return ''

        finally:
            self.logger.info(f"{func_name}/{coin}") if self.logger else 0

    def get_network(self, coin: str or dict = None) -> tuple:
        func_name = inspect.currentframe().f_code.co_name

        try:

            if type(coin) == str:
                link_to_parse = self.get_coin_link(coin)
                response = self.get_response(link=link_to_parse, headers=self.headers, proxy=self.proxy)
                networks = list(json.loads(response.content)['platforms'].keys())

            else:
                networks = list(coin['platforms'].keys())

            # Firstly, we check transaction free networks. If it doesn't exist, we check 1$ TRC20. If not, return ERC-20

            available_networks = dict(sorted({
                key: self.network_fees[key] for key in (set(networks) & set(self.network_fees.keys()))
            }.items(), key=lambda x: x[1][-1]))

            return list(available_networks.items())[0] if available_networks \
                else ('ethereum', self.network_fees['ethereum'])

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return ()

        finally:
            self.logger.info(f"{func_name}/{coin}") if self.logger else 0

    def global_volume(self, coin: str or dict = None) -> float:
        # Had to use the same function here because of too long answer from CoinGecko server on basic request
        func_name = inspect.currentframe().f_code.co_name

        try:

            if type(coin) == str:
                link_to_parse = self.get_coin_link(coin)
                response = self.get_response(link=link_to_parse, headers=self.headers, proxy=self.proxy)
                volume = json.loads(response.content)['market_data']['total_volume']['usd']

            else:
                volume = coin['market_data']['total_volume']['usd']

            return volume
        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return -1

        finally:
            self.logger.info(f"{func_name}/{coin}") if self.logger else 0

    @classmethod
    def sel_sort(cls, array: [dict]) -> list:
        for i in range(len(array) - 1):
            m = i
            j = i + 1
            while j < len(array):
                if float(array[j]["converted_last"]["usd"]) < float(array[m]["converted_last"]["usd"]):
                    m = j
                j = j + 1
            array[i], array[m] = array[m], array[i]

        if array[0]['market']["name"] == array[-1]['market']["name"]:
            c = -1
            while array[0]['market']["name"] == array[c]['market']["name"]:
                c -= 1
            return [array[0], array[c]]
        return [array[0], array[-1]]

    def gecko_pairs(self, coin: str) -> list:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = self.get_coin_link(coin)
            response = self.get_response(link=link_to_parse, headers=self.headers, proxy=self.proxy)

            coin_stats = json.loads(response.content)
            r2_parse = []

            gl_volume = self.global_volume(coin_stats)
            network = self.get_network(coin_stats)

            for market in coin_stats['tickers']:
                if round(float(market["converted_volume"]["usd"]) / (gl_volume / 100), 2) >= 1 and \
                        market["trust_score"] == "green" and market['market']["name"] in self.market_fees.keys():
                    r2_parse.append(market)

            if len(r2_parse) > 2:
                case = self.sel_sort(r2_parse)
                market_fees = {
                    market_fee['market']['name']: self.market_fees[market_fee['market']['name']]
                    for market_fee in case
                }
                case.append(market_fees)
                case.append(network)
                return case

            else:
                return []

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return []

        finally:
            self.logger.info(f"{func_name}/{coin}") if self.logger else 0

    '''             
    ----------------------------------------------
                    Parser logic             
    ----------------------------------------------
    '''

    def input_loc(self, array: list, page: int) -> None:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"https://api.coingecko.com/api/v3/coins/markets" \
                            f"?vs_currency=usd&order=market_cap_desc&page={page}"
            response = self.get_response(link=link_to_parse, headers=self.headers, proxy=self.proxy)

            loc = json.loads(response.content)

            for coin in loc:
                array.append(coin["id"])

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

        finally:
            self.logger.info(f"{func_name}/{array}/{page}") if self.logger else 0

    def gecko_loc(self, pages: int = 2) -> list:
        func_name = inspect.currentframe().f_code.co_name

        try:
            r2_u = []
            for page in range(1, pages + 1):
                with ThreadPoolExecutor() as executor:
                    executor.submit(self.input_loc, r2_u, page)

            return r2_u

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

        finally:
            self.logger.info(f"{func_name}/{pages}") if self.logger else 0


class ArbitoidAPI:

    def __init__(self, api_link: dict, logger=None):
        self.api_link = f"{api_link['protocol']}{api_link['ip']}:{api_link['port']}"
        self.logger = logger

    @classmethod
    def profit_between_markets(cls, market_buy_name: str, market_buy_price: float,
                               market_sell_name: str, market_sell_price: float,
                               network_fees: list, market_fees: dict, amount: float = 1000.0) -> list or int:
        try:

            if market_buy_name not in market_fees.keys():
                market_fees[market_buy_name] = 0.1
            if market_sell_name not in market_fees.keys():
                market_fees[market_sell_name] = 0.1

            # unnecessary to try if the parameter below is less than 10%
            profit_without_fees = round(
                (market_buy_price - market_sell_price) / ((market_buy_price + market_sell_price) / 2) * -100,
                2)
            # therefore we diversify our final profit according to max and min commission % for withdrawals
            coins_received = (amount - (amount * (market_fees[market_buy_name] / 100))) / market_buy_price

            coins_withdrawn_max = coins_received - (min(network_fees) / 100) * coins_received
            coins_withdrawn_min = coins_received - (max(network_fees) / 100) * coins_received

            sell_coins_max = (coins_withdrawn_max * market_sell_price) - (
                    coins_withdrawn_max * (market_fees[market_sell_name] / 100))
            sell_coins_min = (coins_withdrawn_min * market_sell_price) - (
                    coins_withdrawn_min * (market_fees[market_sell_name] / 100))

            coins_to_wallet_max = sell_coins_max - (min(network_fees) / 100) * sell_coins_max
            coins_to_wallet_min = sell_coins_min - (max(network_fees) / 100) * sell_coins_min

            profit_with_fees_max = round(((coins_to_wallet_max - amount) / ((coins_to_wallet_max + amount) / 2)),
                                         2) * 100
            profit_with_fees_min = round(((coins_to_wallet_min - amount) / ((coins_to_wallet_min + amount) / 2)),
                                         2) * 100

            # all the data is sent back in percentage equivalent
            return [profit_without_fees, profit_with_fees_min, profit_with_fees_max]

        except Exception as error:
            return -1

    @classmethod
    def reform_float(cls, number) -> float:
        try:
            # 'e' sign on exist because it tells how much the number is divided by (if e**(-6) -> num/10**6)
            if 'e' in str(number):
                multiplier = int(str(number)[str(number).index('e') + 1::]) * -1
                corrected_value = round(number * (10 ** (multiplier - 2)), 11)
                return corrected_value
            else:
                return number

        except Exception as error:
            return number

    '''             
    ----------------------------------------------
                   Client logic             
    ----------------------------------------------
    '''

    def gecko_pairs(self, coin: str) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/arbitoid/{func_name}/{coin}"
            response = CoinGeckoAPI.get_response(link_to_parse)

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}") if self.logger else 0

    '''             
    ----------------------------------------------
                   Database logic             
    ----------------------------------------------
    '''

    @property
    def get_stats(self) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(link_to_parse)

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}") if self.logger else 0

    @property
    def get_ready_users(self) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(link_to_parse)

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}") if self.logger else 0

    @property
    def get_admins(self) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(link_to_parse)

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}") if self.logger else 0

    def get_user(self, tg_id: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}/{tg_id}"
            response = CoinGeckoAPI.get_response(link_to_parse)

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

    def check_sub(self, tg_id: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}/{tg_id}"
            response = CoinGeckoAPI.get_response(link_to_parse)

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

    def resize_percent(self, tg_id: int, percent: float) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="PUT", data={"tg_id": tg_id, "percent": percent}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}/{percent}") if self.logger else 0

    def add_req(self, tg_id: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="PUT", data={"tg_id": tg_id}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

    def remove_req(self, tg_id: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="POST", data={"tg_id": tg_id}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

    def reset_req(self) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="POST"
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}") if self.logger else 0

    def add_sub(self, tg_id: int, np: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="POST", data={"tg_id": tg_id, "np": np}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}/{np}") if self.logger else 0

    def add_admin(self, tg_id: int, np: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="POST", data={"tg_id": tg_id, "np": np}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}/{np}") if self.logger else 0

    def input_user(self, tg_id: int, username: str = None) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="POST", data={"tg_id": tg_id, "username": username}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0

    def switch_status(self, tg_id: int) -> dict:
        func_name = inspect.currentframe().f_code.co_name

        try:
            link_to_parse = f"{self.api_link}/user/{func_name}"
            response = CoinGeckoAPI.get_response(
                link_to_parse, req_type="POST", data={"tg_id": tg_id}
            )

            json_response = json.loads(response.content)

            return json_response

        except Exception as error:
            self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0
            return {}

        finally:
            self.logger.info(f"{func_name}/{tg_id}") if self.logger else 0
