# 🚀 Guia de Início Rápido - IntegRAGal

**Comece a usar o IntegRAGal em 10 minutos!**

---

## ⚡ Instalação Express (5 minutos)

### Windows

1. **Descompacte** `integragal-v1.0.zip` em `C:\IntegRAGal`

2. **Abra PowerShell** nessa pasta:
   ```powershell
   cd C:\IntegRAGal
   ```

3. **Execute o instalador**:
   ```powershell
   .\install.bat
   ```

4. **Aguarde** (~2-3 minutos) até ver:
   ```
   ✅ Instalação concluída!
   Execute: python main.py
   ```

5. **Pronto!** Sistema instalado.

---

## 🎯 Primeira Análise (5 minutos)

### Passo 1: Abrir o Sistema (30s)

```powershell
python main.py
```

**Login padrão**:
- Usuário: `admin`
- Senha: `admin123`

### Passo 2: Importar Dados (1min)

1. Clique em **📥 Extração**
2. Selecione arquivo `.xlsx` do QuantStudio
3. Sistema detecta automaticamente o equipamento
4. Clique **[Continuar]**

### Passo 3: Validar Resultados (2min)

1. Revise os dados exibidos:
   ```
   Amostras: 96
   Válidas: 92
   Positivos: 48
   Negativos: 44
   ```

2. Clique **[Aplicar Regras]**
3. Sistema valida automaticamente:
   - ✅ Controles OK
   - ✅ CTs dentro dos limites
   - ⚠️ 2 alertas gerados

### Passo 4: Revisar Alertas (30s)

1. Badge **[🔔 Alertas: 2]** no topo
2. Clique para ver detalhes:
   ```
   🔴 CT Alto - Amostra 2024004 (CT: 36.2)
   🟡 CT Baixo - Amostra 2024015 (CT: 12.1)
   ```
3. Marque como lidos se estiverem OK

### Passo 5: Exportar Relatório (1min)

1. Clique **[📄 Exportar]**
2. Escolha **PDF**
3. Selecione destino
4. Clique **[Exportar]**
5. Arquivo criado!

---

## 📋 Checklist Rápido

Use esta checklist para suas análises diárias:

```
[ ] 1. Abrir sistema e fazer login
[ ] 2. Importar arquivo do QuantStudio
[ ] 3. Verificar detecção automática do equipamento
[ ] 4. Aplicar regras de validação
[ ] 5. Revisar alertas (se houver)
[ ] 6. Validar controles positivo e negativo
[ ] 7. Gerar relatório PDF
[ ] 8. Enviar para GAL (se necessário)
[ ] 9. Arquivar documentação
```

**Tempo total**: 10-15 minutos por placa

---

## 🎨 Interface Rápida

### Dashboard (Tela Principal)
```
┌────────────────────────────────────────┐
│ IntegRAGal            [🔔] [⚙️] [❌]   │
├────────────────────────────────────────┤
│                                        │
│  Análises Recentes    Estatísticas    │
│  • P001234 (10/12)    Total: 127      │
│  • P001233 (09/12)    Hoje: 3         │
│                                        │
│  Alertas Ativos       Ações           │
│  • 2 CT Alto          [Nova Análise]  │
│  • 1 CT Baixo         [Histórico]     │
│                                        │
└────────────────────────────────────────┘
```

### Menu Principal
- **📊 Dashboard**: Visão geral
- **📥 Extração**: Importar dados
- **🔬 Análise**: Processar resultados
- **📈 Gráficos**: Visualizações
- **📄 Relatórios**: Exportar
- **🌐 GAL**: Envio online
- **🔔 Alertas**: Notificações
- **📚 Histórico**: Análises anteriores
- **⚙️ Configurações**: Ajustes

### Atalhos Úteis
- `Ctrl+D`: Dashboard
- `Ctrl+N`: Nova análise
- `Ctrl+E`: Exportar
- `Ctrl+H`: Histórico
- `Ctrl+,`: Configurações
- `F1`: Ajuda

---

## ⚙️ Configurações Essenciais

### Antes de Começar

Ajuste estas configurações básicas:

**1. Limites de CT** (`Ctrl+,` → Alertas):
```
CT Alto: [35.0] (seu laboratório pode usar outro)
CT Baixo: [15.0] (ajuste conforme protocolo)
```

**2. Formato de Exportação** (Configurações → Exportação):
```
Formato padrão: [PDF ▼]
Incluir gráficos: [✓]
DPI: [300]
```

**3. Conexão GAL** (Configurações → GAL):
```
URL: [https://gal.saude.gov.br]
Usuário: [seu_usuario]
Senha: [sua_senha]
```

**4. Restaurar Sessão** (Configurações → Sessão):
```
[✓] Restaurar sessão anterior
[✓] Salvar estado automaticamente
Intervalo: [5] minutos
```

---

## 🆘 Resolução Rápida de Problemas

### Erro ao Abrir o Sistema
```
Erro: ModuleNotFoundError: No module named 'customtkinter'
```
**Solução**: Execute novamente `.\install.bat`

### Arquivo Não É Reconhecido
```
⚠️ Equipamento não detectado
```
**Solução**: 
1. Verifique se é arquivo `.xlsx` do QuantStudio
2. Tente seleção manual do equipamento

### Controle Negativo Amplificou
```
🔴 Controle Negativo Positivo (CT: 32.5)
```
**Solução**:
1. Verificar se realmente é contaminação
2. Revisar curva de amplificação
3. Se confirmado, invalidar placa
4. Documentar ocorrência

### Erro ao Enviar para GAL
```
❌ Erro de Conexão com GAL
```
**Solução**:
1. Verificar internet
2. Testar credenciais (Configurações → GAL → [Testar Conexão])
3. Verificar se servidor GAL está online
4. Tentar novamente em alguns minutos

---

## 📊 Principais Tipos de Alertas

| Alerta | O Que Fazer |
|--------|-------------|
| 🔴 **CT Alto** | Verificar se amostra é fraca ou houve problema na reação |
| 🟡 **CT Baixo** | Investigar possível contaminação ou excesso de material |
| 🔵 **Placa Não Mapeada** | Mapear placa antes de continuar |
| ⚪ **Amostra Inválida** | Revisar dados e corrigir se necessário |
| 🟠 **Erro Extração** | Verificar formato do arquivo |
| 🟣 **Aviso Qualidade** | Verificar controles e curva padrão |

---

## 🎓 Fluxo de Trabalho Recomendado

```
1. IMPORTAR
   ↓
   Arquivo .xlsx do QuantStudio
   ↓
2. VALIDAR
   ↓
   Sistema detecta equipamento e valida dados
   ↓
3. ANALISAR
   ↓
   Aplicar regras automáticas
   ↓
4. REVISAR
   ↓
   Verificar alertas e controles
   ↓
5. APROVAR
   ↓
   Confirmar que análise está OK
   ↓
6. EXPORTAR
   ↓
   Gerar relatório PDF
   ↓
7. ENVIAR GAL
   ↓
   Transmitir resultados validados
   ↓
8. ARQUIVAR
   ↓
   Guardar documentação
```

---

## 💡 Dicas Profissionais

### 1. Use Templates de Exportação
Crie templates para diferentes tipos de relatórios:
- **Completo**: Com tudo (gráficos, stats, alertas)
- **Simplificado**: Apenas resultados
- **Apenas Positivos**: Para notificação
- **Apenas Alertas**: Para revisão de qualidade

### 2. Configure Alertas Personalizados
Ajuste limites de CT conforme seu protocolo:
```
COVID-19: CT Alto = 35.0
Influenza: CT Alto = 38.0
HIV: CT Alto = 40.0
```

### 3. Use Atalhos de Teclado
Economize tempo com atalhos:
- `Ctrl+N`: Nova análise (não precisa clicar no menu)
- `Ctrl+E`: Exportar rapidamente
- `Ctrl+Shift+N`: Centro de notificações

### 4. Revise Histórico Regularmente
Uma vez por semana:
1. Abrir **Histórico** (`Ctrl+H`)
2. Filtrar últimos 7 dias
3. Exportar CSV de todas as análises
4. Analisar tendências de CT

### 5. Backup Automático
Configure backup em `Configurações → Sessão`:
```
[✓] Salvar estado automaticamente
Intervalo: [5] minutos
Manter por: [30] dias
```

---

## 📖 Próximos Passos

Agora que você conhece o básico:

1. **📘 Manual Completo**: `docs/MANUAL_USUARIO.md`
   - Todas as funcionalidades detalhadas
   - Casos de uso avançados
   - Boas práticas

2. **❓ FAQ**: `docs/FAQ.md`
   - Perguntas frequentes
   - Soluções rápidas

3. **🔧 Troubleshooting**: `docs/TROUBLESHOOTING.md`
   - Resolução de problemas complexos
   - Mensagens de erro

4. **🏗️ Arquitetura**: `docs/ARQUITETURA_TECNICA.md`
   - Para desenvolvedores
   - Estrutura do sistema

---

## 📞 Suporte

Precisa de ajuda?

- **Email**: suporte@integragal.com
- **Documentação**: https://docs.integragal.com
- **GitHub**: https://github.com/Marciopachecolab/IntegRAGal

---

## ✅ Checklist de Instalação Completa

Verifique se está tudo OK:

```
[✅] Sistema instalado
[✅] Primeiro login realizado
[✅] Primeira análise executada
[✅] Relatório exportado
[✅] Configurações básicas ajustadas
[✅] Limites de CT configurados
[✅] Conexão GAL testada (se aplicável)
[✅] Atalhos memorizados
[✅] Manual lido
```

**Parabéns! Você está pronto para usar o IntegRAGal! 🎉**

---

**Versão**: 1.0.0  
**Data**: Dezembro de 2025  
**Tempo de leitura**: 10 minutos
