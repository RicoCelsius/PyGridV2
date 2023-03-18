from order import Order
from exchange import Exchange
from art import *
import config
import threading
import schedule
from telegram_module import main,sendMessage
import time
from decimal import Decimal
from mysql_module import Mysql
exchange = Exchange()

#retrieve open orders in db
#check if sell orders are filled, if yes. Change status to closed and send a message to TG
#check if buy orders are still open, if not, create sell order
#change status buy order to closed

pair = config.PAIR
cancel_order_factor = 2


def get_current_price():
    ticker = exchange.exchange.fetch_ticker(config.PAIR)
    priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
    return priceUSD
     

def calculate_sell_price(average_buy_price):
    stepsize = Decimal(Decimal(config.SPACE_BETWEEN_GRID)/Decimal(100)*Decimal(average_buy_price))
    sell_price = Decimal(average_buy_price) + Decimal(stepsize)
    print(f'SELLL RRICEEE {sell_price}')
    return sell_price

def calculate_quantity():
        quantityInQuote = config.INVESTMENT_PER_ORDER / get_current_price()
        precision = exchange.base_precision
        return round(quantityInQuote,precision)


def get_open_orders():
    open_orders = Mysql().select_by_status('open')
    open_buy_orders = [order for order in open_orders if order[3] == 'buy']
    open_sell_orders = [order for order in open_orders if order[3] == 'sell']
    # sort the sell orders by price and retrieve the first 10
    sorted_sell_orders = sorted(open_sell_orders, key=lambda x: x[8])
    top_2_sell_orders = sorted_sell_orders[:2]

    sorted_buy_orders = sorted(open_buy_orders, key=lambda x: x[8], reverse=True)
    top_2_buy_orders = sorted_buy_orders[:2]
    
    for order in top_2_sell_orders:
        check_and_update_sell_orders(order)

    for order in top_2_buy_orders:
        check_and_update_buy_orders(order)



def check_and_update_sell_orders(order):
    order_id = order[7]
    symbol = order[1]
    exchange_response = exchange.exchange.fetchOrder(order_id, symbol)
    current_status = exchange_response['status']
    if current_status == 'closed':
        print(f'{order_id} order {current_status}, for {symbol}')
        average_sell_price = exchange_response['average']
        Mysql().update(order_id, current_status,average_sell_price)


def check_and_update_buy_orders(order):
    global cancel_order_factor
    order_id = order[7]
    symbol = order[1]
    exchange_response = exchange.exchange.fetchOrder(order_id, symbol)
    current_status = exchange_response['status']
    print(f'Current status is {current_status}, orderid = {order_id}, symb is {symbol}')
    if current_status == 'closed':
        average_buy_price = exchange_response['average']
        sell_price = calculate_sell_price(average_buy_price)
        print(f'sell price is {sell_price}')
        Order(symbol, config.ORDER_TYPE, 'sell',order[4],sell_price)
        cancel_order_factor = 2
        Mysql().update(order_id, current_status,average_buy_price)


def cancel_lowest_buy_order_for_range():
    try:
        open_orders = Mysql().select_by_status('open')
    
        if open_orders:
            global cancel_order_factor
            open_buy_orders = [order for order in open_orders if order[3] == 'buy']
            buy_prices = [order[8] for order in open_buy_orders]
            lowest_price = min(buy_prices)
            highest_price = max(buy_prices)
            print(f'lowest_price {lowest_price}')
            v1 = highest_price
            v2 = get_current_price()
            percdiff = abs((abs(v1)-abs(v2))/((v1+v2)/2)*100)
            threshold = percdiff/2 > config.SPACE_BETWEEN_GRID
            print(f'pricediff {percdiff}, threshold is {threshold}')
            if open_buy_orders:
                lowest_order = min(open_buy_orders, key=lambda x: x[8])
            if threshold:
                print('CANCELLLING  ORDER')
                try:
                    exchange.exchange.cancel_order(str(lowest_order[7]),symbol=config.PAIR)
                except Exception as e:
                    sendMessage(e)
                    Order(config.PAIR,lowest_order[2],'sell',lowest_order[4],calculate_sell_price(lowest_order[8]))
                quantity = calculate_quantity()
                Order(config.PAIR,config.ORDER_TYPE,'buy',quantity,((highest_price+(get_step_price()*cancel_order_factor))))
                cancel_order_factor += 1
                Mysql().update(lowest_order[7],'canceled')
    except Exception as e: print(e)
            



def get_step_price():
    stepsize = Decimal(Decimal(config.SPACE_BETWEEN_GRID)/Decimal(100)*get_current_price())
    print(f'step size {stepsize}')
    return stepsize


def get_lowest_price(side):
        try:
            stepsize = get_step_price()
            open_orders = Mysql().select_by_status('open')
            open_buy_orders = [order for order in open_orders if order[3] == side]
            buy_prices = [order[8] for order in open_buy_orders]
            lowest_price = min(buy_prices)
            print(f'lowest price = {lowest_price}')
            return lowest_price - stepsize
        except ValueError: return get_current_price() - stepsize


def total_open_orders():
    # Assuming that Mysql() is a custom class with a select_by_status() method
    open_orders = Mysql().select_by_status('open')
    num_open_orders = len(open_orders)
    return num_open_orders, open_orders

def cancel_orders_above_limit():
    # Call the total_open_orders() function with parentheses
    num_open_orders, open_orders = total_open_orders()
    # Assuming that the limit should be 150 or more open orders
    if num_open_orders > config.MAX_OPEN_TOTAL_ORDERS:
        open_sell_orders = [order for order in open_orders if order[3] == 'sell']
        # sort the sell orders by price in descending order and retrieve the first 10
        sorted_sell_orders = sorted(open_sell_orders, key=lambda x: x[8], reverse=True)
        top_sell_orders = sorted_sell_orders[:2]
        # Retrieve the order IDs of the top sell orders and cancel them
        for order in top_sell_orders:
            order_id = order[7]  # Assuming that the order ID is stored in index 7 of the order tuple
            try:
                exchange.exchange.cancel_order(str(order_id), symbol=config.PAIR)
                Mysql().update(order_id,'temporary_canceled')
            except Exception as e: print (e)
    else:
        open_orders_below_limit()

def open_orders_below_limit():
    open_orders = Mysql().select_by_status('temporary_canceled')
    temporary_canceled_sell_orders = [order for order in open_orders if order[3] == 'sell']
    sorted_sell_orders = sorted(temporary_canceled_sell_orders, key=lambda x: x[8], reverse=False)
    top_sell_orders = sorted_sell_orders[:2]
    for order in top_sell_orders:
        # Assuming that Order() is a custom function that creates a new order
        Order(order[1], order[2], order[3], order[4], order[8])
        Mysql().update(order[7],'replaced')




        


          

def check_open_buy_orders_count():
        open_orders = Mysql().select_by_status('open')
        open_buy_orders = [order for order in open_orders if order[3] == 'buy']
        open_buy_orders_count = len(open_buy_orders)
        print(open_buy_orders_count)
        if open_buy_orders_count < config.MAX_OPEN_BUY_ORDERS:
             quantity = calculate_quantity()
             Order(config.PAIR,config.ORDER_TYPE,'buy',quantity,get_lowest_price('buy'))
        else: print(f'Waiting till open buy orders are filled... open orders: {open_buy_orders_count}, maximum: {config.MAX_OPEN_BUY_ORDERS}')
        

def job():
     get_open_orders()
     cancel_lowest_buy_order_for_range()
     check_open_buy_orders_count()
     cancel_orders_above_limit()
     job()
job()






try:
    threading.Thread(target=main()).start()
except Exception as e:
    print(e)



