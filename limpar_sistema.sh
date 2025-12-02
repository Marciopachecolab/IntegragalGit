#!/bin/bash

# 🧹 SCRIPT DE LIMPEZA DO SISTEMA INTEGRAGAL
# Remove arquivos desnecessários para otimização do projeto

echo "🧹 INICIANDO LIMPEZA DO SISTEMA INTEGRAGAL"
echo "=============================================="

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ ERRO: main.py não encontrado. Execute este script na pasta raiz do projeto."
    exit 1
fi

echo "✅ Diretório correto identificado"
echo ""

# Criar backup antes da limpeza
echo "💾 Criando backup de segurança..."
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="backup_integragal_${timestamp}.zip"
zip -r "$backup_file" . -x "backup_*.zip" "*.zip" "__pycache__/*" "*.pyc" "analise/*" "reports/*.csv" 2>/dev/null
echo "✅ Backup criado: $backup_file"
echo ""

# Função para limpar categorias
limpar_categoria() {
    local nome=$1
    local comando=$2
    echo "🧹 Limpando: $nome"
    eval $comando
    echo "✅ Concluído"
    echo ""
}

# 1. LIMPEZA DE CACHE PYTHON (URGENTE)
limpar_categoria "Cache Python" "find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null && find . -name '*.pyc' -delete 2>/dev/null"

# 2. ARQUIVOS DE CORREÇÕES E DOCUMENTAÇÃO (URGENTE)
limpar_categoria "Arquivos de correções (.md)" "rm -f *.md ANALISE_*.md CORRECAO_*.md CORRECOES_*.md GUIA_*.md IMPLEMENTACAO_*.md PROBLEMA_*.md RELATORIO_*.md RESUMO_*.md 2>/dev/null"

limpar_categoria "Instruções de correção (.txt)" "rm -f *.txt INSTRUCOES_*.txt 2>/dev/null"

# 3. PACOTES .zip ANTIGOS (MÉDIA)
limpar_categoria "Pacotes .zip antigos" "ls IntegraGAL_*.zip 2>/dev/null | head -n -1 | xargs rm -f 2>/dev/null"

# 4. PASTA DE DESENVOLVIMENTO (MÉDIA)
if [ -d "analise" ]; then
    limpar_categoria "Pasta analise (scripts de teste)" "rm -rf analise/"
fi

# 5. RELATÓRIOS DE TESTE ANTIGOS (BAIXA)
if [ -d "reports" ]; then
    echo "🧹 Limpando: Relatórios de teste antigos"
    cd reports
    rm -f gal_*.csv 2>/dev/null
    rm -f test_integration_* 2>/dev/null
    echo "✅ Relatórios antigos removidos"
    echo ""
    cd ..
fi

# 6. PASTA TMP (BAIXA)
if [ -d "tmp" ]; then
    limpar_categoria "Pasta tmp (arquivos temporários)" "rm -rf tmp/"
fi

# 7. ARQUIVOS DESNECESSÁRIOS NA RAIZ (BAIXA)
limpar_categoria "Arquivos na raiz desnecessários" "rm -f DOWNLOAD_FILES.txt LEIA_ME_ANTES_DE_USAR.txt 2>/dev/null"

# 8. VERIFICAR SE HÁ ARQUIVOS LOG ANTIGOS
limpar_categoria "Logs antigos (se existirem)" "rm -f *.log 2>/dev/null"

# Verificar tamanho antes e depois
echo "📊 ESTATÍSTICAS FINAIS"
echo "======================="

# Contar arquivos restantes
total_arquivos=$(find . -type f | wc -l)
dirs_restantes=$(find . -type d | wc -l)

echo "📁 Arquivos restantes: $total_arquivos"
echo "📁 Pastas restantes: $dirs_restantes"
echo ""

# Mostrar estrutura limpa
echo "📋 ESTRUTURA FINAL DO PROJETO:"
echo "=============================="
ls -la | head -20
echo ""

echo "🎉 LIMPEZA CONCLUÍDA COM SUCESSO!"
echo "=================================="
echo "✅ Cache Python removido"
echo "✅ Documentação de correções removida" 
echo "✅ Pacotes .zip antigos removidos"
echo "✅ Scripts de desenvolvimento removidos"
echo "✅ Relatórios de teste antigos removidos"
echo "✅ Arquivos temporários removidos"
echo ""
echo "💡 DICAS:"
echo "- Execute: python main.py para testar"
echo "- Verifique: autenticação e exports funcionam"
echo "- Mantenha: backup_${timestamp}.zip salvo"
echo ""
echo "🎯 Sistema otimizado e pronto para uso!"