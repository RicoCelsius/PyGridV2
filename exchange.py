import ccxt
import config
import os
from dotenv import load_dotenv, find_dotenv
import ccxt
import config


load_dotenv(find_dotenv())
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")

class Exchange:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.exchange_class = getattr(ccxt, config.EXCHANGE)
            cls._instance.exchange = cls._instance.exchange_class({
                'apiKey': API_KEY,
                'secret': API_KEY_SECRET,
                'enableRateLimit': True,
            })
            cls._instance.exchange.set_sandbox_mode(True)
            cls._instance.exchange.load_markets()
        return cls._instance
