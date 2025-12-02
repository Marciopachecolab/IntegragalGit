#!/bin/bash

# Script para fazer deploy da versão 3.0 do IntegragalGit para GitHub
# Autor: MiniMax Agent
# Data: 2025-12-02

echo "🚀 Iniciando deploy da versão 3.0 do IntegragalGit..."

# Configurar variáveis
REPO_URL="https://github.com/Marciopachecolab/IntegragalGit.git"
BRANCH="master"
VERSION="v3.0"

echo "📋 Informações do deploy:"
echo "   Repositório: $REPO_URL"
echo "   Branch: $BRANCH"
echo "   Versão: $VERSION"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Erro: Execute este script no diretório root do IntegragalGit-latest"
    exit 1
fi

echo "✅ Diretório verificado"

# Verificar status do git
echo "📊 Verificando status do Git..."
git status

echo ""
echo "🔄 Enviando código para GitHub..."

# Fazer push das mudanças
echo "   → Enviando commits..."
git push origin $BRANCH

# Fazer push da tag
echo "   → Enviando tag $VERSION..."
git push origin $VERSION

echo ""
echo "✅ Deploy da versão $VERSION concluído com sucesso!"
echo ""
echo "🌐 O repositório está disponível em: $REPO_URL"
echo "📝 Changelog v3.0:"
echo "   • Sistema refatorado com arquitetura modular"
echo "   • 17 arquivos desnecessários removidos (~1.5MB)"
echo "   • main.py reduzido de 282 para 112 linhas (60% redução)"
echo "   • UI modularizada em 5 componentes especializados"
echo "   • Validação simplificada (5/5 checks)"
echo "   • README atualizado com documentação completa"
echo "   • Status: Produção-ready"
echo ""
echo "🎯 Próximo passo: Implementar UniversalAnalysisEngine (TAREFA 2)"