
import os
from datetime import datetime
from datetime import timedelta                                    
from jose import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

# 1. Generate new RSA Keypair
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

private_key = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key = key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print("\n" + "="*50)
print("🔑 NEW PUBLIC KEY (Update license_guard.py with this):")
print("="*50)
print(public_key.decode('utf-8'))
print("="*50 + "\n")

# 2. Create License Token (Valid for 100 years)
payload = {
    "sub": "DEV-LICENSE-RECOVERY",
    "name": "Ferreteria Development",
    "type": "ENTERPRISE",
    "features": ["ALL"],
    "machine_id": "*",  # Wildcard for dev
    "exp": datetime.utcnow() + timedelta(days=36500), # ~100 years
    "iat": datetime.utcnow()
}

token = jwt.encode(
    payload,
    private_key.decode('utf-8'),
    algorithm='RS256'
)

# 3. Write license.key
license_path = Path("license.key")
with open(license_path, "w") as f:
    f.write(token)

print(f"✅ Created new license file at: {license_path.absolute()}")
