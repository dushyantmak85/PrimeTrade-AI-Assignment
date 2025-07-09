import logging                                        # Importing logging for logging events
import sys                                            # Importing sys for system-level operations
from binance.client import Client                    
from binance.exceptions import BinanceAPIException    # Importing Binance API exception for error handling
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load keys
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret)
        if testnet:
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        try:
            account = self.client.futures_account()
            logging.info("Connected to Binance Futures Testnet.")
        except Exception as e:
            logging.error("Connection failed: %s", str(e))
            sys.exit("Failed to connect to Binance Testnet. Check API keys.")

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        try:
            if order_type == 'MARKET':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
            elif order_type == 'LIMIT':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity,
                    price=price,
                    timeInForce='GTC'
                )
            elif order_type == 'STOP_MARKET':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='STOP_MARKET',
                    stopPrice=stop_price,
                    closePosition=False,
                    quantity=quantity,
                    timeInForce='GTC'
                )
            else:
                raise ValueError("Unsupported order type.")
            logging.info("Order placed: %s", order)
            return order
        except BinanceAPIException as e:
            logging.error("API Error: %s", str(e))
            return f"API Error: {str(e)}"
        except Exception as e:
            logging.error("Unexpected Error: %s", str(e))
            return f"Unexpected Error: {str(e)}"

def get_user_input():
    symbol = input("Enter symbol (e.g., BTCUSDT): ").upper()
    side = input("Buy or Sell? ").upper()
    order_type = input("Order type (MARKET / LIMIT / STOP_MARKET): ").upper()
    quantity = float(input("Quantity: "))
    
    price = None
    stop_price = None

    if order_type == 'LIMIT':
        price = input("Enter limit price: ")
    elif order_type == 'STOP_MARKET':
        stop_price = input("Enter stop price: ")

    return symbol, side, order_type, quantity, price, stop_price

def main():
    api_key = input("Enter your Binance API key: ")
    api_secret = input("Enter your Binance API secret: ")
    bot = BasicBot(api_key, api_secret)

    while True:
        try:
            symbol, side, order_type, quantity, price, stop_price = get_user_input()
            order = bot.place_order(symbol, side, order_type, quantity, price, stop_price)
            print("Order Result:\n", order)
        except KeyboardInterrupt:
            print("\nExiting bot.")
            break

if __name__ == "__main__":
    main()