import requests
import logging
import csv
from decimal import Decimal

API_URL = "https://devnet-api.multiversx.com"
LOG_FILE = "winter_token_leaderboard.log"
TOKEN_PAGE_SIZE = 100
ACCOUNTS_PER_TOKEN_PAGE_SIZE = 1000

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

def fetch_all_winter_tokens(page_size=TOKEN_PAGE_SIZE):
    """
    Retrieve all WINTER tokens using pagination.
    """
    winter_tokens = []
    page = 0

    while True:
        url = f"{API_URL}/tokens?search=WINTER&from={page * page_size}&size={page_size}"
        logging.info(f"Fetching WINTER tokens from page {page}, size {page_size}")
        response = requests.get(url)

        if response.status_code == 200:
            token_page = response.json()
            if not token_page:  # No more tokens
                break
            winter_tokens.extend(token_page)
            page += 1
        else:
            logging.error(f"Error fetching WINTER tokens: {response.text}")
            break

    logging.info(f"Total WINTER tokens retrieved: {len(winter_tokens)}")
    return winter_tokens

def fetch_token_accounts(token_identifier, total_accounts, page_size=ACCOUNTS_PER_TOKEN_PAGE_SIZE):
    """
    Retrieve all accounts holding a specific token using pagination, 
    stopping early if the fetched accounts reach or exceed total_accounts.
    """
    accounts = []
    page = 0

    while True:
        if len(accounts) >= total_accounts:
            logging.info(f"Reached the total number of accounts ({total_accounts}) for token {token_identifier}. Stopping fetch.")
            break

        url = f"{API_URL}/tokens/{token_identifier}/accounts?from={page * page_size}&size={page_size}"
        logging.info(f"Fetching accounts for token {token_identifier}, page {page}, size {page_size}")
        response = requests.get(url)

        if response.status_code == 200:
            account_page = response.json()
            if not account_page:  # No more accounts
                break
            accounts.extend(account_page)
            page += 1
        else:
            logging.error(f"Error fetching accounts for token {token_identifier}: {response.text}")
            break

    logging.info(f"Total accounts retrieved for token {token_identifier}: {len(accounts)}")
    return accounts

def format_balance(balance, decimals):
    """
    Format the balance from smallest unit to human-readable format with decimals.
    """
    balance_decimal = Decimal(balance) / Decimal(10**decimals)
    return f"{balance_decimal:,.8f}".rstrip('0').rstrip('.')

def save_leaderboard_to_csv(leaderboard, file_path="winter_leaderboard.csv"):
    """
    Save the leaderboard to a CSV file with positions.
    """
    with open(file_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["Position", "Token Identifier", "Address", "Balance"])

        for token, accounts in leaderboard.items():
            for position, account in enumerate(accounts, start=1):
                writer.writerow([position, token, account["address"], account["balance"]])

    logging.info(f"Leaderboard saved to {file_path}")

def generate_leaderboard():
    """
    Generate a leaderboard for all WINTER tokens.
    """
    leaderboard = {}
    winter_tokens = fetch_all_winter_tokens()

    for token in winter_tokens:
        token_identifier = token["identifier"]
        decimals = token["decimals"]  # Fetch token decimals for proper formatting
        total_accounts = token["accounts"]  # Total number of accounts holding this token

        accounts = fetch_token_accounts(token_identifier, total_accounts)
        
        # Sort accounts by balance in descending order and take top 3
        sorted_accounts = sorted(accounts, key=lambda acc: int(acc["balance"]), reverse=True)[:3]

        # Format balances for top 3 accounts
        for account in sorted_accounts:
            account["balance"] = format_balance(account["balance"], decimals)
        
        leaderboard[token_identifier] = sorted_accounts

    save_leaderboard_to_csv(leaderboard)

if __name__ == "__main__":
    try:
        generate_leaderboard()
    except Exception as e:
        logging.error(f"An error occurred: {e}")