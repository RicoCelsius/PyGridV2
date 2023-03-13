from order import Order
from exchange import Exchange
from art import *
from decimal import Decimal
orders = []





order = Order('ETH/USDT', 'market', 'buy', 0.01)





# print(text2art("PyGrid V2"))

# # def getCurrentPrice():
# #     try:
# #         priceUSD = Decimal((float(ticker['ask']) + float(ticker['bid'])) / 2)
# #         return priceUSD
# #     except Exception as e: print(e)

# def getBalance():
#     try:
#         balance = round(Decimal(Exchange.exchange.fetchBalance()['BUSD']['free']),2)
#         return str(balance)
#     except Exception as e: print(e)

# print(getBalance())
# # Define a key function to use for sorting
# def sort_key(order):
#     return order.quantity

# # Sort the orders list
# sorted_orders = sorted(orders, key=sort_key)

# # Loop over the sorted orders list
# for order in sorted_orders:
#     print(order.quantity)


