# `Arbitoid`

Cryptocurrency arbitrage with data retrieval through api and as a telegram bot with built-in admin panel.

___

## *Project Status*

***Completed &#10003;***
___
## Functionality
- CRUD operations on users via [FastAPI + SQLAlchemy ORM](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/api.py#L20-L25)
- [CoinGeckoAPI](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/parse.py#L9) class of interaction with the API of one of the blockchain mirrors, as well as the [calculation of the largest spread](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/parse.py#L158-L194) based on market data.
- [ArbitoidAPI](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/parse.py#L239) class implements the bridge function between the FastAPI application and the end user, as well as [calculating the financial benefit](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/parse.py#L245-L283) of arbitrating the asset.
- DatabaseConnector class that implements both [client](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/database/dbapi.py#L35-L216) and [admin](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/database/dbapi.py#L218-L339) logic for interacting with the user table
- TelegramBot class that implements the main [user interaction](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/tg_bot.py#L113-L482) with the API, as well as a convenient [admin panel](https://github.com/Segfaul/arbitoid/blob/5faf8515eb198b28b76c5dcdb40fbf8807f80f9b/tg_bot.py#L483-L856)

## Technologies and Frameworks
- Python 3.11
- FastAPI 
- SQLAlchemy
- Aiogram
- PostgreSQL
___

## Installation

1. Clone the repository to the local machine

    ```shell
    git clone https://github.com/Segfaul/arbitoid.git
    ```

2. Go to the repository directory

    ```shell
    cd arbitoid
    ```

3. Create and activate a virtual environment

    ```shell
    python -m venv env
    source env/bin/activate
    ```

4. Set project dependencies

    ```shell
    pip install -r requirements.txt
    ```

5. Configure the configuration file cfg.json

    ```shell
    nano cfg.json
    ```

6. Run the FastAPI app in the background

    ```python
    uvicorn api:app --reload --log-level error
    ```

7. Run the business logic in the background

    ```python
    python __init__.py &
    ```

8. Run the global parser in the background

    ```python
    python global_parser.py &
    ```

9. In case of a problem, the program will stop automatically or you can stop execution using

    ```shell
    ps aux | grep ".py"
    kill PID
    ```

10. Also you can build a docker app and run the container

    ```shell
    docker build -t app .
    docker run -d app
    ```
___

