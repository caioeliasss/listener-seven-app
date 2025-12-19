# Roteiro de instalação (do zero) + manter rodando após reboot (Windows)

Este projeto é um listener em Python ([main.py](main.py)) que conecta via TCP no equipamento HorusTech e envia abastecimentos para uma API.

## 0) Pré-requisitos

- Windows 10/11 com acesso de administrador
- Acesso de rede ao HorusTech (IP/porta)
- Saída HTTPS liberada para `https://cashback-app-seven-production.up.railway.app`

Instalar:

- **Python 3.10+** (recomendado 3.11/3.12)
- **Node.js LTS** (vem com `npm`)
- **PM2** (via npm)

https://www.python.org/downloads/
https://nodejs.org/pt/download
npm install pm2 -g
npm i -g pm2-windows-startup

## 1) Clonar/copiar o projeto

Copie a pasta do projeto para o novo PC, por exemplo:

- `C:\apps\listener-seven-app\`

Garanta que estes arquivos existam:

- `main.py`
- `abastecimentos_processados.json` (pode começar vazio, mas o arquivo será criado automaticamente)

## 2) Configurar Python (venv) e dependências

Abra **PowerShell** na pasta do projeto:

```powershell
cd C:\apps\listener-seven-app
python --version
```

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale dependências:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Ajustar configurações do listener

Edite as constantes no topo de [main.py](main.py):

- `CODIGO_POSTO` (ex: `"00001"`)
- `HOST` (IP do HorusTech, ex: `"10.0.0.91"`)
- `PORT` (porta TCP, ex: `3000`)

Dica rápida para descobrir porta acessível:

```powershell
.\.venv\Scripts\python.exe test_connection.py
```

## 4) Teste manual (antes do PM2)

Ainda com o venv ativo:

```powershell
python main.py
```

Se conectou, você verá algo como “Conectado ao HorusTech”. Para parar: `Ctrl+C`.

Opcional (simulador local):

- Em um terminal, rode `python simula_horustech.py`
- Ajuste `HOST = "127.0.0.1"` em `main.py`

## 5) Instalar Node/npm e PM2

Instale **Node.js LTS** (site oficial) e depois confirme:

```powershell
node -v
npm -v
```

Instale PM2 globalmente:

```powershell
npm i -g pm2
pm2 -v
```

## 6) Rodar o Python via PM2

Importante: a forma mais confiável no Windows é apontar o **Python do venv** como interpreter.

Na pasta do projeto:

```powershell
cd C:\apps\listener-seven-app
pm2 start main.py --name listener-seven --interpreter .\.venv\Scripts\python.exe --time
pm2 status
pm2 logs listener-seven
```

Persistir a lista de processos do PM2:

```powershell
pm2 save
```

Comandos úteis:

```powershell
pm2 restart listener-seven
pm2 stop listener-seven
pm2 delete listener-seven
pm2 logs listener-seven --lines 200
```

## 7) Subir automaticamente após reboot (Windows)

### Opção A (recomendada): pm2-windows-startup

Instale o helper de startup:

```powershell
npm i -g pm2-windows-startup
pm2-startup install
```

Depois garanta que seu processo está salvo:

```powershell
pm2 save
```

Reinicie o PC e valide:

```powershell
pm2 status
```

### Opção B: Agendador de Tarefas (Task Scheduler)

Se a Opção A não funcionar no seu Windows, faça assim:

1. Abra **Task Scheduler** → **Create Task...**
2. Aba **General**:
   - Name: `PM2 Resurrect`
   - Marque **Run whether user is logged on or not**
   - Marque **Run with highest privileges**
3. Aba **Triggers**:
   - **New...** → Begin the task: **At startup**
4. Aba **Actions**:
   - **New...** → Action: **Start a program**
   - Program/script: `C:\Program Files\nodejs\pm2.cmd` (ajuste se necessário)
   - Add arguments: `resurrect`
   - Start in: `C:\apps\listener-seven-app`
5. Clique OK e informe credenciais se solicitado.

Após reboot, confira:

```powershell
pm2 status
```

## 8) Observações importantes

- O arquivo `abastecimentos_processados.json` é usado para evitar reenvio. Por isso:
  - Rode sempre com o **Working Directory** na pasta do projeto.
  - Faça backup desse arquivo se você não quiser reprocessar IDs após migração.
- Se o processo “cair”, o PM2 tende a reiniciar automaticamente; você pode ver o motivo em `pm2 logs`.
- Se trocar o IP do HorusTech ou a porta, lembre de editar [main.py](main.py) e reiniciar: `pm2 restart listener-seven`.
