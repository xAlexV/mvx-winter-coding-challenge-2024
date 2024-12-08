class Config:
    def __init__(self, chain_id: str, min_gas_limit: int, gas_limit_per_byte: int) -> None:
        self.chain_id = chain_id
        self.min_gas_limit = min_gas_limit
        self.gas_limit_per_byte = gas_limit_per_byte