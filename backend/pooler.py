# language: python
# Guarda como check_pooler.py y ejecútalo con: python3 check_pooler.py
import socket, sys, time

host = "aws-1-us-east-2.pooler.supabase.com"
port = 6543
timeout = 5

print("getaddrinfo:")
try:
    addrs = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    for a in addrs:
        print(a)
except Exception as e:
    print("getaddrinfo error:", e)

print("\ntry create_connection:")
for attempt in range(1,4):
    try:
        s = socket.create_connection((host, port), timeout)
        s.close()
        print(f"connected on attempt {attempt}")
        sys.exit(0)
    except Exception as e:
        print(f"attempt {attempt} failed:", repr(e))
        time.sleep(1)
print("all attempts failed")
sys.exit(2)