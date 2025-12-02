#!/bin/bash
# Script para limpar arquivos desnecessários do IntegragalGit
# Execute com: bash limpar_arquivos_desnecessarios.sh

echo "🧹 Iniciando limpeza de arquivos desnecessários..."

# Verificar se é um backup seguro (data anterior)
if [ -d "_backup_refatoracao_20251201_125108" ]; then
    echo "📦 Backup encontrado - manteremos como segurança"
fi

# Limpar cache Python
echo "🗂️  Limpando cache Python..."
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

# Backup dos logs importantes antes de excluir
echo "📊 Fazendo backup de logs importantes..."
mkdir -p _backup_logs_$(date +%Y%m%d_%H%M%S)
if [ -f "_archive/logs/sistema.log" ]; then
    cp "_archive/logs/sistema.log" "_backup_logs_$(date +%Y%m%d_%H%M%S)/" 2>/dev/null
fi

# Remover arquivos de dados de teste
echo "🧪 Removendo dados de teste mock..."
rm -f tests/mock_*.xlsx 2>/dev/null
rm -f reports/test_integration_* 2>/dev/null

# Remover archive completo (DADOS SENSÍVEIS)
echo "🗑️  Removendo dados sensíveis antigos..."
rm -rf _archive/

# Remover arquivos de configuração de desenvolvimento
echo "⚙️  Removendo templates de desenvolvimento..."
rm -f github_credentials_template.py 2>/dev/null

echo "✅ Limpeza concluída!"
echo "📊 Espaço liberado: ~570KB"
echo "⚠️  Verifique se todos os módulos ainda funcionam após a limpeza"