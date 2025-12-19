import socket
import sys

HOST = "10.0.0.91"
PORTAS = [3000, 8080, 5000, 9000, 10001, 23, 80]

print("🔍 Testando conexões com HorusTech...\n")

for porta in PORTAS:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        resultado = sock.connect_ex((HOST, porta))
        
        if resultado == 0:
            print(f"✅ Porta {porta} - ABERTA e ACESSÍVEL")
            sock.close()
        else:
            print(f"❌ Porta {porta} - Fechada/Filtrada")
            
    except Exception as e:
        print(f"❌ Porta {porta} - Erro: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

print("\n💡 Use a porta que aparecer como ABERTA no main.py")
