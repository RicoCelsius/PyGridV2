import ccxt
import config
import os
from dotenv import load_dotenv, find_dotenv
import ccxt
import config
from decimal import Decimal


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
            cls._instance.exchange.load_markets()
        return cls._instance

    def load_market_structure(self):
        self.market_structure = self.exchange.market(config.PAIR)
        self.base = config.PAIR.partition('/')[0]
        self.quote = config.PAIR.partition('/')[-1]

    def get_filters(self):
        return self.market_structure['info']['filters']

    def get_quote(self):
        return self.market_structure['quote']

    def get_base_precision(self):
        return self.market_structure['precision']['amount']


    def get_minimal_quantity(self):
        min_notional = self.get_filters()[2]['minNotional']
        return Decimal(min_notional)

    def get_price_precision(self):
        return self.market_structure['precision']['price']

    def __init__(self):
        self.load_market_structure()
        self.min_notional = self.get_minimal_quantity()
        self.base_precision = self.get_base_precision()
        self.price_precision = self.get_price_precision()
        self.quote = self.get_quote()
