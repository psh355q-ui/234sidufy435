
import yfinance as yf
import pandas as pd

def check_yfinance_structures(ticker_symbol):
    print(f"Checking data for {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    print("\n--- Institutional Holders ---")
    try:
        holders = ticker.institutional_holders
        if holders is not None and not holders.empty:
            print("Columns:", holders.columns.tolist())
            print(holders.head(3))
        else:
            print("No institutional holders data found.")
    except Exception as e:
        print(f"Error fetching institutional holders: {e}")

    print("\n--- Insider Transactions ---")
    try:
        # Try both common attributes
        insiders = ticker.insider_transactions
        if insiders is not None and not insiders.empty:
            print("Columns:", insiders.columns.tolist())
            print(insiders.head(3))
        else:
            print("No insider transactions data found.")
            
        print("\n--- Insider Purchases ---")
        purchases = ticker.insider_purchases
        if purchases is not None and not purchases.empty:
            print("Columns:", purchases.columns.tolist())
            print(purchases.head(3))
        else:
            print("No insider purchases data found.")

    except Exception as e:
        print(f"Error fetching insider data: {e}")

if __name__ == "__main__":
    check_yfinance_structures("PLTR")
    check_yfinance_structures("AAPL")
