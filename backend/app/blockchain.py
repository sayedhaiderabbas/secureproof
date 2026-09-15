from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .config import settings


@dataclass
class ProofResult:
    network: str
    contract_address: str
    transaction_hash: str
    block_number: int
    timestamp: datetime


class BlockchainUnavailable(Exception):
    pass


class BlockchainService:
    def __init__(self) -> None:
        self._memory_records: dict[str, tuple[str, str, datetime]] = {}
        self._memory_block = 0

    def register(self, evidence_id: str, evidence_hash: str) -> ProofResult:
        if settings.blockchain_mode == "memory":
            if evidence_id in self._memory_records:
                raise BlockchainUnavailable("A proof is already registered for this evidence.")
            timestamp = datetime.now(timezone.utc)
            self._memory_block += 1
            transaction_hash = "0x" + uuid4().hex + uuid4().hex[:32]
            contract_address = "development-memory-ledger"
            self._memory_records[evidence_id] = (evidence_hash, transaction_hash, timestamp)
            return ProofResult("development-memory", contract_address, transaction_hash, self._memory_block, timestamp)
        if not all([settings.blockchain_rpc_url, settings.blockchain_private_key, settings.contract_address]):
            raise BlockchainUnavailable("RPC mode requires RPC URL, private key, and contract address.")
        try:
            from web3 import Web3
            from web3.middleware import ExtraDataToPOAMiddleware

            web3 = Web3(Web3.HTTPProvider(settings.blockchain_rpc_url))
            web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            if not web3.is_connected():
                raise BlockchainUnavailable("Configured blockchain RPC is unavailable.")
            account = web3.eth.account.from_key(settings.blockchain_private_key)
            contract = web3.eth.contract(address=Web3.to_checksum_address(settings.contract_address), abi=CONTRACT_ABI)
            nonce = web3.eth.get_transaction_count(account.address)
            transaction = contract.functions.registerEvidenceHash(
                Web3.keccak(text=evidence_id), bytes.fromhex(evidence_hash)
            ).build_transaction({"from": account.address, "nonce": nonce, "chainId": settings.chain_id, "gas": 250000, "gasPrice": web3.eth.gas_price})
            signed = account.sign_transaction(transaction)
            transaction_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
            return ProofResult(str(settings.chain_id), settings.contract_address, transaction_hash.hex(), receipt.blockNumber, datetime.now(timezone.utc))
        except BlockchainUnavailable:
            raise
        except Exception as error:
            raise BlockchainUnavailable("Blockchain registration failed.") from error

    def get(self, evidence_id: str) -> tuple[str, str] | None:
        if settings.blockchain_mode == "memory":
            record = self._memory_records.get(evidence_id)
            return (record[0], record[1]) if record else None
        raise BlockchainUnavailable("RPC verification retrieval is not configured in this MVP adapter.")


blockchain_service = BlockchainService()

CONTRACT_ABI = [
    {"inputs": [{"internalType": "bytes32", "name": "evidenceId", "type": "bytes32"}, {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"}], "name": "registerEvidenceHash", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]
