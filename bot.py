# This is main trading bot script that connects to Binance Futures and allows users to place orders.
# It uses the Binance Futures API to interact with the market and perform trading operations.

# For this bot to work, you need to have a Binance account and testnet API_KEY and API_SECRET set up in a .env file .
# The bot supports placing MARKET, LIMIT, and STOP_MARKET orders.

import logging
import sys
import os
from dotenv import load_dotenv
from binance.um_futures import UMFutures  # Importing Binance Futures client for USDT-M Futures
from binance.error import ClientError     # Importing Binance API error for error handling

# Setting up logging
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load keys from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        base_url = "https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com"  # Binance USDT-M Futures API base URL      
        self.client = UMFutures(key=api_key, secret=api_secret, base_url=base_url)                 # Initializing the Binance Futures client      
         
        try:
            account = self.client.account()
            logging.info("Connected to Binance Futures Testnet.")
        except Exception as e:
            logging.error("Connection failed: %s", str(e))
            sys.exit("Failed to connect to Binance Testnet. Check API keys.")

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        try:                      
            params = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity
            }
            
            if order_type == "LIMIT":
                params["price"] = price
                params["timeInForce"] = "GTC"
                
            elif order_type == "STOP_MARKET": # Added a STOP_MARKET order type as the third order type             
                params["stopPrice"] = stop_price
                params["timeInForce"] = "GTE_GTC"
            
            # If order_type is "MARKET", the bot does not add price or stopPrice to params.
            # The Binance API will interpret this as a market order. 
                
            order = self.client.new_order(**params)
            logging.info("Order placed Successfully: %s", order)
            return order
        
        except ClientError as e:                    # Catching Binance API exceptions          
            logging.error("API Error: %s", str(e))  # Log the error message
            return f"API Error: {str(e)}"
        
        except Exception as e:                      # Catching any other exceptions
            logging.error("Unexpected Error: %s", str(e))
            return f"Unexpected Error: {str(e)}"

# Function to get user input for placing an order
def get_user_input():
    symbol = input("Enter symbol (e.g., BTCUSDT): ").upper()
    side = input("Buy or Sell? ").upper()
    order_type = input("Order type (MARKET / LIMIT / STOP_MARKET): ").upper()
    quantity = float(input("Quantity: "))
    price = None
    stop_price = None
    
    if order_type == 'LIMIT':
        price = input("Enter limit price: ")     # For LIMIT orders, the user must provide a price.
        
    elif order_type == 'STOP_MARKET':
        stop_price = input("Enter stop price: ") # For STOP_MARKET orders, the user must provide a stop price.
        
    return symbol, side, order_type, quantity, price, stop_price


# Function to place an order from frontend input
def Input_from_frontend(symbol, side, order_type, quantity, price=None, stop_price=None):
    """Function to place an order from the frontend input and return a JSON-serializable result."""
    bot = BasicBot(API_KEY, API_SECRET)
    order = bot.place_order(symbol, side, order_type, quantity, price, stop_price)
    
    # If order is a dict and contains 'orderId', treat as success
    if isinstance(order, dict) and "orderId" in order:
        return {
            "success": True,
            "message": f"Order placed successfully! Order ID: {order['orderId']}",
            "order": order
        }
        
    # If order is a string (error), treat as error
    return {
        "success": False,
        "message": order if isinstance(order, str) else "Order failed.",
        "order": order
    }
            
     

