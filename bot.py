import logging
import sys
import os
from dotenv import load_dotenv
from binance.um_futures import UMFutures  # Importing Binance Futures client for USDT-M Futures
from binance.error import ClientError     # Importing Binance API error for error handling

# Setup logging
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
        self.client = UMFutures(key=api_key, secret=api_secret, base_url=base_url) # Initializing the Binance Futures client      
         
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
            logging.info("Order placed: %s", order)
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


def main():
    bot = BasicBot(API_KEY, API_SECRET)
    while True:
        try:
            # Get user input for placing an order
            symbol, side, order_type, quantity, price, stop_price = get_user_input()            
            
            # Placing the order using the bot
            order = bot.place_order(symbol, side, order_type, quantity, price, stop_price)
            print("Order Result:\n", order)
            
        except KeyboardInterrupt:
            print("\nExiting bot.")
            break

if __name__ == "__main__":
    main()