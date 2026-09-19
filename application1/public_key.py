# generate_keys.py  (run once)
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import pdb;pdb.set_trace()
KEYS_DIR = Path("keys")          # create a folder named "keys"
KEYS_DIR.mkdir(exist_ok=True)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Private key (keep this secret!)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
(KEYS_DIR / "private_key.pem").write_bytes(private_pem)

# Public key (this one goes to the frontend)
public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
(KEYS_DIR / "public_key.pem").write_bytes(public_pem)

print("Keys generated in ./keys/")