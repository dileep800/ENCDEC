# CRYPT — Recursive File Encryption Utility

A symmetric encryption utility implementing AES-256 and ChaCha20 stream cipher with recursive directory traversal, IV randomization, and a zero-dependency browser-side WebCrypto GUI

## Live Demo

🌐 **[Open GUI →](https://d3sec.github.io/encdec)**

---

## Project Structure

```
crypt/
├── index.html          # Browser GUI (drag & drop, WebCrypto)
├── encrypt.py          # CLI tool (Python, handles files & folders)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## CLI Usage

### Install

```bash
pip install -r requirements.txt
```

### Generate a key

```bash
# 128-bit (32 hex chars)
python3 -c "import os; print(os.urandom(16).hex())"

# 192-bit (48 hex chars)
python3 -c "import os; print(os.urandom(24).hex())"

# 256-bit (64 hex chars)
python3 -c "import os; print(os.urandom(32).hex())"
```

### Encrypt a file

```bash
python3 encrypt.py encrypt secret.txt --cipher aes --mode ctr --key <hex_key>
python3 encrypt.py encrypt secret.txt --cipher aes --mode cbc --key <hex_key>
python3 encrypt.py encrypt secret.txt --cipher aes --mode ofb --key <hex_key>
python3 encrypt.py encrypt secret.txt --cipher aes --mode cfb --key <hex_key>
python3 encrypt.py encrypt secret.txt --cipher chacha20 --key <64_hex> --nonce <32_hex>
```

### Decrypt a file

```bash
python3 encrypt.py decrypt secret.txt.enc --cipher aes --mode ctr --key <hex_key>
python3 encrypt.py decrypt secret.txt.enc --cipher chacha20 --key <64_hex>
```

### Encrypt / Decrypt a folder (recursive)

```bash
# Encrypts all files in the folder and all subfolders
python3 encrypt.py encrypt myfolder/ --cipher aes --mode ctr --key <hex_key>

# Decrypts all .enc files recursively
python3 encrypt.py decrypt myfolder/ --cipher aes --mode ctr --key <hex_key>
```

---

## Key Length Reference

| Bits | Bytes | Hex chars |
|------|-------|-----------|
| 128  | 16    | 32        |
| 192  | 24    | 48        |
| 256  | 32    | 64        |

- **AES** supports 128, 192, and 256-bit keys
- **ChaCha20** requires exactly a 256-bit key + 128-bit nonce (32 hex chars)

---

## File Format

Encrypted files are stored as:

```
[ IV — 16 bytes ][ Ciphertext ]
```

The IV is randomly generated per file (or user-supplied for ChaCha20) and prepended to the ciphertext. No other metadata is stored.

---

## Compatibility (Bonus)

For cross-group compatibility, any implementation that:
1. Prepends the 16-byte IV before the ciphertext
2. Uses PKCS7 zero-byte padding for AES-CBC
3. Passes the full 16-byte nonce directly to ChaCha20

...will be compatible with this program under the same key.

---

## GUI

Open `index.html` in any modern browser. Supports drag & drop, key generation, and downloads the encrypted/decrypted file directly. Runs 100% client-side — no server required.

---

## Requirements

- Python 3.10+
- `cryptography` package
