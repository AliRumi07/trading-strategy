import streamlit as st
import requests
import numpy as np
import time

# Customizable variables
timer = 0.1
api_endpoint = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

# Streamlit input fields
st.sidebar.title("Trading Strategy Parameters")
portfolio_balance = st.sidebar.number_input("Initial Portfolio Balance", min_value=1.0, value=1000.0)
trade_percentage = st.sidebar.slider("Trade Percentage", min_value=0.01, max_value=1.0, value=0.25, step=0.01)
bottom_macd_fast_period = st.sidebar.number_input("Bottom MACD Fast Period", min_value=1, max_value=100, value=15)
bottom_macd_slow_period = st.sidebar.number_input("Bottom MACD Slow Period", min_value=1, max_value=100, value=65)
middle_macd_fast_period = st.sidebar.number_input("Middle MACD Fast Period", min_value=1, max_value=100, value=5)
middle_macd_slow_period = st.sidebar.number_input("Middle MACD Slow Period", min_value=1, max_value=100, value=10)
top_macd_fast_period = st.sidebar.number_input("Top MACD Fast Period", min_value=1, max_value=100, value=3)
top_macd_slow_period = st.sidebar.number_input("Top MACD Slow Period", min_value=1, max_value=100, value=6)
take_profit = st.sidebar.number_input("Take Profit (%)", min_value=0.0001, max_value=1.0, value=0.0001, step=0.0001)
stop_loss = st.sidebar.number_input("Stop Loss (%)", min_value=0.0001, max_value=1.0, value=0.0001, step=0.0001)

# MACD calculation function (unchanged)
def calculate_macd(data, fast_period, slow_period):
    # ... (same as before)

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

    # Streamlit placeholders for live updates
    price_placeholder = st.empty()
    signal_placeholder = st.empty()
    trade_stats_placeholder = st.empty()

    while True:
        response = requests.get(api_endpoint)
        data = response.json()
        close_price = float(data["price"])
        close_prices.append(close_price)

        if len(close_prices) > max(bottom_macd_slow_period, middle_macd_slow_period, top_macd_slow_period):
            bottom_macd = np.append(bottom_macd, calculate_macd(close_prices[-bottom_macd_slow_period:], bottom_macd_fast_period, bottom_macd_slow_period)[-1])
            middle_macd = np.append(middle_macd, calculate_macd(close_prices[-middle_macd_slow_period:], middle_macd_fast_period, middle_macd_slow_period)[-1])
            top_macd = np.append(top_macd, calculate_macd(close_prices[-top_macd_slow_period:], top_macd_fast_period, top_macd_slow_period)[-1])

            # Update price placeholder
            price_placeholder.metric("Current Price", f"${close_price:.2f}")

            if position is None:
                if len(bottom_macd) >= 2 and len(middle_macd) >= 2 and len(top_macd) >= 2:
                    if bottom_macd[-1] > 0 and middle_macd[-1] < middle_macd[-2] and top_macd[-1] < 0 and top_macd[-2] > 0:
                        if middle_macd[-1] < middle_macd[0]:
                            position = "Long"
                            entry_price = close_price
                            stop_loss_price = close_price * (1 - stop_loss)
                            take_profit_price = close_price * (1 + take_profit)
                            total_trades += 1

                            signal_message = f"Signal Detected! Trade Type: {position} Entry Price: ${entry_price:.2f} TP: ${take_profit_price:.2f} SL: ${stop_loss_price:.2f}"
                            signal_placeholder.success(signal_message)

                    elif bottom_macd[-1] < 0 and middle_macd[-1] > middle_macd[-2] and top_macd[-1] > 0 and top_macd[-2] < 0:
                        if middle_macd[-1] > middle_macd[0]:
                            position = "Short"
                            entry_price = close_price
                            stop_loss_price = close_price * (1 + stop_loss)
                            take_profit_price = close_price * (1 - take_profit)
                            total_trades += 1

                            signal_message = f"Signal Detected! Trade Type: {position} Entry Price: ${entry_price:.2f} TP: ${take_profit_price:.2f} SL: ${stop_loss_price:.2f}"
                            signal_placeholder.success(signal_message)

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

                    trade_stats = f"Total Trades: {total_trades}\nTrades in Profit: {trades_in_profit}\nTrades in Loss: {trades_in_loss}\nAccuracy: {accuracy:.2f}%\nProfit/Loss: ${profit_loss:.2f}\nTotal Profit/Loss: ${total_profit_loss:.2f}\nUpdated Portfolio Balance: ${updated_portfolio_balance:.2f}"
                    trade_stats_placeholder.info(trade_stats)

        time.sleep(timer)

# Streamlit app
st.title("Trading Strategy")
generate_signals()
