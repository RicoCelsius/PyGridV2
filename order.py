import ccxt
import enums
import config
from exchange import Exchange



class Order:
    def __init__(self, pair, order_type, side, quantity):
        self.pair = pair
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.status = enums.Status.OPEN
        self.exchange = Exchange().exchange
        self.order_id = None
        self.send_order()

    def send_order(self):
        order_params = {
            'symbol': self.pair,
            'type': self.order_type,
            'side': self.side,
            'amount': self.quantity,
        }
        order = self.exchange.create_order(**order_params)
        self.order_id = order['id']
        print(order)
        print('Order placed:', order['id'])

    def cancel_order(self):
        order_params = {
            'orderId': self.order_id,
            'symbol': self.order_type,
        }
        order = self.exchange.cancel_order(**order_params)
        print('Order canceled:', order['id'])
