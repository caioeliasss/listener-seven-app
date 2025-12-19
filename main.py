import socket
import requests
import time
import json
import os

# Configurações
CODIGO_POSTO = "00001"
HOST = "10.0.0.91"
# HOST = "127.0.0.1"
PORT = 3000
ARQUIVO_PROCESSADOS = "abastecimentos_processados.json"

# Carrega IDs já processados
def carregar_processados():
    if os.path.exists(ARQUIVO_PROCESSADOS):
        with open(ARQUIVO_PROCESSADOS, 'r') as f:
            return set(json.load(f))
    return set()

# Salva IDs processados
def salvar_processados(processados):
    with open(ARQUIVO_PROCESSADOS, 'w') as f:
        json.dump(list(processados), f)

# Conjunto de abastecimentos já processados (pelo índice)
abastecimentos_processados = carregar_processados()

def checksum(cmd):
    total = sum(ord(c) for c in cmd)
    return format(total & 0xFF, '02X')

def build_cmd(data):
    cmd = f">{data}"
    return cmd + checksum(cmd)

def send_cmd(sock, data):
    frame = build_cmd(data)
    sock.sendall(frame.encode())
    resp = sock.recv(2048).decode()
    return resp

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

print("🟢 Conectado ao HorusTech")
print(f"📝 {len(abastecimentos_processados)} abastecimentos já processados")
print("⚠️  MODO SEM MOVER PONTEIRO - Rastreando por ID\n")

while True:
    try:
        # Comando 02 - ler abastecimento
        resp = send_cmd(sock, "?000202")

        if len(resp) > 10 and resp[0:2] == ">!":
            # Extrai dados
            data = resp.split(">!")[1][:-2]
            
            # ID único do abastecimento (NNNNNN)
            idx = data[6:12]
            
            # ✅ Verifica se JÁ processou este ID
            if idx in abastecimentos_processados:
                # Silencioso - já foi enviado antes
                time.sleep(2)
                continue
            
            # NOVO abastecimento! Processa...
            print(f"📥 Novo abastecimento detectado (ID: {idx})")
            print(f"   Frame: {resp}")
            
            bico = data[12:14]
            comb = data[14:16]
            tanque = data[16:18]
            valor = data[18:24]
            litros = data[24:30]
            preco = data[30:34]
            casas_valor = int(data[34])
            casas_litro = int(data[35])
            casas_preco = int(data[36])

            valor_num = int(valor) / (10 ** casas_valor)
            litros_num = int(litros) / (10 ** casas_litro)
            preco_num = int(preco) / (10 ** casas_preco)

            print(f"   Bico: {bico} | Combustível: {comb} | Valor: R$ {valor_num:.2f} | Litros: {litros_num:.3f}L")
            
            try:
                response = requests.post(
                    "https://cashback-app-seven-production.up.railway.app/api/abastecimentos-temp",
                    json={
                        "codigoPosto": CODIGO_POSTO,
                        "bico": bico,
                        "combustivel": comb,
                        "valor": valor_num,
                        "litros": litros_num,
                        "preco": preco_num
                    },
                    timeout=5
                )
                
                if response.status_code == 201:
                    result = response.json()
                    
                    # ✅ MARCA COMO PROCESSADO
                    abastecimentos_processados.add(idx)
                    salvar_processados(abastecimentos_processados)
                    
                    if result.get('tipo') == 'definitivo':
                        print(f"   ✓ Vinculado automaticamente ao cliente!")
                    else:
                        print(f"   ⚠ Aguardando cliente vincular...")
                    
                    print(f"   ✓ Salvo com sucesso (Total processados: {len(abastecimentos_processados)})")
                    print(f"   ⚠️  PONTEIRO NÃO MOVIDO (modo seguro)\n")
                else:
                    print(f"   ✗ Erro API: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ✗ Timeout na API - ID {idx} NÃO marcado (tentará novamente)")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Erro: {e}")
        
        # Limpeza: remove IDs muito antigos (opcional, após 100 registros)
        if len(abastecimentos_processados) > 100:
            print("🗑️  Limpando cache antigo...")
            abastecimentos_processados.clear()
            salvar_processados(abastecimentos_processados)
                
    except Exception as e:
        print(f"❌ Erro no loop: {e}")
    
    time.sleep(2)