import logging
from pathlib import Path
from multiversx_sdk import (
    Address,
    ProxyNetworkProvider,
    QueryRunnerAdapter,
    SmartContractQueriesController
)
from multiversx_sdk.abi import Abi

LOG_FILE = "query_sc.log"

# Configuration for the blockchain connection
API_URL = "https://devnet-api.multiversx.com"
ABI_PATH = "./issue-token-snow-sc/output/issue-token-snow-sc.abi.json"
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqmm40w8anjxdr9mrtcag0a4ydhg4a9ukfq7vqrfujc7"
VIEW_ENDPOINT = "get_account_tokens"  # The view function to call
USER_ADDRESS = "erd1jvch655u7egt93vqj54ea2mxp4fsqr6v5gwftwg8qd06dwllq7vq2mkggc"  # Replace with the user's address to query

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

def query_user_issued_tokens():
    # Set up ProxyNetworkProvider and QueryRunnerAdapter
    proxy = ProxyNetworkProvider(API_URL)
    query_runner = QueryRunnerAdapter(proxy)

    # Load the ABI
    abi = Abi.load(Path(ABI_PATH))

    # Create the Query Controller
    query_controller = SmartContractQueriesController(query_runner, abi)

    # Convert USER_ADDRESS to an Address object
    user_address = Address.new_from_bech32(USER_ADDRESS)

    # Prepare the query
    logging.info(f"Querying contract: {SC_ADDRESS}, endpoint: {VIEW_ENDPOINT}, user: {USER_ADDRESS}")
    query = query_controller.create_query(
        contract=SC_ADDRESS,
        function=VIEW_ENDPOINT,
        arguments=[user_address],  # Pass the address object as argument
    )

    # Execute the query
    query_response = query_controller.run_query(query)

    # Parse the query response
    try:
        data_parts = query_controller.parse_query_response(query_response)
        logging.info(f"Query result (parsed): {data_parts}")
        return data_parts
    except Exception as e:
        logging.error(f"Error parsing query response: {e}")
        raise

if __name__ == "__main__":
    try:
        result = query_user_issued_tokens()
        if result:
            logging.info(f"Tokens issued by user: \n{str(result)}")
        else:
            logging.info("No tokens found for the user.")
    except Exception as e:
        logging.error(f"An error occurred during the query: {e}")