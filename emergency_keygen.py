import sys
try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend

    print("Generating keys...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()
    
    # Export Public
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open("new_public.txt", "wb") as f:
        f.write(pem)
        
    print("SUCCESS")
except Exception as e:
    with open("keygen_error.txt", "w") as f:
        f.write(str(e))
