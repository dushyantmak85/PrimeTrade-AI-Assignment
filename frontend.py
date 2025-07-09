# This is a Flask web application that allows users to place orders on Binance Futures through a web interface. 

# This application runs on port 5000 and provides a form for users to input order details.
# To run the application, ensure you have Flask installed and start the server with `python frontend.py`.

from flask import Flask, render_template_string, request
from bot import Input_from_frontend  # Importing the function from bot.py to handle order placement

app = Flask(__name__)

# HTML template for the form
HTML_FORM = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Binance Futures Order</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      background: linear-gradient(135deg, #232526, #414345);
      min-height: 100vh;
      font-family: 'Segoe UI', Arial, sans-serif;
      color: #f5f6fa;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .container {
      background: rgba(34, 40, 49, 0.95);
      padding: 2.5rem 2rem 2rem 2rem;
      border-radius: 18px;
      box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
      max-width: 400px;
      width: 100%;
      margin: 2rem;
      animation: fadeIn 1s;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-30px);}
      to { opacity: 1; transform: translateY(0);}
    }
    h2 {
      text-align: center;
      margin-bottom: 1.5rem;
      letter-spacing: 1px;
      color: #ffd700;
      font-weight: 700;
    }
    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #ffd700;
    }
    input, select {
      width: 100%;
      padding: 0.6rem;
      margin-bottom: 1.2rem;
      border: none;
      border-radius: 8px;
      background: #393e46;
      color: #f5f6fa;
      font-size: 1rem;
      transition: background 0.2s;
    }
    input:focus, select:focus {
      background: #222831;
      outline: 2px solid #ffd700;
    }
    .hidden {
      display: none;
    }
    button, input[type=submit] {
      width: 100%;
      padding: 0.8rem;
      background: linear-gradient(90deg, #ffd700 60%, #ffb300 100%);
      color: #232526;
      border: none;
      border-radius: 8px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(255, 215, 0, 0.15);
      transition: background 0.2s, color 0.2s;
    }
    button:hover, input[type=submit]:hover {
      background: linear-gradient(90deg, #ffb300 60%, #ffd700 100%);
      color: #232526;
    }
    .alert {
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1.2rem;
      text-align: center;
      font-weight: 600;
      font-size: 1.05rem;
      box-shadow: 0 2px 8px rgba(255, 215, 0, 0.07);
      animation: fadeIn 0.6s;
    }
    .alert-success {
      background: #1e5631;
      color: #d4ffb2;
      border: 1px solid #a6e22e;
    }
    .alert-error {
      background: #5c1e1e;
      color: #ffd6d6;
      border: 1px solid #ff4d4d;
    }
    pre {
      background: #232526;
      color: #ffd700;
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.98rem;
      margin-top: 1.2rem;
      box-shadow: 0 2px 8px rgba(255, 215, 0, 0.07);
    }
    @media (max-width: 500px) {
      .container { padding: 1.2rem 0.5rem; }
      h2 { font-size: 1.3rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Binance Futures Order</h2>
    {% if message %}
      <div class="alert {{ 'alert-success' if success else 'alert-error' }}">{{ message }}</div>
    {% endif %}
    <form method="post" autocomplete="off">
      <label for="symbol">Symbol</label>
      <input name="symbol" id="symbol" value="BTCUSDT" required>

      <label for="side">Side</label>
      <select name="side" id="side">
        <option value="BUY">BUY</option>
        <option value="SELL">SELL</option>
      </select>

      <label for="order_type">Order Type</label>
      <select name="order_type" id="order_type" onchange="showFields(this.value)">
        <option value="MARKET">MARKET</option>
        <option value="LIMIT">LIMIT</option>
        <option value="STOP_MARKET">STOP_MARKET</option>
      </select>

      <label for="quantity">Quantity</label>
      <input name="quantity" id="quantity" value="0.001" required>

      <div id="limit_price" class="hidden">
        <label for="price">Limit Price</label>
        <input name="price" id="price" type="number" step="any">
      </div>
      <div id="stop_price" class="hidden">
        <label for="stop_price_input">Stop Price</label>
        <input name="stop_price" id="stop_price_input" type="number" step="any">
      </div>
      <input type="submit" value="Place Order">
    </form>
    {% if result %}
    <h3 style="color:#ffd700;text-align:center;">Order Result:</h3>
    <pre>{{ result }}</pre>
    {% endif %}
  </div>
  <script>
    function showFields(type) {
      document.getElementById('limit_price').classList.toggle('hidden', type !== 'LIMIT');
      document.getElementById('stop_price').classList.toggle('hidden', type !== 'STOP_MARKET');
    }
    // On page load, set correct fields
    document.addEventListener('DOMContentLoaded', function() {
      showFields(document.getElementById('order_type').value);
    });
  </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    message = None
    success = False

   
    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        side = request.form['side'].upper()
        order_type = request.form['order_type'].upper()
        quantity = float(request.form['quantity'])
        price = request.form.get('price') or None
        stop_price = request.form.get('stop_price') or None
        if price == '':
            price = None
        if stop_price == '':
            stop_price = None

        response = Input_from_frontend(symbol, side, order_type, quantity, price, stop_price)
        result = response

        # Use the returned dictionary's success and message fields
        if isinstance(response, dict):
            success = response.get("success", False)
            message = response.get("message", "Order failed. See details below.")
        else:
            # fallback for string or unexpected result
            message = str(response)
            success = False

    return render_template_string(HTML_FORM, result=result, message=message, success=success)

if __name__ == '__main__':
    app.run(debug=True)