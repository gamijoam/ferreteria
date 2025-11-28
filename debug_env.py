import socket
import os
import psycopg2
import sys

def check_port(host, port):
    print(f"Checking {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        print("Port is OPEN.")
        s.close()
        return True
    except Exception as e:
        print(f"Port is CLOSED or unreachable: {e}")
        return False

# Check if Postgres is running
is_open = check_port("127.0.0.1", 5432)

if not is_open:
    print("\nWARNING: Postgres does not seem to be running on port 5432.")
    print("This is likely why the connection fails.")
    print("The UnicodeDecodeError is probably a side effect of psycopg2 trying to decode a localized 'Connection refused' message.")

print("\nTesting with PGCLIENTENCODING=utf-8...")
os.environ["PGCLIENTENCODING"] = "utf-8"
try:
    conn = psycopg2.connect("postgresql://postgres:password@localhost:5432/ferreteria_db")
    print("Success!")
    conn.close()
except Exception as e:
    print(f"Failed: {e}")

print("\nTesting with PGCLIENTENCODING=latin1...")
os.environ["PGCLIENTENCODING"] = "latin1"
try:
    conn = psycopg2.connect("postgresql://postgres:password@localhost:5432/ferreteria_db")
    print("Success!")
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
