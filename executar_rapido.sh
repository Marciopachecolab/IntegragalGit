#!/bin/bash

# ========================================
# ⚡ Execução Rápida - IntegragalGit
# Versão: 1.0
# Data: 02/12/2025
# ========================================

# Função para imprimir mensagens coloridas
print_header() {
    echo ""
    echo "⚡ $1"
    echo "$(printf '=%.0s' {1..40})"
}

print_success() {
    echo -e "✅ $1"
}

print_error() {
    echo -e "❌ $1"
}

print_info() {
    echo -e "ℹ️ $1"
}

# Verificar se está no diretório correto
if [[ ! -f "main.py" ]]; then
    print_error "Arquivo main.py não encontrado!"
    print_info "Execute este script no diretório raiz do projeto IntegragalGit"
    exit 1
fi

# Função para configurar display automaticamente
setup_display() {
    if [[ -z "$DISPLAY" ]]; then
        print_info "Configurando DISPLAY automaticamente..."
        
        # Tentar Xvfb primeiro (para servidor sem interface)
        if command -v Xvfb &> /dev/null; then
            print_info "Iniciando Xvfb..."
            Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
            XVFB_PID=$!
            sleep 2
            export DISPLAY=:99
            print_success "Xvfb iniciado (PID: $XVFB_PID)"
        else
            # Tentar usar display padrão
            export DISPLAY=:0
            print_info "Usando DISPLAY=:0 (configure manualmente se necessário)"
        fi
    else
        print_success "DISPLAY já configurado: $DISPLAY"
    fi
}

# Função para executar validação rápida
run_quick_validation() {
    print_header "VALIDAÇÃO RÁPIDA"
    
    # Verificar se dependências Python estão instaladas
    local missing_deps=()
    
    local required_modules=("customtkinter" "pandas" "matplotlib" "bcrypt" "psycopg2")
    for module in "${required_modules[@]}"; do
        if ! python3 -c "import $module" &>/dev/null; then
            missing_deps+=("$module")
        fi
    done
    
    if [[ ${#missing_deps[@]} -eq 0 ]]; then
        print_success "Todas as dependências críticas estão instaladas"
    else
        print_error "Dependências em falta: ${missing_deps[*]}"
        print_info "Execute: uv pip install -r requirements.txt"
        return 1
    fi
    
    # Verificar usuário marcio
    if grep -q "marcio" banco/credenciais.csv 2>/dev/null; then
        print_success "Usuário 'marcio' encontrado nas credenciais"
    else
        print_warning "Usuário 'marcio' não encontrado"
    fi
    
    return 0
}

# Função para executar o sistema
run_system() {
    print_header "EXECUTANDO SISTEMA"
    
    # Configurar variáveis de ambiente
    export PYTHONPATH="$(pwd)"
    source .env 2>/dev/null || true
    
    print_info "Iniciando IntegragalGit..."
    print_info "DISPLAY: $DISPLAY"
    print_info "PYTHONPATH: $PYTHONPATH"
    echo ""
    
    # Executar sistema
    python3 main.py
}

# Função para mostrar menu de opções
show_menu() {
    echo ""
    echo "🎯 OPÇÕES DE EXECUÇÃO:"
    echo "1) Execução completa (configurar + validar + executar)"
    echo "2) Apenas executar (assume sistema já configurado)"
    echo "3) Verificação rápida (sem executar)"
    echo "4) Sair"
    echo ""
    read -p "Escolha uma opção (1-4): " choice
    
    case $choice in
        1)
            print_info "Executando configuração completa..."
            setup_display
            if run_quick_validation; then
                run_system
            else
                print_error "Validação falhou. Execute setup_automatico.sh primeiro."
            fi
            ;;
        2)
            print_info "Executando sistema diretamente..."
            setup_display
            run_system
            ;;
        3)
            print_info "Executando verificação rápida..."
            setup_display
            run_quick_validation
            ;;
        4)
            print_info "Saindo..."
            exit 0
            ;;
        *)
            print_error "Opção inválida"
            show_menu
            ;;
    esac
}

# Função principal
main() {
    echo "⚡ EXECUÇÃO RÁPIDA - INTEGRAGALGIT"
    echo "==================================="
    
    # Se argumentos foram fornecidos, usar modo direto
    if [[ $# -eq 0 ]]; then
        show_menu
    else
        case "$1" in
            "executar"|"run")
                setup_display
                run_quick_validation && run_system
                ;;
            "validar"|"validate")
                setup_display
                run_quick_validation
                ;;
            "configurar"|"setup")
                setup_display
                print_success "Configuração automática realizada"
                ;;
            *)
                echo "Uso: $0 [executar|validar|configurar]"
                echo ""
                echo "Comandos:"
                echo "  executar  - Configurar e executar o sistema"
                echo "  validar   - Apenas executar validações"
                echo "  configurar - Apenas configurar ambiente"
                echo "  (sem argumento) - Menu interativo"
                exit 1
                ;;
        esac
    fi
}

# Executar função principal
main "$@"