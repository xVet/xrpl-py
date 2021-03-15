"""High-level sign-and-submit methods with XRPL transactions."""

from typing import Any, Callable, Dict

from xrpl.binarycodec import encode, encode_for_signing
from xrpl.keypairs.main import sign
from xrpl.models.requests.request import Request
from xrpl.models.requests.transactions.submit_only import SubmitOnly
from xrpl.models.response import Response
from xrpl.models.transactions import Transaction
from xrpl.wallet import Wallet


def transaction_transaction(
    transaction: Transaction,
    wallet: Wallet,
    send_transaction: Callable[[Request], Response],
) -> Response:
    """
    Signs a transaction and submits it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        send_transaction: the function with which to submit the transaction.

    Returns:
        The response from the ledger.
    """
    tx_blob = sign_transaction(transaction, wallet)
    return submit_transaction_blob(tx_blob, send_transaction)


def sign_transaction(transaction: Transaction, wallet: Wallet) -> str:
    """
    Signs a transaction.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    # Increment the wallet sequence number, since we're about to use one.
    wallet.next_sequence_num += 1
    transaction_json = transaction_json_to_binary_codec_form(transaction.to_dict())
    transaction_json["SigningPubKey"] = wallet.pub_key
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = sign(serialized_bytes, wallet.priv_key)
    transaction_json["TxnSignature"] = signature
    return encode(transaction_json)


def submit_transaction_blob(
    transaction_blob: str,
    send_transaction: Callable[[Request], Response],
) -> Response:
    """
    Submits a transaction blob to the ledger.

    Args:
        transaction_blob: the transaction blob to be submitted.
        send_transaction: the function with which to submit the transaction.

    Returns:
        The response from the ledger.
    """
    submit_request = SubmitOnly(tx_blob=transaction_blob)
    return send_transaction(submit_request)


def transaction_json_to_binary_codec_form(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a new dictionary in which the keys have been formatted as CamelCase and
    standardized to be serialized by the binary codec.

    Args:
        dictionary: The dictionary to be reformatted.

    Returns:
        A new dictionary object that has been reformatted.
    """
    formatted_dict = {
        _snake_to_capital_camel(key): value for (key, value) in dictionary.items()
    }
    # one-off conversion cases for transaction field names
    if "CheckId" in formatted_dict:
        formatted_dict["CheckID"] = formatted_dict["CheckId"]
        del formatted_dict["CheckId"]
    if "InvoiceId" in formatted_dict:
        formatted_dict["InvoiceID"] = formatted_dict["InvoiceId"]
        del formatted_dict["InvoiceId"]
    return formatted_dict


def _snake_to_capital_camel(field: str) -> str:
    """Transforms snake case to capitalized camel case.
    For example, 'transaction_type' becomes 'TransactionType'.
    """
    words = field.split("_")
    capitalized_words = [word.capitalize() for word in words]
    return "".join(capitalized_words)