# Robinhood Trading Bot with ChatGPT

This project is a Python-based trading bot that interacts with Robinhood to execute fractional share trades using insights from OpenAI's GPT model. The bot dynamically retrieves the top 15 stocks by market capitalization and makes buy, sell, or hold decisions based on stock data and sentiment analysis.

## Features

- **Dynamic Stock Selection**: Fetches the top 15 stocks by market capitalization using the `yfinance` API.
- **Trade Decisions Powered by ChatGPT**: Uses OpenAI's GPT model to generate trade recommendations based on stock data.
- **Fractional Share Trading**: Executes fractional share trades on Robinhood.
- **Detailed Output**: Logs trade actions, including number of shares traded, price, and total dollar amount.
- **Balance Tracking**: Tracks and prints the account balance before and after trades.
- **Cycle-Based Execution**: Runs for a fixed number of cycles, executing trades at intervals.

## Prerequisites

Before you can run the bot, you'll need:

1. **Python** (3.7+)
2. A **Robinhood account**.
3. An **OpenAI API key**.
4. The following Python libraries:
   - `robin_stocks`
   - `openai`
   - `yfinance`
   - `logging`

Install the required libraries using:

```bash
pip install robin_stocks openai yfinance
