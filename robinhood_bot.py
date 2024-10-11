import robin_stocks.robinhood as r
import openai
import yfinance as yf
import time
import logging
from datetime import datetime, timedelta
import pytz  # To handle time zones

# Robinhood Login
robinhood_username = "your_robinhood_username"
robinhood_password = "your_robinhood_password"
login = r.login(robinhood_username, robinhood_password)

# OpenAI API Key (Get from OpenAI dashboard)
openai.api_key = 'your_openai_api_key'

# Set up logging to keep track of balances and trades
logging.basicConfig(filename='trade_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to get available balance
def get_available_balance():
    profile_data = r.profiles.load_account_profile()
    return float(profile_data['cash'])

# Ask GPT for trading decision
def ask_chatgpt(stock_symbol, current_price, moving_average, sentiment, purchase_price):
    prompt = f"""
    Analyze the following stock data and suggest whether to buy, sell, or hold.
    Stock: {stock_symbol}
    Current Price: ${current_price}
    Moving Average (10 days): ${moving_average}
    Market Sentiment: {sentiment}
    Purchase Price: ${purchase_price}
    Provide a decision with reasoning.
    """

    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=150,
        temperature=0.5,
    )

    return response['choices'][0]['text'].strip()

# Get market sentiment (Placeholder)
def get_market_sentiment(stock_symbol):
    return "positive"  # Replace with actual sentiment analysis

# Moving average strategy
def moving_average_strategy(stock_symbol, purchase_price):
    # Fetch historical stock data for last 10 days
    historicals = r.stocks.get_stock_historicals(stock_symbol, interval='day', span='month')
    closing_prices = [float(day['close_price']) for day in historicals[-10:]]
    moving_average = sum(closing_prices) / len(closing_prices)

    # Get current stock price
    current_price = float(r.stocks.get_latest_price(stock_symbol)[0])

    # Get market sentiment
    sentiment = get_market_sentiment(stock_symbol)

    # Ask GPT for trade decision
    gpt_decision = ask_chatgpt(stock_symbol, current_price, moving_average, sentiment, purchase_price)
    return gpt_decision, current_price

# Trade stock based on available balance using fractional shares
def trade_stock(stock_symbol, available_balance, purchase_price, allocation_fraction=0.05):
    decision, current_price = moving_average_strategy(stock_symbol, purchase_price)
    
    # Determine how much of the balance to allocate for this stock (e.g., 5% of available balance)
    allocation_amount = available_balance * allocation_fraction

    if decision.lower() == "buy":
        if allocation_amount > 0:
            # Calculate how much fractional shares to buy based on available allocation
            fractional_shares = allocation_amount / current_price
            r.orders.order_buy_fractional_by_quantity(stock_symbol, fractional_shares)
            trade_value = fractional_shares * current_price
            print(f"Bought {fractional_shares:.4f} share(s) of {stock_symbol} at ${current_price:.2f} per share.")
            print(f"Total dollar amount of the trade: ${trade_value:.2f}")
            logging.info(f"Bought {fractional_shares:.4f} share(s) of {stock_symbol} at ${current_price:.2f} per share.")
            return trade_value  # Deduct from balance
        else:
            print(f"Not enough balance to buy {stock_symbol}.")
            logging.info(f"Not enough balance to buy {stock_symbol}.")
    
    elif decision.lower() == "sell":
        # Assuming fractional shares were previously bought (you would need to check actual holdings)
        holdings = r.stocks.get_open_stock_positions(stock_symbol)
        if holdings:
            fractional_shares_to_sell = holdings[0]['quantity'] * 0.5  # Replace 0.5 with desired sell fraction
            r.orders.order_sell_fractional_by_quantity(stock_symbol, fractional_shares_to_sell)
            trade_value = fractional_shares_to_sell * current_price
            print(f"Sold {fractional_shares_to_sell:.4f} share(s) of {stock_symbol} at ${current_price:.2f} per share.")
            print(f"Total dollar amount of the trade: ${trade_value:.2f}")
            logging.info(f"Sold {fractional_shares_to_sell:.4f} share(s) of {stock_symbol} at ${current_price:.2f} per share.")
    
    else:
        print(f"Holding {stock_symbol}.")
        logging.info(f"Holding {stock_symbol}.")

    return 0

# Fetch current holdings, including purchase price, and exclude VOO and S&P 500 stocks
def get_filtered_holdings():
    # Fetch current positions from Robinhood
    holdings = r.account.build_holdings()
    
    # List of S&P 500 stocks (this list can be updated as needed)
    s_and_p_500_symbols = ['VOO']  # Add any other specific symbols you want to exclude

    # Filter out stocks that are in VOO or the S&P 500
    filtered_holdings = {symbol: details for symbol, details in holdings.items() if symbol not in s_and_p_500_symbols}
    
    # Extract holdings with average purchase price
    holdings_with_purchase_price = {symbol: details['average_buy_price'] for symbol, details in filtered_holdings.items()}
    
    return holdings_with_purchase_price

# Check if the market is open (9:30 AM to 4:00 PM Eastern Time)
def is_market_open():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

# Execute trades only when the market is open
def run_bot():
    initial_balance = get_available_balance()
    logging.info(f"Initial account balance: ${initial_balance:.2f}")
    print(f"Initial account balance: ${initial_balance:.2f}")

    # Fetch the filtered holdings dynamically (excluding VOO and S&P 500)
    filtered_holdings_with_prices = get_filtered_holdings()
    logging.info(f"Filtered holdings (excluding VOO and S&P 500) with purchase prices: {filtered_holdings_with_prices}")
    print(f"Filtered holdings (excluding VOO and S&P 500) with purchase prices: {filtered_holdings_with_prices}")

    # Set a loop limit for testing (for example, run for 3 cycles or you can modify this)
    cycles = 3
    while cycles > 0:
        if is_market_open():
            available_balance = get_available_balance()

            # Keep track of balance throughout the cycle
            total_spent = 0
            for stock, purchase_price in filtered_holdings_with_prices.items():
                if available_balance <= 0:
                    logging.info("Insufficient funds, stopping trades.")
                    print("Insufficient funds, stopping trades.")
                    break
                spent = trade_stock(stock, available_balance, float(purchase_price))
                total_spent += spent  # Sum up all spending for the cycle
                available_balance -= spent  # Update available balance for the next trade

            # Log and print the ending balance after each cycle
            final_balance = get_available_balance()
            logging.info(f"End of cycle. Current balance: ${final_balance:.2f}")
            print(f"End of cycle. Current balance: ${final_balance:.2f}")
            
            # Reduce cycle count
            cycles -= 1

            # Sleep for an hour before the next cycle (for testing, you can reduce this to a few seconds)
            time.sleep(3600)
        else:
            print("Market is closed. Sleeping until market opens.")
            time_to_market_open = (datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)) - datetime.now()
            time.sleep(time_to_market_open.total_seconds())

# Run the bot
while True:
    if is_market_open():
        run_bot()
    else:
        print("Market is closed. Sleeping until market opens.")
        # Sleep until the next market open (9:30 AM Eastern Time the next day)
        time_to_market_open = (datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)) - datetime.now()
        time.sleep(time_to_market_open.total_seconds())
