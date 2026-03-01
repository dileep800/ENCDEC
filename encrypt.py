import os, argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# ── colours ──────────────────────────────────────────────
R="\033[91m"; G="\033[92m"; Y="\033[93m"
C="\033[96m"; B="\033[94m"; M="\033[95m"; W="\033[97m"; X="\033[0m"
BOLD="\033[1m"; DIM="\033[2m"

BANNER = f"""{M}{BOLD}
  ██████╗██████╗ ██╗   ██╗██████╗ ████████╗
 ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝
 ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   
 ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   
 ╚██████╗██║  ██║   ██║   ██║        ██║   
  ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝  {X}
{DIM}{C}  Recursive File Encryption Utility  |  CS 645/745{X}
{DIM}  AES (CBC/CTR/OFB/CFB)  +  ChaCha20{X}
"""

def log_info(msg):  print(f"  {C}[*]{X} {msg}")
def log_ok(msg):    print(f"  {G}[+]{X} {W}{BOLD}{msg}{X}")
def log_err(msg):   print(f"  {R}[!]{X} {R}{msg}{X}")
def log_dim(msg):   print(f"  {DIM}    {msg}{X}")

def section(title):
    print(f"\n{B}{'─'*50}{X}")
    print(f"{B}  {BOLD}{title}{X}")
    print(f"{B}{'─'*50}{X}")

# ── crypto ───────────────────────────────────────────────
def encrypt_file(path, cipher, mode, key, nonce):
    with open(path, 'rb') as f:
        data = f.read()

    if cipher == 'chacha20':
        iv = bytes.fromhex(nonce)
        ct = Cipher(algorithms.ChaCha20(key, iv), mode=None).encryptor().update(data)
    else:
        iv = os.urandom(16)
        m = {'cbc': modes.CBC, 'ctr': modes.CTR, 'ofb': modes.OFB, 'cfb': modes.CFB}[mode]
        if mode == 'cbc':
            data += b'\x00' * (16 - len(data) % 16)
        ct = Cipher(algorithms.AES(key), m(iv)).encryptor().update(data)

    out = path + '.enc'
    with open(out, 'wb') as f:
        f.write(iv + ct)

    size = os.path.getsize(out)
    log_ok(f"Encrypted: {path}")
    log_dim(f"→ {out}  ({size} bytes)")

def decrypt_file(path, cipher, mode, key):
    with open(path, 'rb') as f:
        data = f.read()

    iv, ct = data[:16], data[16:]

    if cipher == 'chacha20':
        pt = Cipher(algorithms.ChaCha20(key, iv), mode=None).decryptor().update(ct)
    else:
        m = {'cbc': modes.CBC, 'ctr': modes.CTR, 'ofb': modes.OFB, 'cfb': modes.CFB}[mode]
        pt = Cipher(algorithms.AES(key), m(iv)).decryptor().update(ct)
        if mode == 'cbc':
            pt = pt.rstrip(b'\x00')

    out = path.removesuffix('.enc')
    with open(out, 'wb') as f:
        f.write(pt)

    log_ok(f"Decrypted: {path}")
    log_dim(f"→ {out}  ({len(pt)} bytes)")

def process(path, action, cipher, mode, key, nonce):
    if os.path.isfile(path):
        if action == 'encrypt':
            encrypt_file(path, cipher, mode, key, nonce)
        else:
            decrypt_file(path, cipher, mode, key)
    elif os.path.isdir(path):
        files = [(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs]
        if action == 'decrypt':
            files = [f for f in files if f.endswith('.enc')]
        log_info(f"Found {Y}{len(files)}{X} file(s) in {W}{path}{X}")
        for fp in files:
            if action == 'encrypt':
                encrypt_file(fp, cipher, mode, key, nonce)
            else:
                decrypt_file(fp, cipher, mode, key)

# ── cli ──────────────────────────────────────────────────
print(BANNER)

p = argparse.ArgumentParser(add_help=False)
p.add_argument('action', choices=['encrypt', 'decrypt'])
p.add_argument('path')
p.add_argument('--cipher', choices=['aes', 'chacha20'], required=True)
p.add_argument('--mode',   choices=['cbc', 'ctr', 'ofb', 'cfb'])
p.add_argument('--key',    required=True)
p.add_argument('--nonce')
args = p.parse_args()

try:
    key = bytes.fromhex(args.key)
except ValueError:
    log_err("Key must be hex-encoded (e.g. deadbeef...)")
    log_dim("128-bit = 32 hex chars | 192-bit = 48 | 256-bit = 64")
    exit(1)

if len(key) not in (16, 24, 32):
    log_err(f"Invalid key length: {len(key)*8} bits. Must be 128, 192, or 256.")
    exit(1)

if args.cipher == 'chacha20' and len(key) != 32:
    log_err("ChaCha20 requires a 256-bit key (64 hex chars).")
    exit(1)

if args.cipher == 'aes' and not args.mode:
    log_err("AES requires --mode (cbc, ctr, ofb, cfb)")
    exit(1)

# print job summary
action_label = f"{G}ENCRYPT{X}" if args.action == 'encrypt' else f"{R}DECRYPT{X}"
section(f"{args.action.upper()}ING")
log_info(f"Action : {action_label}")
log_info(f"Target : {W}{args.path}{X}")
log_info(f"Cipher : {Y}{args.cipher.upper()}{X}" + (f"  Mode: {Y}{args.mode.upper()}{X}" if args.mode else ""))
log_info(f"Key    : {DIM}{args.key[:8]}...{args.key[-4:]}  ({len(key)*8}-bit){X}")
print()

process(args.path, args.action, args.cipher, args.mode, key, args.nonce)

print(f"\n{G}{'─'*50}")
print(f"  Done!{X}\n")
