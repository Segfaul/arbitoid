import asyncio
import inspect

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as md


class Form(StatesGroup):
    percent = State()
    coin = State()
    sub = State()
    admin = State()
    acc = State()


class TelegramBot:

    def __init__(self, api_token: str, arbitoid, logger=None):
        self.bot = Bot(token=api_token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.logger = logger
        self.arbitoid = arbitoid

        self.handlers()

    @classmethod
    def keyboard(cls, commands: [list]) -> types.ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for row in commands:
            markup.row(
                *list(map(types.KeyboardButton, row))
            )

        return markup

    @classmethod
    def main_menu(cls, user: dict = None) -> list:
        menu = [
            ["🔍 ARBITRAGE"],
            [
                f"💸 {user['percent'] if user and user['percent'] else '3.5'}%",
                f"💡 {'ON' if user and user['status'] else 'OFF'}"
            ],
            ["👤 ACC", "📎 HELP"]
        ]
        return menu

    @classmethod
    def admin_panel(cls) -> list:
        menu = [
            ["🏹 STATS"],
            ["🎫 SUB", "🏆 ADMIN", "👥 ACC"],
            ["⬅ MENU"]
        ]

        return menu

    def handlers(self):

        @self.dp.message_handler(commands=['start'])
        async def commands_start(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:

                if self.arbitoid.input_user(message.from_user.id, message.from_user.username)['Response'] == 0:
                    for admin in self.arbitoid.get_admins['Response']:
                        await self.bot.send_message(admin['id'],
                                                    f"&#128314           "
                                                    f"{md.hitalic('New user')}           "
                                                    f"&#128314\n\nStats:\n"
                                                    f"├{md.hbold('ID')}: {md.hcode(message.from_user.id)}\n"
                                                    f"├{md.hbold('Nick')}: @{message.from_user.username}\n"
                                                    f"├{md.hbold('Is_bot')}: {message.from_user.is_bot}\n"
                                                    f"\nTelegram bot: @Arbitroid_bot",
                                                    parse_mode='html')

                if type(self.arbitoid.check_sub(message.from_user.id)['Response']) == int:
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Welcome, @{message.from_user.username if message.from_user.username else 'user'}\n"
                        f"To gain access to the bot, write ---> @percoit  &#128172",
                        parse_mode='html'
                    )

                else:

                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id,
                        f"Welcome back, @{message.from_user.username if message.from_user.username else 'user'}\n",
                        parse_mode='html',
                        reply_markup=markup
                    )

                await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        '''             
        ----------------------------------------------
                        Client logic             
        ----------------------------------------------
        '''

        @self.dp.message_handler(commands=['account', 'acc', 'акк', 'аккаунт'])
        @self.dp.message_handler(Text(equals=['👤 ACC'], ignore_case=True))
        async def commands_account(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name
            try:
                if type(self.arbitoid.check_sub(message.from_user.id)['Response']) == str:
                    user = self.arbitoid.get_user(message.from_user.id)['Response']

                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id,
                        f"\n&#128221 {md.hbold('Subscription expires on')}: "
                        f"{md.hitalic(user['sub'] if user['sub'] else 'XX-XX-XX')}(Y-M-D)\n"
                        f"\n&#128100My Profile:\n"
                        f"├Requests per minute: {md.hcode(str(user['req_num']) + '/5')}\n"
                        f"├Arbitrage % (min for alert): "
                        f"{md.hcode(str(user['percent']) + '%') if user['percent'] else md.hcode('3.5%')}\n"
                        f"\n&#128276Alerts: {'on' if user['status'] == True else 'off'}",
                        parse_mode='html',
                        reply_markup=markup
                    )
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['help', 'hlp', 'hp', 'поддержка'])
        @self.dp.message_handler(Text(equals=['📎 HELP'], ignore_case=True))
        async def commands_help(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name
            try:
                if type(self.arbitoid.check_sub(message.from_user.id)['Response']) == str:

                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id,
                        f"&#128206Details on each of the commands&#128206\n\n"
                        f"/acc {md.hitalic('- get your bot account details')}\n"
                        f"/pairs {md.hitalic('- get the most profitable arbitrage strategy on a coin')}\n"
                        f"/sw {md.hitalic('- to resume/break connection to the parser notification')}\n"
                        f"/prc {md.hitalic('- % of profit from which notifications will be sent (standard: 3.5)')}\n",
                        parse_mode='html',
                        reply_markup=markup
                    )

                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['status', 'st', 'switch', 'sw', 'change'])
        @self.dp.message_handler(Text(contains=['💡'], ignore_case=True))
        async def commands_status(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if type(self.arbitoid.check_sub(message.from_user.id)['Response']) == str:
                    result = self.arbitoid.switch_status(message.from_user.id)['Response']

                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    if result == 1:
                        await self.bot.send_message(
                            message.from_user.id,
                            f"Alerts {md.hbold('on')}...\n\n"
                            f"As soon as I find a good deal, I'll send a notification&#9203"
                            f"To disable notifications, type &#128073 /sw",
                            parse_mode='html',
                            reply_markup=markup
                        )

                    else:
                        await self.bot.send_message(
                            message.from_user.id,
                            f"Alerts {md.hbold('off')}...\n\n"
                            f"To enable notifications, type &#128073 /sw",
                            parse_mode='html',
                            reply_markup=markup
                        )

                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['percent', '%', 'prc', 'процент'])
        @self.dp.message_handler(Text(contains=['💸'], ignore_case=True))
        async def commands_prc(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if type(self.arbitoid.check_sub(message.from_user.id)['Response']) == str:

                    markup = TelegramBot.keyboard(
                        [
                            ['X']
                        ]
                    )

                    await Form.percent.set()
                    await self.bot.send_message(
                        message.from_user.id,
                        "Enter % of which you'd like to receive arbitrage cases\n"
                        "To cancel, type the command 👉 /cancel",
                        parse_mode='html',
                        reply_markup=markup
                    )

                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(state='*', commands='cancel')
        @self.dp.message_handler(Text(equals=['cancel', 'отмена', '❌', 'X'], ignore_case=True), state='*')
        async def cancel_handler(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            try:

                await message.delete()

                current_state = await state.get_state()
                if current_state is None:
                    return

                if current_state.split(':')[1] in ['percent', 'coin']:
                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                else:
                    markup = TelegramBot.keyboard(self.admin_panel())

                await self.bot.send_message(message.from_user.id, "Input stopped &#128219", parse_mode='html',
                                            reply_markup=markup)

                await self.bot.delete_message(
                    message.from_user.id, message.message_id - 1
                )

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                await state.finish()
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(state=Form.percent)
        async def process_prc(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name
            try:
                async with state.proxy() as data:
                    data['percent'] = message.text

                result = self.arbitoid.resize_percent(message.from_user.id, float(data['percent']))['Response']

                user = self.arbitoid.get_user(message.from_user.id)['Response']
                menu = self.main_menu(user)
                menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                markup = TelegramBot.keyboard(menu)

                if result == 0:

                    await self.bot.send_message(
                        message.from_user.id,
                        md.text(
                            md.text(
                                "Percent updated: " + md.hcode(data['percent'] + '%') + " &#128279"
                            ),
                            sep='\n',
                        ),
                        parse_mode='html',
                        reply_markup=markup
                    )

                else:
                    await self.bot.send_message(
                        message.from_user.id, "Incorrect input &#128219 \n"
                                              "Try again, type the command 👉 /prc", parse_mode='html',
                        reply_markup=markup
                    )

            except Exception as error:
                try:
                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id, "Unexpected error &#128219 \n"
                                              "Try again, type the command 👉 /prc", parse_mode='html',
                        reply_markup=markup
                    )
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                await state.finish()
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['pairs', 'find_pairs', 'market', 'arbitro'])
        @self.dp.message_handler(Text(equals=['🔍 ARBITRAGE'], ignore_case=True))
        async def commands_pairs(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if type(self.arbitoid.check_sub(message.from_user.id)['Response']) == str:

                    user = self.arbitoid.get_user(message.from_user.id)['Response']

                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0

                    if user['req_num'] < 5:
                        markup = TelegramBot.keyboard([["X"]])

                        await Form.coin.set()
                        await self.bot.send_message(
                            message.from_user.id,
                            f"Enter the name of the cryptocurrency ({md.hitalic('bitcoin')})\n"
                            f"{md.hitalic('*check the correctness with the id on ')}"
                            f"{md.hlink('CoinGecko', 'https://www.coingecko.com/')}\n\n"
                            "To cancel, type the command 👉 /cancel",
                            disable_web_page_preview=True,
                            parse_mode='html',
                            reply_markup=markup
                        )

                    else:
                        markup = TelegramBot.keyboard(menu)

                        await self.bot.send_message(
                            message.from_user.id,
                            f"You have reached the request limit ({md.hcode(str(user['req_num']) + '/5')} per 1m)\n"
                            "Try again later type the command 👉 /pairs",
                            parse_mode='html',
                            reply_markup=markup
                        )

                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(state=Form.coin)
        async def process_pairs(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name
            try:
                async with state.proxy() as data:
                    data['coin'] = message.text.lower()

                result = self.arbitoid.gecko_pairs(data['coin'])['Response']
                self.arbitoid.add_req(message.from_user.id)

                user = self.arbitoid.get_user(message.from_user.id)['Response']
                menu = self.main_menu(user)
                menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                markup = TelegramBot.keyboard(menu)

                if result:
                    f = await self.bot.send_message(
                        message.from_user.id,
                        "Initialized the analysis of the selected coin...  &#8987",
                        parse_mode='html'
                    )

                    market_buy, buy_price, link_buy = \
                        result[0]['market']['name'], result[0]['converted_last']['usd'], result[0]['trade_url']
                    market_sell, sell_price, link_sell = \
                        result[1]['market']['name'], result[1]['converted_last']['usd'], result[1]['trade_url']
                    network, market_fees = result[-1], result[2]

                    total_profit = self.arbitoid.profit_between_markets(
                        market_buy, self.arbitoid.reform_float(buy_price),
                        market_sell, self.arbitoid.reform_float(sell_price),
                        network[-1], market_fees
                    )
                    await asyncio.sleep(1)
                    await f.delete()

                    await self.bot.send_message(
                        message.from_user.id,
                        md.text(
                            md.hitalic("Link to check: ") +
                            f"https://www.coingecko.com/en/coins/{data['coin'].lower()}#markets" + ' &#9989'
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
                        disable_web_page_preview=True,
                        parse_mode='html',
                        reply_markup=markup
                    )

                else:
                    await self.bot.send_message(
                        message.from_user.id, "Incorrect input &#128219 \n"
                                              "Try again, type the command 👉 /pairs", parse_mode='html',
                        reply_markup=markup
                    )

            except Exception as error:
                try:
                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id, "Unexpected error &#128219 \n"
                                              "Try again, type the command 👉 /pairs", parse_mode='html',
                        reply_markup=markup
                    )
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                await state.finish()
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0
        '''
        ----------------------------------------------
                        Admin logic
        ----------------------------------------------
        '''
        @self.dp.message_handler(commands=['admin', 'promote'])
        @self.dp.message_handler(Text(equals=['🏆 ADMIN'], ignore_case=True))
        async def commands_admin(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in [admin['id'] for admin in self.arbitoid.get_admins['Response']]:
                    markup = TelegramBot.keyboard([["X"]])

                    await Form.admin.set()
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Send the string in the following format: \n\n"
                        f"{md.hcode('user_id|status')}\n"
                        f"{md.hitalic('*0/1 - downgrade/upgrade to admin')}\n\n"
                        "To cancel, type the command 👉 /cancel",
                        disable_web_page_preview=True,
                        parse_mode='html',
                        reply_markup=markup
                    )
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(state=Form.admin)
        async def process_admin(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            try:
                async with state.proxy() as data:
                    data['admin'] = message.text

                tg_id, status = list(map(int, data['admin'].split('|')))
                result = self.arbitoid.add_admin(tg_id, status)['Response']

                user = self.arbitoid.get_user(tg_id)['Response']
                markup = TelegramBot.keyboard(self.admin_panel())

                if result == 0:

                    await self.bot.send_message(
                        message.from_user.id,
                        md.text(
                            f"{'🔥' if status == 1 else '💧'} "
                            f"User {('@' + user['username']) if user['username'] else md.hcode(user['id'])} "
                            f"{'promoted' if status == 1 else 'downgraded'} "
                            f"to {md.hbold('admin' if status == 1 else 'user')}",
                            sep='\n'
                        ),
                        parse_mode='html',
                        reply_markup=markup
                    )

                else:
                    await self.bot.send_message(
                        message.from_user.id, "Incorrect input &#128219 \n"
                                              "Try again, type the command 👉 /admin", parse_mode='html',
                        reply_markup=markup
                    )

                if status == 1:
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    response_markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        tg_id,
                        f"You've been promoted to admin &#10004",
                        parse_mode='html',
                        reply_markup=response_markup
                    )

                else:
                    response_markup = TelegramBot.keyboard(self.main_menu(user)) \
                        if type(self.arbitoid.check_sub(tg_id)['Response']) == str else types.ReplyKeyboardRemove()

                    await self.bot.send_message(
                        tg_id,
                        f"You've been downgraded to user &#10060",
                        parse_mode='html',
                        reply_markup=response_markup
                    )

            except Exception as error:
                try:
                    await self.bot.send_message(
                        message.from_user.id, "Unexpected error &#128219 \n"
                                              "Try again, type the command 👉 /admin", parse_mode='html',
                        reply_markup=TelegramBot.keyboard(self.admin_panel())
                    )
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                await state.finish()
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['stats', 'loc', 'акки', 'data'])
        @self.dp.message_handler(Text(equals=['🏹 STATS'], ignore_case=True))
        async def commands_stats(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in [admin['id'] for admin in self.arbitoid.get_admins['Response']]:
                    user_stats = self.arbitoid.get_stats['Response']
                    markup = TelegramBot.keyboard(self.admin_panel())

                    await self.bot.send_message(
                        message.from_user.id,
                        f"🌍        {md.hbold('USER STATS')}        🌍\n"
                        f"⸻⸻⸻⸻⸻⸻⸻\n\n"
                        f"&#128100 {md.hbold('ALL')}\n"
                        f"├Num: {md.hcode(len(user_stats['all']))}\n"
                        f"├Last Record: "
                        f"{md.hitalic(user_stats['all'][-1] if user_stats['all'] else 'отсутсвует')}\n\n"
                        f"&#128278 {md.hbold('SUB')}\n"
                        f"├Num: {md.hcode(len(user_stats['with_sub']))}\n"
                        f"├Last Record: "
                        f"{md.hitalic(user_stats['with_sub'][-1] if user_stats['with_sub'] else 'отсутсвует')}\n\n"
                        f"Data collected by @Arbitroid_bot",
                        disable_web_page_preview=True,
                        parse_mode='html',
                        reply_markup=markup
                    )
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['add_sub', 'adds'])
        @self.dp.message_handler(Text(equals=['🎫 SUB'], ignore_case=True))
        async def add_sub(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in [admin['id'] for admin in self.arbitoid.get_admins['Response']]:
                    markup = TelegramBot.keyboard([["X"]])

                    await Form.sub.set()
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Send the string in the following format: \n\n"
                        f"{md.hcode('user_id|status')}\n"
                        f"{md.hitalic('*0/1 - take away/give a 2 month sub')}\n\n"
                        "To cancel, type the command 👉 /cancel",
                        disable_web_page_preview=True,
                        parse_mode='html',
                        reply_markup=markup
                    )
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(state=Form.sub)
        async def process_sub(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            try:
                async with state.proxy() as data:
                    data['sub'] = message.text

                tg_id, status = list(map(int, data['sub'].split('|')))
                result = self.arbitoid.add_sub(tg_id, status)['Response']

                user = self.arbitoid.get_user(tg_id)['Response']
                markup = TelegramBot.keyboard(self.admin_panel())

                if result == 0:

                    await self.bot.send_message(
                        message.from_user.id,
                        md.text(
                            f"{'✔' if status == 1 else '✖'} "
                            f"User {('@' + user['username']) if user['username'] else md.hcode(user['id'])} "
                            f"{'subscribed' if status == 1 else 'unsubscribed'} ",
                            sep='\n'
                        ),
                        parse_mode='html',
                        reply_markup=markup
                    )

                else:
                    await self.bot.send_message(
                        message.from_user.id, "Incorrect input &#128219 \n"
                                              "Try again, type the command 👉 /add_sub", parse_mode='html',
                        reply_markup=markup
                    )

                if user['is_admin'] is True:
                    await self.bot.send_message(
                        tg_id,
                        f"Subscription {'confirmed &#10004' if status == 1 else 'declined &#10060'}",
                        parse_mode='html',
                    )
                else:
                    response_markup = TelegramBot.keyboard(self.main_menu(user)) \
                        if status == 1 else types.ReplyKeyboardRemove()

                    await self.bot.send_message(
                        tg_id,
                        f"Subscription {'confirmed &#10004' if status == 1 else 'declined &#10060'}",
                        parse_mode='html',
                        reply_markup=response_markup
                    )

            except Exception as error:
                try:
                    await self.bot.send_message(
                        message.from_user.id, "Unexpected error &#128219 \n"
                                              "Try again, type the command 👉 /add_sub", parse_mode='html',
                        reply_markup=TelegramBot.keyboard(self.admin_panel())
                    )
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                await state.finish()
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(commands=['check_user', 'user'])
        @self.dp.message_handler(Text(equals=['👥 ACC'], ignore_case=True))
        async def check_user(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in [admin['id'] for admin in self.arbitoid.get_admins['Response']]:
                    markup = TelegramBot.keyboard([["X"]])

                    await Form.acc.set()
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Send the string in the following format: \n\n"
                        f"{md.hcode('user_id')}\n\n"
                        "To cancel, type the command 👉 /cancel",
                        disable_web_page_preview=True,
                        parse_mode='html',
                        reply_markup=markup
                    )
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(state=Form.acc)
        async def process_check_user(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            try:
                async with state.proxy() as data:
                    data['check_user'] = message.text

                tg_id = data['check_user']
                result = self.arbitoid.get_user(tg_id)['Response']

                markup = TelegramBot.keyboard(self.admin_panel())

                if type(result) == dict:

                    await self.bot.send_message(
                        message.from_user.id,
                        md.text(
                            f"&#128100 USER"
                            f"⸻⸻⸻⸻⸻⸻⸻\n\n"
                            f"├{md.hbold('ID')}: {md.hcode(result['id'])}\n"
                            f"├{md.hbold('Nick')}: @{result['username'] if result['username'] else 'none'}\n"
                            f"├{md.hbold('Is_admin')}: {result['is_admin']}\n"
                            f"├{md.hbold('Sub')}: {md.hitalic(result['sub'])}\n"
                            f"├{md.hbold('Req_per_1m')}: {md.hcode(str(result['req_num']) + '/5')}\n"
                            f"├{md.hbold('Alerts')}: {'on' if result['status'] == True else 'off'}\n"
                            f"├{md.hbold('Percent')}: {md.hcode(str(result['percent']))}\n"
                            f"├{md.hbold('Is_bot')}: {message.from_user.is_bot}\n",
                            sep='\n'
                        ),
                        parse_mode='html',
                        reply_markup=markup
                    )

                else:
                    await self.bot.send_message(
                        message.from_user.id, "Incorrect input &#128219 \n"
                                              "Try again, type the command 👉 /check_user", parse_mode='html',
                        reply_markup=markup
                    )

            except Exception as error:
                try:
                    await self.bot.send_message(
                        message.from_user.id, "Unexpected error &#128219 \n"
                                              "Try again, type the command 👉 /check_user", parse_mode='html',
                        reply_markup=TelegramBot.keyboard(self.admin_panel())
                    )
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                await state.finish()
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(Text(equals=['⬅ MENU'], ignore_case=True))
        async def back_to_menu(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in [admin['id'] for admin in self.arbitoid.get_admins['Response']]:

                    user = self.arbitoid.get_user(message.from_user.id)['Response']
                    menu = self.main_menu(user)
                    menu.append(['➡ ADMIN_PANEL']) if user['is_admin'] else 0
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id,
                        f"Welcome back, @{message.from_user.username if message.from_user.username else 'user'}\n",
                        parse_mode='html',
                        reply_markup=markup
                    )

                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

        @self.dp.message_handler(Text(equals=['➡ ADMIN_PANEL'], ignore_case=True))
        async def enter_admin_panel(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in [admin['id'] for admin in self.arbitoid.get_admins['Response']]:
                    menu = self.admin_panel()
                    markup = TelegramBot.keyboard(menu)

                    await self.bot.send_message(
                        message.from_user.id,
                        f"&#128272 Welcome to {md.hbold('ARBITOID')} ADMIN PANEL, "
                        f"@{message.from_user.username if message.from_user.username else 'user'}\n",
                        parse_mode='html',
                        reply_markup=markup
                    )

                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}") if self.logger else 0

            finally:
                self.logger.info(f"{func_name}/{message.from_user.id}") if self.logger else 0

    def start(self, skip_updates: bool = True):
        executor.start_polling(self.dp, skip_updates=skip_updates)
