#!/bin/bash

# ========================================
# 🚀 Script de Configuração Automática - IntegragalGit
# Versão: 1.0
# Data: 02/12/2025
# ========================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅ SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️ ATENÇÃO]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ ERRO]${NC} $1"
}

# Verificar se está no diretório correto
check_directory() {
    if [[ ! -f "main.py" ]]; then
        print_error "Arquivo main.py não encontrado!"
        print_status "Execute este script no diretório raiz do projeto IntegragalGit"
        exit 1
    fi
    print_success "Diretório do projeto encontrado"
}

# Instalar dependências do sistema
install_system_deps() {
    print_status "Instalando dependências do sistema..."
    
    # Detectar distribuição Linux
    if command -v apt &> /dev/null; then
        print_status "Detectado Ubuntu/Debian - usando apt"
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv git xorg-server xterm dbus-x11 postgresql postgresql-contrib xvfb
    elif command -v yum &> /dev/null; then
        print_status "Detectado CentOS/RHEL - usando yum"
        sudo yum install -y python3 python3-pip git xorg-x11-server-Xorg xterm dbus-x11 postgresql postgresql-contrib xorg-x11-server-Xvfb
    elif command -v brew &> /dev/null; then
        print_status "Detectado macOS - usando Homebrew"
        brew install python3 git postgresql
    else
        print_warning "Não foi possível detectar o gerenciador de pacotes"
        print_status "Instale manualmente: Python 3.8+, Git, PostgreSQL, Servidor X"
    fi
    
    print_success "Dependências do sistema instaladas"
}

# Instalar uv se não estiver disponível
install_uv() {
    if ! command -v uv &> /dev/null; then
        print_status "Instalando uv (gerenciador de pacotes Python)..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc
        source ~/.profile
        
        # Tentar adicionar ao PATH atual
        if [[ -f "$HOME/.local/bin/uv" ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
    else
        print_success "uv já está instalado"
    fi
}

# Instalar dependências Python
install_python_deps() {
    print_status "Instalando dependências Python..."
    
    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        python3 -m pip install -r requirements.txt
    fi
    
    print_success "Dependências Python instaladas"
}

# Configurar PostgreSQL
setup_postgresql() {
    print_status "Configurando PostgreSQL..."
    
    # Iniciar serviço PostgreSQL
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql || print_warning "Não foi possível iniciar PostgreSQL via systemctl"
        sudo systemctl enable postgresql
    fi
    
    # Aguardar PostgreSQL inicializar
    sleep 3
    
    # Criar banco de dados e usuário
    sudo -u postgres psql << EOF
        CREATE DATABASE integragalgit;
        CREATE USER integragal WITH PASSWORD 'sua_senha_aqui';
        GRANT ALL PRIVILEGES ON DATABASE integragalgit TO integragal;
        \q
EOF
    
    print_success "PostgreSQL configurado"
}

# Configurar variáveis de ambiente
setup_environment() {
    print_status "Configurando variáveis de ambiente..."
    
    cat > .env << EOF
# Configurações do Sistema IntegragalGit
DISPLAY=:0
PYTHONPATH=$(pwd)
GAL_DATABASE_URL=postgresql://integragal:sua_senha_aqui@localhost:5432/integragalgit
EOF
    
    print_success "Arquivo .env criado"
}

# Iniciar servidor X se necessário
start_x_server() {
    print_status "Verificando servidor X..."
    
    if [[ -z "$DISPLAY" ]]; then
        print_status "DISPLAY não configurado, iniciando Xvfb..."
        # Tentar iniciar Xvfb
        if command -v Xvfb &> /dev/null; then
            Xvfb :99 -screen 0 1024x768x24 &
            XVFB_PID=$!
            export DISPLAY=:99
            sleep 2
            print_success "Xvfb iniciado (PID: $XVFB_PID)"
        else
            print_warning "Xvfb não encontrado. Configure DISPLAY manualmente:"
            print_status "export DISPLAY=:0"
        fi
    else
        print_success "DISPLAY já configurado: $DISPLAY"
    fi
}

# Executar validações
run_validations() {
    print_status "Executando validações do sistema..."
    
    # Testar importações críticas
    python3 << 'EOF'
import sys
required_modules = [
    'customtkinter', 'pandas', 'matplotlib', 'bcrypt', 
    'psycopg2', 'selenium', 'openpyxl', 'numpy'
]

failed_imports = []
for module in required_modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
        failed_imports.append(module)

if failed_imports:
    print(f"\n❌ Módulos com falha: {', '.join(failed_imports)}")
    sys.exit(1)
else:
    print("\n✅ Todas as importações críticas funcionaram!")
EOF
    
    if [[ $? -eq 0 ]]; then
        print_success "Importações testadas com sucesso"
    else
        print_error "Falha nas importações críticas"
        exit 1
    fi
}

# Criar scripts de conveniência
create_convenience_scripts() {
    print_status "Criando scripts de conveniência..."
    
    # Script de execução rápida
    cat > executar_sistema.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env
export DISPLAY=:0
python3 main.py
EOF
    chmod +x executar_sistema.sh
    
    # Script de teste rápido
    cat > testar_sistema.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 testar_pos_limpeza.py
EOF
    chmod +x testar_sistema.sh
    
    # Script de limpeza
    cat > limpar_sistema.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
bash limpar_arquivos_desnecessarios.sh
EOF
    chmod +x limpar_sistema.sh
    
    print_success "Scripts de conveniência criados"
}

# Exibir resumo final
show_summary() {
    echo ""
    echo "🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "=================================="
    echo ""
    print_success "Sistema configurado e pronto para uso"
    echo ""
    echo "📋 PRÓXIMOS PASSOS:"
    echo "  1. Execute: ./executar_sistema.sh"
    echo "  2. Faça login com: usuário 'marcio', senha 'flafla'"
    echo "  3. Use ./testar_sistema.sh para verificar funcionamento"
    echo ""
    echo "🔧 COMANDOS ÚTEIS:"
    echo "  - Executar sistema: ./executar_sistema.sh"
    echo "  - Testar sistema: ./testar_sistema.sh"
    echo "  - Limpeza: ./limpar_sistema.sh"
    echo ""
    echo "📁 ARQUIVOS IMPORTANTES:"
    echo "  - config.json: Configurações do sistema"
    echo "  - .env: Variáveis de ambiente"
    echo "  - logs/: Logs do sistema"
    echo ""
    print_warning "IMPORTANTE: Configure as senhas nos arquivos .env e config.json antes do uso em produção!"
}

# Função principal
main() {
    echo "🚀 CONFIGURAÇÃO AUTOMÁTICA DO SISTEMA INTEGRAGALGIT"
    echo "=================================================="
    echo ""
    
    check_directory
    install_system_deps
    install_uv
    install_python_deps
    
    # PostgreSQL é opcional, apenas tentar configurar
    if command -v psql &> /dev/null; then
        print_status "Configurando PostgreSQL (opcional)..."
        setup_postgresql || print_warning "Falha na configuração do PostgreSQL"
    fi
    
    setup_environment
    start_x_server
    run_validations
    create_convenience_scripts
    show_summary
}

# Verificar se script está sendo executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi