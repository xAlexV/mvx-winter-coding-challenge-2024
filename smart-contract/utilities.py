import logging
import time
from multiversx_sdk import ProxyNetworkProvider

class Utilities:
    def encode_to_hex(value):
        """Encode a string or numerical value to hexadecimal."""
        if isinstance(value, int):
            # Ensure even-length hex for numerical values
            return hex(value)[2:].zfill(2 * ((len(hex(value)[2:]) + 1) // 2))
        return value.encode().hex()
    
    def encode_boolean(value):
        """Encode a boolean value to hex (`True` -> `01`, `False` -> `00`)."""
        return "01" if value else "00"

    def wait_for_transaction(proxy: ProxyNetworkProvider, tx_hash: str, timeout: int = 60):
        """
        Waits for the transaction to finalize by polling its status.
        """
        start_time = time.time()
        while True:
            transaction_on_network = proxy.get_transaction(tx_hash)
            status = transaction_on_network.status

            logging.info(f"Transaction status: {status}")

            if transaction_on_network.status.is_successful() or transaction_on_network.status.is_executed():
                logging.info("Transaction successfully finalized.")
                return transaction_on_network
            elif transaction_on_network.status.is_failed() or transaction_on_network.status.is_invalid():
                logging.error(f"Transaction failed with status: {status}")
                raise RuntimeError(f"Transaction failed with status: {status}")

            # Check for timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Transaction not finalized within {timeout} seconds.")

            # Poll every 5 seconds
            time.sleep(5)