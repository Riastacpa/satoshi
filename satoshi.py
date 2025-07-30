from bitcoinrpc.authproxy import AuthServiceProxy
import re

def extract_op_return_messages(limit=100):
    rpc_user = "bitcoin"
    rpc_password = "local321"
    rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:8332")

    block_count = rpc_connection.getblockcount()
    messages = []

    for i in range(block_count, block_count - limit, -1):
        block_hash = rpc_connection.getblockhash(i)
        block = rpc_connection.getblock(block_hash)
        for txid in block['tx']:
            tx = rpc_connection.getrawtransaction(txid, True)
            for vout in tx.get("vout", []):
                script_pub_key = vout.get("scriptPubKey", {})
                asm = script_pub_key.get("asm", "")
                if asm.startswith("OP_RETURN"):
                    hex_data = asm.split(" ")[1]
                    try:
                        decoded = bytes.fromhex(hex_data).decode('utf-8', errors='replace')
                        cleaned = decoded.strip().replace('\x00', '')
                        if cleaned:
                            messages.append({
                                "block": i,
                                "txid": txid,
                                "message": cleaned
                            })
                    except Exception:
                        continue
    return messages
