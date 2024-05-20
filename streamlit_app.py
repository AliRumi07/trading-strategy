import requests
import numpy as np
import time

# Customizable variables
timer = 0.1
api_endpoint = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
portfolio_balance = 1000
trade_percentage = 0.25
bottom_macd_fast_period = 15
bottom_macd_slow_period = 65
middle_macd_fast_period = 5
middle_macd_slow_period = 10
top_macd_fast_period = 3
top_macd_slow_period = 6
take_profit = 0.0001
stop_loss = 0.0001

def calculate_macd(data, fast_period, slow_period):
    prices = np.array(data)
    fast_ema = np.zeros_like(prices)
    slow_ema = np.zeros_like(prices)
    macd_histogram = np.zeros_like(prices)

    fast_ema[0] = prices[0]
    slow_ema[0] = prices[0]

    for i in range(1, len(prices)):
        fast_ema[i] = (prices[i] - fast_ema[i-1]) * (2 / (fast_period + 1)) + fast_ema[i-1]
        slow_ema[i] = (prices[i] - slow_ema[i-1]) * (2 / (slow_period + 1)) + slow_ema[i-1]

    macd_histogram = fast_ema - slow_ema

    return macd_histogram

def generate_signals():
    position = None
    entry_price = None
    stop_loss_price = None
    take_profit_price = None

    total_trades = 0
    trades_in_profit = 0
    trades_in_loss = 0
    total_profit_loss = 0

    close_prices = []
    bottom_macd = np.array([])
    middle_macd = np.array([])
    top_macd = np.array([])

    while True:
        response = requests.get(api_endpoint)
        data = response.json()
        close_price = float(data["price"])
        close_prices.append(close_price)

        if len(close_prices) > max(bottom_macd_slow_period, middle_macd_slow_period, top_macd_slow_period):
            bottom_macd = np.append(bottom_macd, calculate_macd(close_prices[-bottom_macd_slow_period:], bottom_macd_fast_period, bottom_macd_slow_period)[-1])
            middle_macd = np.append(middle_macd, calculate_macd(close_prices[-middle_macd_slow_period:], middle_macd_fast_period, middle_macd_slow_period)[-1])
            top_macd = np.append(top_macd, calculate_macd(close_prices[-top_macd_slow_period:], top_macd_fast_period, top_macd_slow_period)[-1])

            if position is None:
                if len(bottom_macd) >= 2 and len(middle_macd) >= 2 and len(top_macd) >= 2:
                    if bottom_macd[-1] > 0 and middle_macd[-1] < middle_macd[-2] and top_macd[-1] < 0 and top_macd[-2] > 0:
                        if middle_macd[-1] < middle_macd[0]:
                            position = "Long"
                            entry_price = close_price
                            stop_loss_price = close_price * (1 - stop_loss)
                            take_profit_price = close_price * (1 + take_profit)
                            total_trades += 1

                            print("Signal Detected!")
                            print(f"Trade Type: {position}")
                            print(f"Entry Price: ${entry_price:.2f}")
                            print(f"TP: ${take_profit_price:.2f}")
                            print(f"SL: ${stop_loss_price:.2f}")
                            print()
                    elif bottom_macd[-1] < 0 and middle_macd[-1] > middle_macd[-2] and top_macd[-1] > 0 and top_macd[-2] < 0:
                        if middle_macd[-1] > middle_macd[0]:
                            position = "Short"
                            entry_price = close_price
                            stop_loss_price = close_price * (1 + stop_loss)
                            take_profit_price = close_price * (1 - take_profit)
                            total_trades += 1

                            print("Signal Detected!")
                            print(f"Trade Type: {position}")
                            print(f"Entry Price: ${entry_price:.2f}")
                            print(f"TP: ${take_profit_price:.2f}")
                            print(f"SL: ${stop_loss_price:.2f}")
                            print()

            if position is not None:
                trade_amount = portfolio_balance * trade_percentage
                if position == "Long":
                    if close_price >= take_profit_price:
                        trades_in_profit += 1
                        profit_loss = (take_profit_price - entry_price) * trade_amount / entry_price
                        total_profit_loss += profit_loss
                        position = None
                    elif close_price <= stop_loss_price:
                        trades_in_loss += 1
                        profit_loss = (stop_loss_price - entry_price) * trade_amount / entry_price
                        total_profit_loss += profit_loss
                        position = None
                elif position == "Short":
                    if close_price <= take_profit_price:
                        trades_in_profit += 1
                        profit_loss = (entry_price - take_profit_price) * trade_amount / entry_price
                        total_profit_loss += profit_loss
                        position = None
                    elif close_price >= stop_loss_price:
                        trades_in_loss += 1
                        profit_loss = (entry_price - stop_loss_price) * trade_amount / entry_price
                        total_profit_loss += profit_loss
                        position = None

                if position is None:
                    accuracy = trades_in_profit / total_trades * 100 if total_trades > 0 else 0
                    updated_portfolio_balance = portfolio_balance + total_profit_loss

                    print(f"Total Trades: {total_trades}")
                    print(f"Trades in Profit: {trades_in_profit}")
                    print(f"Trades in Loss: {trades_in_loss}")
                    print(f"Accuracy: {accuracy:.2f}%")
                    print(f"Profit/Loss: ${profit_loss:.2f}")
                    print(f"Total Profit/Loss: ${total_profit_loss:.2f}")
                    print(f"Updated Portfolio Balance: ${updated_portfolio_balance:.2f}")
                    print("------------------------------")
                    print()

        time.sleep(timer)

# Generate trading signals and execute trades
generate_signals()
