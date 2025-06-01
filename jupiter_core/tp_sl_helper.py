
import base64
import base58
import requests
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client

def place_tp_sl_order(
    private_key_base58: str,
    input_mint: str,
    output_mint: str,
    in_amount: int,
    out_amount: int,
    rpc_url: str = "https://api.mainnet-beta.solana.com"
) -> str:
    """
    Create a TP or SL limit order through Jupiter's Trigger API.
    """
    wallet = Keypair.from_bytes(base58.b58decode(private_key_base58))
    maker = str(wallet.pubkey())

    create_order_req = {
        "maker": maker,
        "payer": maker,
        "inputMint": input_mint,
        "outputMint": output_mint,
        "params": {
            "makingAmount": str(in_amount),
            "takingAmount": str(out_amount)
        },
        "computeUnitPrice": "auto"
    }

    resp = requests.post("https://api.jup.ag/limit/v1/createOrder", json=create_order_req)

    try:
        data = resp.json()
    except Exception:
        raise Exception(f"Failed to decode response from Jupiter: {resp.status_code} - {resp.text}")

    order_acc = data["order"]
    tx_base64 = data["tx"]

    tx = VersionedTransaction.deserialize(base64.b64decode(tx_base64))
    tx.sign([wallet])
    client = Client(rpc_url)
    tx_sig = client.send_raw_transaction(tx.serialize())["result"]

    return f"🚀 Placed TP/SL order. Order: {order_acc}, Tx: {tx_sig}"
