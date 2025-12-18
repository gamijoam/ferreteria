import os
from dotenv import load_dotenv

target_env = r"c:\Users\Equipo\Documents\ferreteria\ferreteria_refactor\backend_api\.env"

print(f"--- Inspecting {target_env} ---")

if os.path.exists(target_env):
    # Read binary to find bad bytes
    try:
        with open(target_env, 'rb') as f:
            content = f.read()
            print(f"File size: {len(content)} bytes")
            
            # Print first few chars to check encoding/BOM
            print(f"Start bytes: {content[:20]}")
            
            # Check for 0xAB
            if b'\xab' in content:
                print("!!! FOUND BYTE 0xAB (Invalid Start Byte) in file !!!")
                pos = content.find(b'\xab')
                print(f"At position: {pos}")
                snippet = content[max(0, pos-20):min(len(content), pos+20)]
                print(f"Context: {snippet}")
            else:
                print("Byte 0xAB not found in file raw content.")
                
    except Exception as e:
        print(f"Error reading file: {e}")

    # Load and check vars
    load_dotenv(target_env)
else:
    print("File not found!")

# Check Keys
for key in ["DATABASE_URL", "DB_URL"]:
    val = os.getenv(key)
    if val:
        print(f"\nKey '{key}' found.")
        print(f"Repr: {repr(val)}")
        try:
            val.encode('utf-8')
            print("Encoding: OK")
        except Exception as e:
            print(f"Encoding Error: {e}")
    else:
        print(f"\nKey '{key}' NOT found.")
