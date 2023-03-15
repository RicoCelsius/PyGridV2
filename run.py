from order import Order
from exchange import Exchange
from art import *
from decimal import Decimal
from mysql_module import Mysql
exchange = Exchange()





Order('ETH/BUSD','limit','buy',0.01,1400)
Mysql().update(12345,'closeed')



def calculateSellPrice(buy_price): print()


def check_open_orders():
    open_orders = Mysql().select_by_status('open')
    open_buy_orders = [order for order in open_orders if order[3] == 'buy']
    for orders in open_buy_orders:
        order_id = orders[7]
        symbol = orders[1]
        exchange_response = exchange.exchange.fetchOrder(order_id,symbol)
        current_status = exchange_response['status']
        print(current_status)
        if current_status == 'filled':
            average_bought_price = exchange_response['average']
            Mysql().update(order_id,'filled')


check_open_orders()
