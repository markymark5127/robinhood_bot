# Robinhood Trading Bot with ChatGPT and Purchase Price Analysis

This project is a Python-based trading bot that interacts with Robinhood to execute fractional share trades using insights from OpenAI's GPT model. The bot dynamically retrieves your current stock holdings, filters out specific stocks (such as those in VOO or the S&P 500), and makes buy, sell, or hold decisions based on stock data, average purchase price, and market conditions. The bot operates only during U.S. market hours (9:30 AM to 4:00 PM ET).

## Features

- **Dynamic Stock Holdings**: Fetches the stocks you currently hold in your Robinhood account and analyzes them.
- **Exclusion of VOO and S&P 500 Stocks**: Automatically excludes VOO and any other specified stocks (e.g., S&P 500 stocks) from trading.
- **Purchase Price Analysis**: Analyzes the average purchase price of each stock you hold and includes it in the decision-making process.
- **Trade Decisions Powered by ChatGPT**: Uses OpenAI's GPT model to generate trade recommendations (buy, sell, hold) based on stock data, average purchase price, and sentiment analysis.
- **Fractional Share Trading**: Executes fractional share trades on Robinhood.
- **U.S. Stock Market Hours**: The bot runs only during market hours (9:30 AM to 4:00 PM ET) and sleeps outside of these hours.
- **Detailed Output**: Logs trade actions, including number of shares traded, price, and total dollar amount. Also tracks balance updates after trades.

## Prerequisites

Before you can run the bot, you'll need:

1. **Python** (3.7+)
2. A **Robinhood account**.
3. An **OpenAI API key**.
4. The following Python libraries:
   - `robin_stocks`
   - `openai`
   - `yfinance`
   - `pytz`
   - `logging`

Install the required libraries using:

```bash
pip install robin_stocks openai yfinance pytz
