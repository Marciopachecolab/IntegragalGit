# Instruções para Execução no Windows

## Problema Identificado
O sistema estava usando caminhos relativos que funcionam no Linux, mas podem ter problemas no Windows.

## Soluções Implementadas

### 1. Caminhos Absolutos
- auth_service.py agora usa caminhos absolutos mais robustos
- Múltiplos fallbacks para encontrar os arquivos corretos
- Melhor tratamento de erros

### 2. Encoding e Separadores
- Melhor detecção de separadores CSV (priorizando ';')
- Múltiplas tentativas de encoding (utf-8-sig, utf-8, latin-1)
- Fallbacks para diferentes versões do Windows

### 3. Scripts de Execução
- executar_integragal.bat: Script principal para Windows
- validar_credenciais_windows.py: Validador de credenciais

## Como Usar

### Opção 1: Script Batch (Recomendado)
1. Vá para: `C:\Users\marci\Downloads\Integragal`
2. Execute: `executar_integragal.bat`

### Opção 2: Linha de Comando
1. Abra Command Prompt ou PowerShell
2. Navegue até: `C:\Users\marci\Downloads\Integragal`
3. Execute: `python IntegragalGit/main.py`

### Opção 3: Validação Primeiro
1. Execute: `python validar_credenciais_windows.py`
2. Se der sucesso, execute o sistema normalmente

## Estrutura de Diretórios Necessária
```
C:\Users\marci\Downloads\Integragal\
├── executar_integragal.bat
├── validar_credenciais_windows.py
├── IntegragalGit\
│   ├── main.py
│   ├── banco\
│   │   └── credenciais.csv
│   ├── autenticacao\
│   │   └── auth_service.py
│   └── utils\
│       └── io_utils.py
```

## Credenciais de Teste
- Usuário: marcio
- Senha: flafla

## Troubleshooting

### Se o arquivo não for encontrado:
- Verifique se você está no diretório correto: `C:\Users\marci\Downloads\Integragal`
- Execute o validador primeiro: `python validar_credenciais_windows.py`

### Se houver erros de encoding:
- O sistema agora tenta múltiplos encodings automaticamente
- Se persistir, verifique se o arquivo credenciais.csv está em UTF-8

### Se a autenticação falhar:
- Use o validador para verificar se as credenciais estão corretas
- O hash da senha 'flafla' é: $2b$12$tBZZ5hWsiWr7XmsRZG7i4.CSUuP4bok2LHDZ/8nQ6jXnB4rEh9762

### Se houver problemas de dependências:
```bash
pip install pandas customtkinter bcrypt
```

## Logs
Os logs são salvos em `logs/sistema.log` no diretório do programa.
