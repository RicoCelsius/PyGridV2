from order import Order
from exchange_module import Exchange
from art import *
import config
from telegram_module import sendMessage
from exception_handler_module import exception_handler
from decimal import Decimal
from mysql_module import Mysql
exchange = Exchange()

#retrieve open orders in db
#check if sell orders are filled, if yes. Change status to closed and send a message to TG
#check if buy orders are still open, if not, create sell order
#change status buy order to closed

pair = config.PAIR
cancelled_dust = Decimal(0)




def get_current_price():
    try:
        ticker = exchange.exchange.fetch_ticker(config.PAIR)
        priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
        return priceUSD
    except Exception as e: exception_handler(e)
     

def calculate_sell_price(average_buy_price):
    try:
        stepsize = Decimal(Decimal(config.SPACE_BETWEEN_GRID)/Decimal(100)*Decimal(average_buy_price))
        sell_price = Decimal(average_buy_price) + Decimal(stepsize)
        return sell_price
    except Exception as e: exception_handler(e)

def calculate_quantity():
        try:
            quantityInQuote = config.INVESTMENT_PER_ORDER / get_current_price()
            precision = exchange.base_precision
            return round(quantityInQuote,precision)
        except Exception as e: exception_handler(e)

def get_open_orders(side):
        open_orders = Mysql().select_by_status('open')
        open_side_orders = [order for order in open_orders if order[3] == f'{side}']
        return open_side_orders


def sell_dust(minimum_quantity,highest_price):
    global cancelled_dust
    if cancelled_dust > minimum_quantity:
        sendMessage('Trying to send order to get rid of dust')
        Order(config.PAIR, config.ORDER_TYPE, 'sell', Decimal(cancelled_dust), highest_price + get_step_price(),'dust order')
        sendMessage(f'send order {cancelled_dust}')
        cancelled_dust = Decimal(0)

def check_open_orders():
    try:
        

        open_sell_orders = get_open_orders('sell')
        open_buy_orders = get_open_orders('buy')
        # sort the sell orders by price and retrieve the first 10
        sorted_sell_orders = sorted(open_sell_orders, key=lambda x: x[8])
        top_2_sell_orders = sorted_sell_orders[:2]

        sorted_buy_orders = sorted(open_buy_orders, key=lambda x: x[8], reverse=True)
        top_2_buy_orders = sorted_buy_orders[:2]
        
        for order in top_2_sell_orders:
            check_and_update_sell_orders(order)

        for order in top_2_buy_orders:
            check_and_update_buy_orders(order)
    except Exception as e: exception_handler(e)



def check_and_update_sell_orders(order):
    try:
        order_id = order[7]
        symbol = order[1]
        exchange_response = exchange.exchange.fetchOrder(order_id, symbol)
        current_status = exchange_response['status']
        if current_status == 'closed':
            print(f'{order_id} order {current_status}, for {symbol}')
            average_sell_price = exchange_response['average']
            fee = get_fee(order_id)
            Mysql().update(order_id, current_status,average_sell_price,fee)
    except Exception as e: exception_handler(e)

def check_and_update_buy_orders(order):
    try:
        order_id = order[7]
        symbol = order[1]
        exchange_response = exchange.exchange.fetchOrder(order_id, symbol)
        current_status = exchange_response['status']
        print(f'Current status is {current_status}, orderid = {order_id}, symb is {symbol}')
        if current_status == 'closed':
            average_buy_price = exchange_response['average']
            fee = get_fee(order_id)
            sell_qty = Decimal(order[4]) - fee
            sell_price = calculate_sell_price(average_buy_price)
            Order(symbol, config.ORDER_TYPE, 'sell',sell_qty,sell_price)
            Mysql().update(order_id, current_status,average_buy_price,fee)
    except Exception as e: exception_handler(e)


def check_threshold(open_buy_orders):
        print('Checking threshold')
        highest_price = get_highest_price_in_list(open_buy_orders)
        v1 = highest_price
        v2 = get_current_price()
        percdiff = abs((abs(v1)-abs(v2))/((v1+v2)/2)*100)
        threshold = percdiff > (config.SPACE_BETWEEN_GRID*2)
        print(f'Threshold is {threshold}')
        return True if threshold else False
        
def get_highest_price_in_list(open_buy_orders):
    buy_prices = [order[8] for order in open_buy_orders]
    highest_price = max(buy_prices)
    return highest_price





def cancel_lowest_buy_order_for_range():
    try:
        global cancelled_dust
        open_buy_orders = get_open_orders('buy')
        if open_buy_orders:
            threshold = check_threshold(open_buy_orders)
            if threshold:
                lowest_order = min(open_buy_orders, key=lambda x: x[8])
                highest_price = get_highest_price_in_list(open_buy_orders)
                print('Cancelling order')
                try:
                    exchange.exchange.cancel_order(str(lowest_order[7]), symbol=config.PAIR)
                    exchange_response = exchange.exchange.fetchOrder(lowest_order[7], config.PAIR)
                    if Decimal(exchange_response['filled']) > 0:
                        filled = exchange_response['filled']
                        sendMessage(f'Order cancelled, but something is filled: {filled}')
                        minimum_quantity = (Decimal(exchange.get_minimal_quantity() + 1)) / Decimal(get_current_price())
                        cancelled_dust += Decimal(str(filled))
                        sendMessage(f'Min qty = {minimum_quantity}, cancelled dust = {cancelled_dust}')
                        sell_dust(minimum_quantity,highest_price)

                            
                except Exception as e:
                    try:
                        exchange_response = exchange.exchange.fetchOrder(lowest_order[7], config.PAIR)
                        filled = exchange_response['filled']
                        status = exchange_response['info']['status']
                        minimum_quantity = (Decimal(exchange.get_minimal_quantity() + 1)) / Decimal(get_current_price())
                        sendMessage(f"Order couldn't be cancelled, status is {status}, amount filled: {filled}")
                        cancelled_dust += Decimal(str(filled))
                        sendMessage(f'cancelled dust = {cancelled_dust}, min qty = {minimum_quantity}')
                        sell_dust(minimum_quantity,highest_price)

                    except Exception as e:
                        exception_handler(e)

                Order(config.PAIR, config.ORDER_TYPE, 'buy', calculate_quantity(), highest_price + get_step_price())
                Mysql().update(lowest_order[7], 'canceled')
    except Exception as e:
        exception_handler(e)

            

def get_fee(order_id):
    try:
        exchange_response = exchange.exchange.fetchOrder(order_id,config.PAIR)
        if exchange_response is not None and 'fee' in exchange_response:
            fee = exchange_response['fee']
            return 0 if fee is None else fee
    except Exception as e: exception_handler(e)    
    






def get_step_price():
    try:
        stepsize = Decimal(Decimal(config.SPACE_BETWEEN_GRID)/Decimal(100)*get_current_price())
        return stepsize
    except Exception as e: exception_handler(e)


def get_lowest_price(side):
        try:
            stepsize = get_step_price()
            open_orders = Mysql().select_by_status('open')
            open_buy_orders = [order for order in open_orders if order[3] == side]
            if len(open_buy_orders) != 0:
                buy_prices = [order[8] for order in open_buy_orders]
                lowest_price = min(buy_prices)
                return lowest_price - stepsize
            else: return get_current_price() - stepsize
        except Exception as e: 
            exception_handler(e)
            


def total_open_orders():
    try:
        # Assuming that Mysql() is a custom class with a select_by_status() method
        open_orders = Mysql().select_by_status('open')
        num_open_orders = len(open_orders)
        return num_open_orders, open_orders
    except Exception as e: exception_handler(e)

def cancel_orders_above_limit():
    # Call the total_open_orders() function with parentheses
    num_open_orders, open_orders = total_open_orders()
    print(num_open_orders)
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
            except Exception as e: exception_handler(e)
    else:
        open_orders_below_limit()



def open_orders_below_limit():
    try:
        open_orders = Mysql().select_by_status('temporary_canceled')
        temporary_canceled_sell_orders = [order for order in open_orders if order[3] == 'sell']
        sorted_sell_orders = sorted(temporary_canceled_sell_orders, key=lambda x: x[8], reverse=False)
        top_sell_orders = sorted_sell_orders[:2]
        for order in top_sell_orders:
            # Assuming that Order() is a custom function that creates a new order
            Order(order[1], order[2], order[3], order[4], order[8])
            Mysql().update(order[7],'replaced')
    except Exception as e: exception_handler(e)
          

def check_open_buy_orders_count():
    try:
        open_orders = Mysql().select_by_status('open')
        open_buy_orders = [order for order in open_orders if order[3] == 'buy']
        open_buy_orders_count = len(open_buy_orders)
        if open_buy_orders_count < config.MAX_OPEN_BUY_ORDERS:
            quantity = calculate_quantity()
            Order(config.PAIR,config.ORDER_TYPE,'buy',quantity,get_lowest_price('buy'))
        else: print(f'Waiting till open buy orders are filled... open orders: {open_buy_orders_count}, maximum: {config.MAX_OPEN_BUY_ORDERS}')
    except Exception as e: exception_handler(e)
        



while True:
    cancel_orders_above_limit()
    check_open_orders()
    check_open_buy_orders_count()
    cancel_lowest_buy_order_for_range()
    




