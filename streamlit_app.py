pip install requests
import streamlit as st
import requests
import time

# Define the API endpoint
api_endpoint = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

# Function to fetch the price from the API
def get_price():
    response = requests.get(api_endpoint)
    data = response.json()
    return float(data["price"])

# Initialize the price
price = get_price()

# Streamlit app
def app():
    st.title("Bitcoin Price Tracker")

    # Create a placeholder for the price
    price_placeholder = st.empty()

    # Update the price every second
    while True:
        new_price = get_price()
        if new_price != price:
            price = new_price
            price_placeholder.metric("Bitcoin Price (BTCUSDT)", f"${price:,.2f}")
        time.sleep(1)

# Run the Streamlit app
if __name__ == "__main__":
    app()
