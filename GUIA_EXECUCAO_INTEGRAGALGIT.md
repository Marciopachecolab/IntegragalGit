# 🚀 Guia Completo de Execução - Sistema IntegragalGit

## 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Preparação do Ambiente](#preparação-do-ambiente)
3. [Configuração Inicial](#configuração-inicial)
4. [Execução do Sistema](#execução-do-sistema)
5. [Testes e Validação](#testes-e-validação)
6. [Troubleshooting](#troubleshooting)
7. [Operações de Manutenção](#operações-de-manutenção)

---

## 🔧 Pré-requisitos

### Sistema Operacional
- **Linux** (recomendado: Ubuntu 20.04+, CentOS 8+, ou similar)
- **Windows** (com WSL2 + X Server) ou **macOS** (com XQuartz)

### Ferramentas Necessárias
- Python 3.8 ou superior
- Git
- Servidor X (para interface gráfica)
- Gerenciador de pacotes (apt, yum, brew)

### Verificação de Versões
```bash
python3 --version    # Deve ser >= 3.8
git --version        # Qualquer versão recente
```

---

## 🛠️ Preparação do Ambiente

### Passo 1: Clonar o Repositório
```bash
# Navegar para diretório de trabalho
cd /seu/diretorio/de/trabalho

# Clonar repositório
git clone https://github.com/Marciopachecolab/IntegragalGit.git
cd IntegragalGit
```

### Passo 2: Configurar Servidor X (Linux)
```bash
# Instalar servidor X (Ubuntu/Debian)
sudo apt update
sudo apt install -y xorg-server xterm dbus-x11

# Instalar servidor X (CentOS/RHEL)
sudo yum install -y xorg-x11-server-Xorg xterm dbus-x11

# Verificar se X está funcionando
echo $DISPLAY
```

### Passo 3: Instalar Python e Dependências
```bash
# Instalar uv (gerenciador de pacotes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# OU instalar via pip
pip3 install uv

# Navegar para diretório do projeto
cd /caminho/para/IntegragalGit

# Instalar dependências do sistema
uv pip install -r requirements.txt
```

### Passo 4: Verificar Instalação
```bash
# Testar importação de módulos críticos
python3 -c "
import customtkinter
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
import psycopg2
print('✅ Todas as dependências instaladas com sucesso!')
"
```

---

## ⚙️ Configuração Inicial

### Passo 1: Configurar Banco de Dados (se necessário)
```bash
# Verificar se PostgreSQL está instalado
sudo systemctl status postgresql

# Se não estiver instalado (Ubuntu):
sudo apt install postgresql postgresql-contrib

# Criar banco de dados (se necessário)
sudo -u postgres psql -c "CREATE DATABASE integragalgit;"
sudo -u postgres psql -c "CREATE USER integragal WITH PASSWORD 'sua_senha_aqui';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE integragalgit TO integragal;"
```

### Passo 2: Configurar Variáveis de Ambiente
```bash
# Criar arquivo de configuração (se não existir)
cat > .env << EOF
# Configurações do Sistema IntegragalGit
DISPLAY=:0
PYTHONPATH=/caminho/para/IntegragalGit
GAL_DATABASE_URL=postgresql://integragal:sua_senha_aqui@localhost:5432/integragalgit
EOF

# Carregar variáveis
source .env
```

### Passo 3: Verificar Configurações
```bash
# Verificar se arquivo de configuração existe
ls -la config.json

# Verificar conteúdo (sem expor senhas)
python3 -c "
import json
with open('config.json', 'r') as f:
    config = json.load(f)
    print('Configuração carregada:')
    print(f'- GAL URL: {config.get(\"gal_url\", \"N/A\")}')
    print(f'- Timeout: {config.get(\"timeout\", \"N/A\")}')
    print(f'- Logs: {config.get(\"log_level\", \"N/A\")}')
"
```

---

## 🚀 Execução do Sistema

### Método 1: Execução Direta (Recomendado)

#### Terminal 1 - Iniciar Servidor X (se necessário)
```bash
# Iniciar servidor X (caso não esteja rodando)
startx &

# Aguardar inicialização
sleep 5

# Verificar se display está ativo
echo $DISPLAY
```

#### Terminal 2 - Executar Sistema
```bash
# Navegar para diretório do projeto
cd /caminho/para/IntegragalGit

# Executar sistema
python3 main.py
```

### Método 2: Execução com Configuração Explícita
```bash
# Definir display explicitamente
export DISPLAY=:0

# Executar com verbose
python3 -v main.py

# OU executar com logging detalhado
python3 main.py --debug
```

### Método 3: Execução em Background
```bash
# Executar em segundo plano
nohup python3 main.py > sistema.log 2>&1 &

# Verificar se está rodando
ps aux | grep main.py

# Ver logs em tempo real
tail -f sistema.log
```

---

## 🧪 Testes e Validação

### Teste 1: Verificação de Módulos
```bash
# Executar script de validação
python3 testar_pos_limpeza.py
```

**Resultado Esperado:**
```
🎉 SISTEMA FUNCIONANDO CORRETAMENTE PÓS-ANÁLISE!
✅ Importações críticas: 8/8 funcionando
✅ Arquivos essenciais: 8/8 presentes
✅ Usuário marcio: OK (senha: flafla)
✅ Todos os módulos essenciais operacionais
```

### Teste 2: Verificação de Importação Individual
```bash
# Testar cada módulo individualmente
python3 -c "
try:
    import ui.main_window
    print('✅ ui.main_window')
except Exception as e:
    print(f'❌ ui.main_window: {e}')

try:
    import ui.menu_handler
    print('✅ ui.menu_handler')
except Exception as e:
    print(f'❌ ui.menu_handler: {e}')

# ... (repetir para todos os módulos)
"
```

### Teste 3: Verificação de Credenciais
```bash
# Verificar se usuário marcio existe
python3 -c "
import pandas as pd
df = pd.read_csv('banco/credeciais.csv')
if 'marcio' in df['usuario'].values:
    print('✅ Usuário marcio encontrado')
    print(f'Hash da senha: {df[df[\"usuario\"]==\"marcio\"][\"senha\"].iloc[0][:20]}...')
else:
    print('❌ Usuário marcio não encontrado')
"
```

---

## 🔍 Troubleshooting

### Problema 1: Erro "cannot connect to X server"
```bash
# Solução 1: Verificar servidor X
ps aux | grep X
echo $DISPLAY

# Solução 2: Iniciar servidor X
startx &

# Solução 3: Usar Xvfb (sem interface visual)
sudo apt install xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

### Problema 2: Erro de permissão de arquivo
```bash
# Verificar permissões
ls -la banco/
chmod 755 banco/
chmod 644 banco/credenciais.csv

# Verificar proprietário
sudo chown $USER:$USER banco/ -R
```

### Problema 3: Módulo customtkinter não encontrado
```bash
# Reinstalar dependências
uv pip install -r requirements.txt --force-reinstall

# Verificar instalação
python3 -c "import customtkinter; print(customtkinter.__version__)"
```

### Problema 4: Erro de conexão com banco
```bash
# Verificar status PostgreSQL
sudo systemctl status postgresql

# Verificar conexão manual
psql -h localhost -U integragal -d integragalgit

# Verificar logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Problema 5: Interface não aparece
```bash
# Verificar se DISPLAY está configurado
echo $DISPLAY

# Testar interface básica
python3 -c "
import customtkinter
root = customtkinter.CTk()
root.title('Teste')
root.geometry('200x100')
label = customtkinter.CTkLabel(root, text='Teste de Interface')
label.pack(pady=20)
print('Interface criada com sucesso!')
# root.mainloop()  # Não executar para não travar
"
```

---

## 🧹 Operações de Manutenção

### Limpeza de Arquivos Temporários
```bash
# Executar limpeza manual
bash limpar_arquivos_desnecessarios.sh

# Verificar espaço liberado
du -sh _archive/ 2>/dev/null || echo "Diretório _archive/ não existe (já removido)"
```

### Verificação de Logs
```bash
# Ver logs do sistema
tail -f logs/sistema.log

# Verificar erros recentes
grep -i "error\|exception" logs/sistema.log | tail -10

# Limpar logs antigos (opcional)
find logs/ -name "*.log" -mtime +30 -delete
```

### Backup de Configurações
```bash
# Criar backup das configurações
tar -czf backup_config_$(date +%Y%m%d_%H%M%S).tar.gz \
    config.json \
    banco/credenciais.csv \
    .env \
    logs/

# Restaurar backup
tar -xzf backup_config_YYYYMMDD_HHMMSS.tar.gz
```

### Verificação de Integridade
```bash
# Verificar todos os arquivos essenciais
python3 validar_resumo.py

# Verificar dependências do sistema
python3 -c "
import sys
required_modules = [
    'customtkinter', 'pandas', 'matplotlib', 'bcrypt', 
    'psycopg2', 'selenium', 'openpyxl', 'numpy'
]
for module in required_modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
"
```

---

## 📊 Monitoramento de Performance

### Verificar Uso de Memória
```bash
# Monitorar processo do sistema
top -p $(pgrep -f "python.*main.py")

# Verificar uso de recursos
ps aux | grep main.py | grep -v grep
```

### Verificar Conectividade
```bash
# Testar conectividade com GAL
curl -I http://seu-servidor-gal:8080/gal/rest/

# Verificar portas abertas
netstat -tlnp | grep python
```

---

## 🆘 Comandos de Emergência

### Parar Sistema em Execução
```bash
# Encontrar e matar processo
pkill -f "python.*main.py"

# OU parar processo específico
kill $(pgrep -f main.py)
```

### Restaurar Configuração Padrão
```bash
# Restaurar a partir do backup mais recente
tar -xzf backup_config_*.tar.gz --strip-components=0

# OU resetar credenciais (CUIDADO!)
echo "usuario,senha,nivel_acesso" > banco/credenciais.csv
```

### Recriar Banco de Dados
```bash
# Drop e recreate (CUIDADO - PERDE DADOS!)
sudo -u postgres dropdb integragalgit
sudo -u postgres createdb integragalgit
sudo -u postgres psql -d integragalgit -c "
CREATE USER integragal WITH PASSWORD 'nova_senha_aqui';
GRANT ALL PRIVILEGES ON DATABASE integragalgit TO integragal;
"
```

---

## ✅ Checklist Final de Verificação

### Antes da Primeira Execução:
- [ ] Repositório clonado e atualizado
- [ ] Dependências Python instaladas
- [ ] Servidor X configurado e funcionando
- [ ] Banco de dados PostgreSQL configurado
- [ ] Arquivo .env configurado
- [ ] Usuário marcio criado com senha flafla
- [ ] Validação executar com sucesso

### Durante a Execução:
- [ ] Interface gráfica abre sem erros
- [ ] Login funciona com usuário marcio
- [ ] Navegação entre telas funciona
- [ ] Funcionalidades principais acessíveis
- [ ] Logs não apresentam erros críticos

### Após a Execução:
- [ ] Sistema pode ser fechado normalmente
- [ ] Logs estão sendo gravados corretamente
- [ ] Backup automático foi criado (se configurado)
- [ ] Arquivos temporários podem ser limpos

---

## 📞 Suporte

Em caso de problemas não cobertos neste guia:

1. **Verificar logs**: `tail -f logs/sistema.log`
2. **Executar validação**: `python3 validar_resumo.py`
3. **Reiniciar servidor X**: `sudo systemctl restart lightdm`
4. **Verificar dependências**: `pip list | grep -E "(customtkinter|pandas|matplotlib)"`

---

*Última atualização: 02/12/2025 - Versão do Guia: 1.0*