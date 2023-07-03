import json
import logging

from fastapi import FastAPI

from parse import CoinGeckoAPI
from database.dbapi import DatabaseConnector

cfg = json.load(open('cfg.json', 'r'))

logger = logging.getLogger("FastAPI")
logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler('arbitoid.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


app = FastAPI()
db_con = DatabaseConnector(cfg['database']['params'], logger)
gecko_api = CoinGeckoAPI(
    cfg['CoinGecko']['link'], cfg['CoinGecko']['network_fees'], cfg['CoinGecko']['market_fees'],
    cfg['parse']['headers'], {"https": f"http://{cfg['parse']['proxy']['proxy2']}"}, logger
)


@app.get("/arbitoid/gecko_pairs/{coin}")
def gecko_pairs(coin: str) -> dict:
    response = gecko_api.gecko_pairs(coin)
    return {'Response': response}


@app.get("/user/get_stats")
def get_stats() -> dict:
    response = db_con.get_stats
    return {'Response': response}


@app.get("/user/get_ready_users")
def get_ready_users() -> dict:
    response = db_con.get_ready_users
    return {'Response': response}


@app.get("/user/get_admins")
def get_admins() -> dict:
    response = db_con.get_admins
    return {'Response': response}


@app.get("/user/get_user/{tg_id}")
def get_user(tg_id: int) -> dict:
    response = db_con.get_user(tg_id)
    return {'Response': response}


@app.get("/user/check_sub/{tg_id}")
def check_sub(tg_id: int) -> dict:
    response = db_con.check_sub(tg_id)
    return {'Response': response}


@app.post("/user/input_user")
def input_user(tg_id: int, username: str = None) -> dict:
    response = db_con.input_user(tg_id, username)
    return {'Response': response}


@app.post("/user/switch_status")
def switch_status(tg_id: int) -> dict:
    response = db_con.switch_status(tg_id)
    return {'Response': response}


@app.post("/user/add_sub")
def add_sub(tg_id: int, np: int) -> dict:
    response = db_con.add_sub(tg_id, np)
    return {'Response': response}


@app.post("/user/remove_req")
def remove_req(tg_id: int) -> dict:
    response = db_con.remove_req(tg_id)
    return {'Response': response}


@app.post("/user/reset_req")
def remove_req() -> dict:
    response = db_con.reset_req()
    return {'Response': response}


@app.post("/user/add_admin")
def add_admin(tg_id: int, np: int) -> dict:
    response = db_con.add_admin(tg_id, np)
    return {'Response': response}


@app.put("/user/add_req")
def add_req(tg_id: int) -> dict:
    response = db_con.add_req(tg_id)
    return {'Response': response}


@app.put("/user/resize_percent")
def resize_percent(tg_id: int, percent: float) -> dict:
    response = db_con.resize_percent(tg_id, percent)
    return {'Response': response}
