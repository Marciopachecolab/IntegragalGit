#!/bin/bash

# ========================================
# 🔍 Verificador de Sistema - IntegragalGit
# Versão: 1.0
# Data: 02/12/2025
# ========================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Função para imprimir mensagens coloridas
print_header() {
    echo ""
    echo -e "${BLUE}🔍 $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
    ((TOTAL_CHECKS++))
}

# Verificar se está no diretório correto
check_project_directory() {
    print_header "VERIFICAÇÃO DO DIRETÓRIO"
    
    if [[ -f "main.py" ]]; then
        print_success "Diretório do projeto encontrado (main.py presente)"
        
        # Verificar outros arquivos essenciais
        local essential_files=("config.json" "requirements.txt" "banco/credenciais.csv")
        for file in "${essential_files[@]}"; do
            if [[ -f "$file" ]]; then
                print_success "Arquivo essencial encontrado: $file"
            else
                print_error "Arquivo essencial ausente: $file"
            fi
        done
    else
        print_error "Diretório do projeto inválido (main.py não encontrado)"
        print_info "Execute este script no diretório raiz do projeto IntegragalGit"
        exit 1
    fi
}

# Verificar Python e dependências
check_python_environment() {
    print_header "VERIFICAÇÃO DO PYTHON"
    
    # Verificar versão do Python
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python3 encontrado: $python_version"
        
        # Verificar se versão é >= 3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Versão do Python compatível (>= 3.8)"
        else
            print_error "Versão do Python incompatível (necessário >= 3.8)"
        fi
    else
        print_error "Python3 não encontrado"
    fi
    
    # Verificar uv
    if command -v uv &> /dev/null; then
        local uv_version=$(uv --version | cut -d' ' -f2)
        print_success "uv encontrado: $uv_version"
    else
        print_warning "uv não encontrado (recomendado para instalação)"
    fi
}

# Verificar dependências Python
check_python_dependencies() {
    print_header "VERIFICAÇÃO DAS DEPENDÊNCIAS PYTHON"
    
    local required_modules=(
        "customtkinter:Interface gráfica"
        "pandas:Manipulação de dados"
        "matplotlib:Geração de gráficos"
        "bcrypt:Criptografia de senhas"
        "psycopg2:Conexão PostgreSQL"
        "selenium:Automação web"
        "openpyxl:Manipulação Excel"
        "numpy:Computação numérica"
    )
    
    for module_info in "${required_modules[@]}"; do
        local module=$(echo "$module_info" | cut -d':' -f1)
        local description=$(echo "$module_info" | cut -d':' -f2)
        
        if python3 -c "import $module" 2>/dev/null; then
            print_success "$module ($description)"
        else
            print_error "$module ($description) - não instalado"
        fi
    done
}

# Verificar servidor X e display
check_display_server() {
    print_header "VERIFICAÇÃO DO SERVIDOR GRÁFICO"
    
    # Verificar DISPLAY
    if [[ -n "$DISPLAY" ]]; then
        print_success "Variável DISPLAY configurada: $DISPLAY"
        
        # Testar conexão com servidor X
        if xset q &>/dev/null; then
            print_success "Conexão com servidor X funcionando"
        else
            print_error "Servidor X não responde na variável DISPLAY"
        fi
    else
        print_error "Variável DISPLAY não configurada"
        print_info "Execute: export DISPLAY=:0 ou configure X Server"
    fi
    
    # Verificar X Server executando
    if command -v Xvfb &> /dev/null; then
        print_success "Xvfb disponível (para ambiente sem interface)"
    else
        print_warning "Xvfb não encontrado (pode ser necessário)"
    fi
}

# Verificar PostgreSQL
check_postgresql() {
    print_header "VERIFICAÇÃO DO POSTGRESQL"
    
    if command -v psql &> /dev/null; then
        print_success "Cliente PostgreSQL encontrado"
        
        # Verificar se serviço está rodando
        if command -v systemctl &> /dev/null; then
            if systemctl is-active --quiet postgresql 2>/dev/null; then
                print_success "Serviço PostgreSQL ativo"
            else
                print_warning "Serviço PostgreSQL não ativo"
                print_info "Execute: sudo systemctl start postgresql"
            fi
        fi
        
        # Testar conexão local
        if sudo -u postgres psql -c "\q" &>/dev/null; then
            print_success "Conexão PostgreSQL funcionando"
        else
            print_warning "Erro na conexão PostgreSQL"
        fi
    else
        print_warning "Cliente PostgreSQL não encontrado"
    fi
}

# Verificar estrutura de arquivos
check_file_structure() {
    print_header "VERIFICAÇÃO DA ESTRUTURA DE ARQUIVOS"
    
    # Diretórios essenciais
    local essential_dirs=("ui" "utils" "autenticacao" "analise" "exportacao" "banco" "logs")
    for dir in "${essential_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_success "Diretório essencial encontrado: $dir/"
        else
            print_error "Diretório essencial ausente: $dir/"
        fi
    done
    
    # Arquivos de configuração
    if [[ -f "config.json" ]]; then
        print_success "Arquivo de configuração config.json encontrado"
        
        # Verificar se tem senhas placeholder
        if grep -q "your_password_here" config.json 2>/dev/null; then
            print_warning "Senhas placeholder encontradas em config.json"
            print_info "Configure as senhas reais antes do uso"
        fi
    else
        print_error "Arquivo de configuração config.json ausente"
    fi
    
    # Arquivo de credenciais
    if [[ -f "banco/credenciais.csv" ]]; then
        print_success "Arquivo de credenciais encontrado"
        
        # Verificar se usuário marcio existe
        if grep -q "marcio" banco/credenciais.csv 2>/dev/null; then
            print_success "Usuário 'marcio' encontrado nas credenciais"
        else
            print_warning "Usuário 'marcio' não encontrado nas credenciais"
        fi
    else
        print_error "Arquivo de credenciais banco/credenciais.csv ausente"
    fi
}

# Verificar integridade do código
check_code_integrity() {
    print_header "VERIFICAÇÃO DA INTEGRIDADE DO CÓDIGO"
    
    # Testar importações dos módulos principais
    local critical_imports=(
        "ui.main_window"
        "ui.menu_handler"
        "ui.status_manager"
        "ui.navigation"
        "utils.logger"
        "autenticacao.login"
        "models"
        "analise.vr1e2_biomanguinhos_7500"
    )
    
    for import in "${critical_imports[@]}"; do
        if python3 -c "import $import" 2>/dev/null; then
            print_success "Módulo importável: $import"
        else
            print_error "Falha na importação: $import"
        fi
    done
}

# Verificar logs e histórico
check_logs_and_history() {
    print_header "VERIFICAÇÃO DE LOGS E HISTÓRICO"
    
    # Verificar se diretório de logs existe
    if [[ -d "logs" ]]; then
        print_success "Diretório de logs encontrado"
        
        # Contar arquivos de log
        local log_count=$(find logs/ -name "*.log" 2>/dev/null | wc -l)
        if [[ $log_count -gt 0 ]]; then
            print_success "Encontrados $log_count arquivo(s) de log"
        else
            print_info "Nenhum arquivo de log encontrado (normal para primeira execução)"
        fi
    else
        print_warning "Diretório de logs não encontrado"
    fi
    
    # Verificar arquivos de backup/archive
    if [[ -d "_archive" ]]; then
        local archive_size=$(du -sh _archive/ 2>/dev/null | cut -f1)
        print_warning "Diretório _archive/ encontrado (tamanho: $archive_size)"
        print_info "Considere executar limpeza com: bash limpar_arquivos_desnecessarios.sh"
    else
        print_success "Diretório _archive/ não encontrado (já limpo ou nunca existiu)"
    fi
}

# Verificar permissões
check_permissions() {
    print_header "VERIFICAÇÃO DE PERMISSÕES"
    
    # Verificar permissões do diretório banco
    if [[ -d "banco" ]]; then
        local banco_perms=$(stat -c "%a" banco/ 2>/dev/null || echo "unknown")
        print_info "Permissões do diretório banco/: $banco_perms"
        
        # Verificar se arquivo de credenciais é legível
        if [[ -f "banco/credenciais.csv" ]]; then
            if [[ -r "banco/credenciais.csv" ]]; then
                print_success "Arquivo de credenciais legível"
            else
                print_error "Arquivo de credenciais não legível"
                print_info "Execute: chmod 644 banco/credenciais.csv"
            fi
        fi
    fi
    
    # Verificar se scripts são executáveis
    local scripts=("main.py" "validar_resumo.py")
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if [[ -r "$script" ]]; then
                print_success "Arquivo legível: $script"
            else
                print_error "Arquivo não legível: $script"
            fi
        fi
    done
}

# Verificar conectividade de rede
check_network_connectivity() {
    print_header "VERIFICAÇÃO DE CONECTIVIDADE"
    
    # Verificar se há configuração de GAL
    if [[ -f "config.json" ]]; then
        local gal_url=$(python3 -c "
import json
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        print(config.get('gal_url', 'N/A'))
except:
    print('N/A')
" 2>/dev/null)
        
        if [[ "$gal_url" != "N/A"" && "$gal_url" != "" ]]; then
            print_success "URL do GAL configurada: $gal_url"
            
            # Testar conectividade (se for HTTP)
            if [[ "$gal_url" == http://* ]]; then
                if curl -s -I "$gal_url" &>/dev/null; then
                    print_success "Conectividade com GAL OK"
                else
                    print_warning "Não foi possível conectar ao GAL"
                fi
            fi
        else
            print_warning "URL do GAL não configurada em config.json"
        fi
    fi
}

# Gerar relatório final
generate_final_report() {
    print_header "RELATÓRIO FINAL"
    
    echo ""
    echo -e "${BLUE}📊 RESUMO DA VERIFICAÇÃO${NC}"
    echo "========================"
    echo -e "${GREEN}✅ Verificações bem-sucedidas: $PASSED_CHECKS${NC}"
    echo -e "${RED}❌ Verificações com falha: $FAILED_CHECKS${NC}"
    echo -e "${YELLOW}⚠️ Avisos: $WARNING_CHECKS${NC}"
    echo -e "📋 Total de verificações: $TOTAL_CHECKS"
    echo ""
    
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        echo -e "${GREEN}🎉 SISTEMA PRONTO PARA USO!${NC}"
        echo ""
        echo "Próximos passos:"
        echo "  1. Execute: ./executar_sistema.sh"
        echo "  2. Faça login com usuário 'marcio' e senha 'flafla'"
        echo "  3. Configure as senhas reais em config.json antes do uso em produção"
        exit 0
    else
        echo -e "${RED}🔧 SISTEMA PRECISA DE AJUSTES${NC}"
        echo ""
        echo "Ações recomendadas:"
        echo "  1. Revise os erros acima"
        echo "  2. Execute: bash setup_automatico.sh (para configuração automática)"
        echo "  3. Instale dependências em falta: uv pip install -r requirements.txt"
        echo "  4. Configure servidor X se necessário"
        exit 1
    fi
}

# Função principal
main() {
    echo "🔍 VERIFICADOR DE SISTEMA INTEGRAGALGIT"
    echo "======================================="
    
    check_project_directory
    check_python_environment
    check_python_dependencies
    check_display_server
    check_postgresql
    check_file_structure
    check_code_integrity
    check_logs_and_history
    check_permissions
    check_network_connectivity
    
    generate_final_report
}

# Verificar se script está sendo executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi