import socket

HOST = "0.0.0.0"  # Escuta em todas as interfaces
PORT = 3000

def checksum(cmd):
    total = sum(ord(c) for c in cmd)
    return format(total & 0xFF, '02X')

def build_response(data):
    cmd = f">!{data}"
    return cmd + checksum(cmd)

# Cria servidor socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print(f"Simulador HorusTech rodando na porta {PORT}")
print("Aguardando conexão...")

conn, addr = server.accept()
print(f"Cliente conectado: {addr}")

# Flag para controlar se há abastecimento pendente
tem_abastecimento = True

try:
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        print(f"Recebido: {data}")
        
        # Se receber comando 02 (ler abastecimento)
        if "?000202" in data:
            if tem_abastecimento:
                # Simula um abastecimento:
                # EEEEEE = 000202 (código)
                # NNNNNN = 000001 (índice)
                # BB = 01 (bico 1)
                # CC = 01 (combustível tipo 1 - gasolina comum)
                # AA = 01 (tanque 1)
                # TTTTTT = 010000 (valor R$ 100,00)
                # LLLLLL = 020000 (litros 20,000)
                # PPPP = 0500 (preço R$ 5,00)
                # D1 = 2 (2 casas decimais no valor)
                # D2 = 3 (3 casas decimais no litro)
                # D3 = 2 (2 casas decimais no preço)
                
                abastecimento = "0002020000010101010100000200000500232"
                response = build_response(abastecimento)
                conn.sendall(response.encode())
                print(f"Enviado: {response}")
                print("Decodificado:")
                print("  Bico: 01")
                print("  Combustível: 01")
                print("  Valor: R$ 100,00")
                print("  Litros: 20,000 L")
                print("  Preço: R$ 5,00/L")
            else:
                # Sem abastecimento pendente - resposta curta
                response = build_response("000202")
                conn.sendall(response.encode())
                print(f"Sem abastecimento pendente. Enviado: {response}")
        
        # Se receber comando 06 (mover ponteiro)
        elif "?000206" in data:
            tem_abastecimento = False  # Marca como lido
            response = build_response("000206")
            conn.sendall(response.encode())
            print(f"Ponteiro movido. Enviado: {response}")
        
        else:
            # Resposta genérica
            response = ">!OK" + checksum(">!OK")
            conn.sendall(response.encode())
            print(f"Enviado: {response}")

except KeyboardInterrupt:
    print("\nEncerrando servidor...")
finally:
    conn.close()
    server.close()
    print("Servidor fechado")
