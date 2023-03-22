import ccxt
import enums
import config
from exchange import Exchange
from decimal import Decimal
from telegram_module import sendMessage
from mysql_module import Mysql
exchange = Exchange()

class Order:

    
    def __init__(self, pair, order_type, side, quantity,price):
        self.pair = pair
        self.order_type = order_type
        self.side = side
        self.quantity = Decimal(quantity)
        self.status = enums.Status.OPEN
        self.exchange = Exchange().exchange
        self.order_id = None
        self.price = price
        self.send_order()
    
    def send_order(self):
 
            order_params = {
                'symbol': self.pair,
                'type': self.order_type,
                'side': self.side,
                'amount': Decimal(self.quantity),
                'price' : self.price
            }
            print(order_params['price'])
            order = self.exchange.create_order(**order_params)
            self.order_id = order['id']
           
            Mysql().insert_order(self.pair,self.order_type,self.side,Decimal(self.quantity),self.status.value,config.EXCHANGE,self.order_id,order_params['price'])
            sendMessage(f'PAIR: {self.pair}\nQUANTITY: {Decimal(self.quantity)}\nSIDE: {self.side}\nPRICE:{self.price}')
            print('Order placed:', order['id'])



    def cancel_order(self):
        order_params = {
            'orderId': self.order_id,
            'symbol': self.order_type,
        }
        order = self.exchange.cancel_order(**order_params)
        print('Order canceled:', order['id'])
