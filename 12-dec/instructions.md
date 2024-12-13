# Prerequisites

- Python 3.x: Ensure Python 3.x is installed.
- Required Python libraries:
```shell
pip install requests
```

# Run the Script
- change constants if needed
```
TOKEN_PAGE_SIZE = 100 # number of token WINTER tokens per page
ACCOUNTS_PER_TOKEN_PAGE_SIZE = 1000 # number of accounts with WINTER token per page
```
- run
```shell
python generate_winter_leaderboard.py
```
- output can be viewed in winter_token_leaderboard.log
- winter_leaderboard.csv containing the leaderboards for each WINTER token is created