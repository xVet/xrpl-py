"""Utility functions and variables for integration tests."""

from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.network_clients import JsonRpcClient
from xrpl.sign_and_submit import sign_and_submit_transaction
from xrpl.wallet import Wallet

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)


def submit_transaction(transaction: Transaction, wallet: Wallet) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return sign_and_submit_transaction(transaction, wallet, JSON_RPC_CLIENT.request)