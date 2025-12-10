# 🔧 TROUBLESHOOTING - Guia de Resolução de Problemas

**IntegRAGal - Diagnóstico e Soluções Técnicas**

---

## 📑 Índice Rápido

- [Problemas de Instalação](#problemas-de-instalação)
- [Erros ao Iniciar o Sistema](#erros-ao-iniciar-o-sistema)
- [Problemas de Importação de Dados](#problemas-de-importação-de-dados)
- [Erros de Análise e Validação](#erros-de-análise-e-validação)
- [Problemas com Alertas](#problemas-com-alertas)
- [Erros de Exportação](#erros-de-exportação)
- [Problemas de Conexão GAL](#problemas-de-conexão-gal)
- [Performance e Memória](#performance-e-memória)
- [Erros de Interface](#erros-de-interface)
- [Problemas de Configuração](#problemas-de-configuração)
- [Diagnóstico Avançado](#diagnóstico-avançado)

---

## Problemas de Instalação

### ❌ Erro: "Python não reconhecido como comando"

**Sintoma**: Ao executar `python --version`, recebe erro "não é reconhecido como comando interno ou externo".

**Causa**: Python não instalado ou não adicionado ao PATH.

**Solução**:
```powershell
# 1. Baixe Python 3.13 de python.org
# 2. Na instalação, marque "Add Python to PATH"
# 3. Após instalar, verifique:
python --version

# Se ainda não funcionar, adicione manualmente ao PATH:
# Windows: Configurações → Sistema → Sobre → Configurações avançadas → Variáveis de Ambiente
# Adicione: C:\Python313 e C:\Python313\Scripts
```

---

### ❌ Erro: "pip: command not found"

**Sintoma**: `pip` não funciona.

**Solução**:
```powershell
# Use python -m pip em vez de pip:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### ❌ Erro: "ModuleNotFoundError: No module named 'customtkinter'"

**Sintoma**: Dependências não instaladas corretamente.

**Causa**: `install.bat` não executado ou falhou silenciosamente.

**Solução**:
```powershell
# 1. Execute novamente:
.\install.bat

# 2. Se falhar, instale manualmente:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Verifique instalação:
python -c "import customtkinter; print('OK')"

# 4. Se persistir, crie ambiente virtual:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### ❌ Erro: "PermissionError durante instalação"

**Sintoma**: Erro de permissão ao instalar pacotes.

**Causa**: Necessário privilégios administrativos.

**Solução**:
```powershell
# Opção 1: Execute PowerShell como Administrador
# Botão direito → "Executar como Administrador"

# Opção 2: Instale apenas para usuário atual:
pip install --user -r requirements.txt
```

---

## Erros ao Iniciar o Sistema

### ❌ Erro: "FileNotFoundError: banco/usuarios.csv"

**Sintoma**: Sistema não encontra arquivos do banco de dados.

**Causa**: Executando de diretório errado ou arquivos faltando.

**Solução**:
```powershell
# 1. Certifique-se que está no diretório correto:
cd C:\IntegRAGal

# 2. Verifique estrutura:
Test-Path .\banco\usuarios.csv  # Deve retornar True

# 3. Se arquivos faltam, recrie estrutura:
python
>>> from db.db_utils import inicializar_banco
>>> inicializar_banco()
>>> exit()

# 4. Inicie sistema:
python main.py
```

---

### ❌ Sistema abre e fecha imediatamente

**Sintoma**: Janela aparece por segundo e fecha.

**Causa**: Erro fatal não capturado.

**Solução**:
```powershell
# Execute via terminal para ver erros:
python main.py

# Leia os logs:
Get-Content .\logs\integragal.log -Tail 50

# Ative modo debug:
$env:DEBUG="1"
python main.py
```

---

### ❌ Erro: "TclError: no display name"

**Sintoma**: Erro ao iniciar interface (comum em SSH/Remote Desktop).

**Causa**: Sem servidor X ou display configurado.

**Solução**:
```bash
# Linux/Mac via SSH:
export DISPLAY=:0
python main.py

# Windows Remote Desktop: use conexão RDP normal (não CLI)
```

---

### ❌ Tela fica em branco ao abrir

**Sintoma**: Sistema abre, mas dashboard não carrega.

**Causa**: Cache corrompido ou erro na inicialização.

**Solução**:
```powershell
# 1. Limpe cache:
Remove-Item ".\data\state\cache\*" -Recurse -Force

# 2. Reinicie:
python main.py

# 3. Se persistir, resete configurações:
Copy-Item ".\config\default_config.json" ".\config\config.json" -Force
```

---

## Problemas de Importação de Dados

### ❌ Erro: "Equipamento não detectado"

**Sintoma**: Arquivo não é reconhecido automaticamente.

**Causa**: Formato incompatível ou falta de metadados.

**Solução**:
```powershell
# 1. Verifique formato do arquivo:
# - Deve ser .xlsx ou .xls do QuantStudio
# - Primeira linha deve conter cabeçalhos
# - Coluna "CT" ou "Ct" deve existir

# 2. Tente seleção manual:
# Extração → [Selecionar Equipamento Manualmente]

# 3. Valide arquivo em Python:
python
>>> import pandas as pd
>>> df = pd.read_excel("seu_arquivo.xlsx")
>>> print(df.columns.tolist())  # Veja colunas disponíveis
>>> print(df.head())  # Primeiras linhas
```

---

### ❌ Erro: "Placa não mapeada"

**Sintoma**: Alerta de placa não mapeada.

**Causa**: ID da placa não existe no cadastro.

**Solução**:
```plaintext
1. Anote ID da placa no alerta (ex: "PLACA_2025_001")
2. Extração → [Mapear Manualmente]
3. Adicione:
   - ID: PLACA_2025_001
   - Nome: Descrição legível
   - Data: Data da corrida
   - Protocolo: Nome do protocolo
4. Confirme mapeamento
5. Reprocesse análise
```

---

### ❌ Erro: "Valores CT inválidos"

**Sintoma**: CTs negativos, muito altos (>50), ou texto.

**Causa**: Erro na exportação ou arquivo editado manualmente.

**Solução**:
```powershell
# 1. Verifique integridade:
python
>>> import pandas as pd
>>> df = pd.read_excel("arquivo.xlsx")
>>> print(df['CT'].describe())  # Estatísticas
>>> print(df[df['CT'].isna()])  # Valores faltando
>>> print(df[df['CT'] < 0])  # CTs negativos
>>> print(df[df['CT'] > 50])  # CTs suspeitos

# 2. Reexporte do QuantStudio:
# - Não edite arquivo manualmente
# - Use opção "Export Results" do software
# - Mantenha formato original
```

---

### ❌ Erro: "Arquivo corrompido ou protegido"

**Sintoma**: Não consegue ler arquivo Excel.

**Causa**: Arquivo danificado, senha, ou aberto em outro programa.

**Solução**:
```powershell
# 1. Feche arquivo em outros programas:
# - Feche Excel/OpenOffice
# - Verifique processos: Get-Process EXCEL

# 2. Remova proteção:
# - Abra no Excel
# - Arquivo → Informações → Proteger → Remover proteção

# 3. Recrie arquivo:
# - Abra Excel
# - Salvar Como → Novo arquivo
# - Use novo arquivo no IntegRAGal

# 4. Converta para CSV (última opção):
# CSV perde alguns metadados
```

---

## Erros de Análise e Validação

### ❌ Controle Negativo Amplificou

**Sintoma**: Alerta "Controle Negativo com amplificação detectada".

**Diagnóstico**:
```plaintext
1. Verifique CT do controle:
   - CT < 30: Contaminação confirmada → INVALIDE
   - 30 < CT < 35: Suspeita → Revise curva
   - CT > 35: Pode ser ruído → Analise contexto

2. Compare com outras amostras:
   - Se todas têm CT similar: Contaminação global
   - Se apenas controle: Contaminação localizada

3. Revise curva de amplificação:
   - Curva sigmoidal típica: Amplificação real
   - Curva irregular: Artefato/ruído
```

**Ações**:
```plaintext
✅ Se Contaminação Confirmada:
   - Marque placa como inválida
   - Repita análise com nova extração
   - Investigue fonte (reagentes, ambiente, pipetas)
   - Documente no log

⚠️ Se Inconclusivo:
   - Adicione observação
   - Notifique supervisor
   - Considere repetir apenas controles
```

---

### ❌ Controle Positivo Não Amplificou

**Sintoma**: Alerta "Controle Positivo sem amplificação".

**Causas Comuns**:
1. **Degradação do controle**: Armazenamento inadequado
2. **Erro de pipetagem**: Volume insuficiente
3. **Inibição**: Presença de inibidores na reação
4. **Falha do equipamento**: Problema técnico

**Solução**:
```plaintext
1. Verifique validade do controle
2. Confirme protocolo de preparo
3. Repita análise com:
   - Novo controle (alíquota diferente)
   - Verificação de volumes
   - Checagem de equipamento
4. Se persistir: INVALIDE e reporte problema técnico
```

---

### ❌ Muitos Outliers Detectados

**Sintoma**: >10% das amostras marcadas como outliers.

**Causas**:
- Limites de CT muito restritos
- Protocolo inadequado para tipo de amostra
- Problema técnico sistemático

**Solução**:
```powershell
# 1. Revise limites de CT:
Configurações → Análise → CT Limite Superior: [35] → [38]

# 2. Desabilite temporariamente detecção:
Configurações → Análise → [ ] Detectar outliers automaticamente

# 3. Análise manual:
# Revise cada outlier individualmente
# Considere características da amostra
# Consulte responsável técnico

# 4. Ajuste sensibilidade (IQR):
Configurações → Análise → Fator IQR: [1.5] → [2.0]
# Valores maiores = menos outliers detectados
```

---

### ❌ Resultados Inconsistentes entre Duplicatas

**Sintoma**: Mesma amostra em duplicata com resultados diferentes.

**Tolerância Aceitável**:
```
ΔCT < 0.5: Excelente
ΔCT 0.5-1.0: Aceitável
ΔCT 1.0-2.0: Repetir recomendado
ΔCT > 2.0: Repetir obrigatório
```

**Ações**:
```plaintext
1. Calcule diferença: |CT1 - CT2|
2. Se ΔCT > 1.0:
   - Verifique curvas de amplificação
   - Confirme volume de amostra
   - Repita análise
3. Documente variação no relatório
4. Considere triplicata para amostras críticas
```

---

## Problemas com Alertas

### ❌ Alertas Não Aparecem

**Sintoma**: Nenhum alerta é gerado apesar de problemas visíveis.

**Causa**: Sistema de alertas desabilitado.

**Solução**:
```powershell
# 1. Verifique status:
Configurações → Alertas → [✓] Habilitar Sistema de Alertas

# 2. Confirme limites configurados:
Configurações → Análise:
   - CT Limite Superior: [35]  # Deve ser > 0
   - CT Limite Inferior: [15]  # Deve ser > 0

# 3. Verifique severidade mínima:
Configurações → Alertas → Severidade mínima: [Baixa]
# Se estiver em "Alta", só alertas críticos aparecem

# 4. Limpe cache:
python -c "from utils.persistence import persistence; persistence.limpar_cache()"
```

---

### ❌ Excesso de Alertas (Badge sempre vermelho)

**Sintoma**: Centenas de alertas acumulados.

**Causas**:
- Alertas antigos não resolvidos
- Limites de CT muito restritos
- Configuração inadequada

**Solução**:
```powershell
# 1. Limpe alertas antigos:
Centro de Notificações → [Marcar Todos como Lidos]

# 2. Ative limpeza automática:
Configurações → Performance:
   - [✓] Limpar alertas antigos automaticamente
   - Manter alertas por: [7] dias

# 3. Ajuste limites:
Configurações → Análise:
   - CT Limite Superior: [35] → [38]  # Menos alertas "CT Alto"
   - CT Limite Inferior: [15] → [12]  # Menos alertas "CT Baixo"

# 4. Filtre alertas críticos:
Centro de Notificações → Filtro: [Crítico]
# Foque apenas em alertas importantes
```

---

### ❌ Alertas Duplicados

**Sintoma**: Mesmo alerta aparece múltiplas vezes.

**Causa**: Bug no sistema de deduplicação.

**Solução Temporária**:
```powershell
# 1. Limpe cache:
Remove-Item ".\data\state\cache\alerts_cache.pkl" -Force

# 2. Reinicie sistema:
python main.py

# 3. Reporte bug:
# GitHub Issues com logs anexados
```

---

## Erros de Exportação

### ❌ Erro: "PermissionError ao exportar PDF"

**Sintoma**: Não consegue salvar relatório.

**Causa**: Arquivo já aberto ou pasta protegida.

**Solução**:
```powershell
# 1. Feche arquivo se aberto:
# Feche Adobe Reader, navegador, etc.

# 2. Escolha pasta diferente:
# Exportação → [Escolher Pasta] → Desktop

# 3. Execute como Administrador:
# Botão direito PowerShell → Executar como Admin

# 4. Verifique permissões:
icacls "C:\IntegRAGal\reports"
# Deve incluir: (F) - Full Control
```

---

### ❌ PDF sem gráficos

**Sintoma**: Relatório exporta, mas sem gráficos.

**Causa**: Matplotlib não instalado ou erro na geração.

**Solução**:
```powershell
# 1. Verifique Matplotlib:
python -c "import matplotlib; print('OK')"

# Se erro, instale:
pip install matplotlib

# 2. Habilite gráficos:
Configurações → Exportação → [✓] Incluir gráficos

# 3. Aumente DPI se gráficos aparecem corrompidos:
Configurações → Exportação → DPI dos gráficos: [300] → [150]

# 4. Verifique espaço em disco:
# Gráficos de alta resolução ocupam espaço
```

---

### ❌ Excel não abre ou corrompido

**Sintoma**: Arquivo .xlsx não abre ou Excel reclama de corrupção.

**Causa**: Versão incompatível do openpyxl ou dados problemáticos.

**Solução**:
```powershell
# 1. Atualize openpyxl:
pip install --upgrade openpyxl

# 2. Exporte como CSV:
# Formato mais simples, sempre funciona

# 3. Tente abrir no LibreOffice:
# Pode ter melhor compatibilidade

# 4. Use modo de reparo do Excel:
# Abrir → [Procurar] → Selecione arquivo → Seta ao lado de Abrir → Abrir e Reparar
```

---

### ❌ Exportação muito lenta

**Sintoma**: Demora >5 minutos para gerar relatório.

**Causa**: Muitos dados ou gráficos de alta resolução.

**Solução**:
```powershell
# 1. Reduza DPI dos gráficos:
Configurações → Exportação → DPI: [600] → [300]

# 2. Desabilite gráficos temporariamente:
Configurações → Exportação → [ ] Incluir gráficos

# 3. Exporte apenas dados filtrados:
# Filtre amostras antes de exportar

# 4. Use CSV para grandes volumes:
# Muito mais rápido que PDF/Excel
```

---

## Problemas de Conexão GAL

### ❌ Erro: "Timeout ao conectar com GAL"

**Sintoma**: Conexão expira após 30-60 segundos.

**Diagnóstico**:
```powershell
# 1. Teste conectividade:
Test-NetConnection -ComputerName "gal.saude.gov.br" -Port 443

# 2. Verifique internet:
ping 8.8.8.8

# 3. Teste URL no navegador:
# Abra https://gal.saude.gov.br
# Deve carregar página de login
```

**Soluções**:
```powershell
# 1. Aumente timeout:
Configurações → GAL → Timeout: [30] → [90] segundos

# 2. Verifique proxy:
Configurações → GAL → Proxy:
   - [✓] Usar proxy
   - Servidor: proxy.instituicao.br
   - Porta: 8080

# 3. Desabilite VPN temporariamente:
# VPNs podem interferir

# 4. Adicione exceção no firewall:
# Windows Defender → Permitir aplicativo:
# C:\Python313\python.exe
```

---

### ❌ Erro: "Credenciais inválidas"

**Sintoma**: GAL rejeita usuário/senha.

**Solução**:
```plaintext
1. Confirme credenciais no navegador:
   - Acesse https://gal.saude.gov.br manualmente
   - Faça login com mesmas credenciais
   - Se falhar: resete senha no GAL

2. Verifique espaços extras:
   - Usuário: [SEM ESPAÇOS]
   - Senha: [COPIE/COLE para evitar erros]

3. Atualize no sistema:
   Configurações → GAL → Credenciais → [Salvar]

4. Teste conexão:
   Configurações → GAL → [Testar Conexão]
```

---

### ❌ Erro: "Amostra já cadastrada no GAL"

**Sintoma**: GAL rejeita amostra por duplicação.

**Causa**: Amostra enviada anteriormente.

**Ações**:
```plaintext
✅ Se envio legítimo anterior:
   - Pule amostra no reenvio
   - Marque como enviada no histórico

⚠️ Se erro (nunca foi enviada):
   1. Verifique protocolo GAL no histórico
   2. Consulte GAL via web para confirmar
   3. Se não existe no GAL:
      - Reporte inconsistência ao suporte GAL
      - Use protocolo diferente (se permitido)
```

---

### ❌ Envio parcial (algumas amostras falharam)

**Sintoma**: Metade das amostras envia, metade falha.

**Causa**: Problemas individuais por amostra (CPF inválido, dados faltando, etc.).

**Solução**:
```plaintext
1. Verifique log de envio:
   Histórico → Envios GAL → [Detalhes]

2. Para cada erro:
   - "CPF inválido": Corrija CPF e reenvie
   - "Campo obrigatório": Preencha campo faltando
   - "Formato inválido": Ajuste formato de data/hora

3. Reenvie apenas falhas:
   Histórico → Envios GAL → [Reenviar Falhas]

4. Se muitos erros:
   - Exporte log: [Exportar Erros]
   - Corrija em lote no Excel
   - Reimporte dados corrigidos
```

---

## Performance e Memória

### ❌ Sistema Lento após Várias Horas de Uso

**Sintoma**: Performance degrada com o tempo.

**Causa**: Vazamento de memória ou cache inflado.

**Solução**:
```powershell
# 1. Reinicie o sistema diariamente:
# Atalho: Ctrl+Q (sair) → Reabra

# 2. Limpe cache periodicamente:
Configurações → Performance → [Limpar Cache]

# 3. Reduza histórico em memória:
Configurações → Sessão:
   - Manter histórico por: [90] → [30] dias
   - [✓] Remover automaticamente análises antigas

# 4. Monitore memória:
# Abra Task Manager (Ctrl+Shift+Esc)
# Verifique uso do python.exe
# Se >500 MB: Reinicie sistema
```

---

### ❌ "MemoryError" ao processar grandes placas

**Sintoma**: Erro de memória com muitas amostras.

**Causa**: RAM insuficiente.

**Solução**:
```powershell
# 1. Feche outros programas:
# Libere memória fechando Chrome, etc.

# 2. Processe em lotes menores:
# Divida placa em múltiplas importações

# 3. Desabilite cache:
Configurações → Avançado → [ ] Habilitar cache

# 4. Aumente memória virtual:
# Windows: Configurações → Sistema → Sobre → Configurações avançadas
# → Desempenho → Avançado → Memória virtual → Alterar
# Sugestão: 2x a RAM física

# 5. Upgrade de hardware (longo prazo):
# Mínimo 8 GB RAM recomendado
```

---

### ❌ CPU a 100% constantemente

**Sintoma**: Ventoinhas em máximo, sistema travando.

**Causa**: Processamento pesado ou loop infinito (bug).

**Diagnóstico**:
```powershell
# 1. Verifique no Task Manager:
# Se python.exe > 50% CPU por >5 min → Problema

# 2. Veja logs:
Get-Content .\logs\integragal.log -Tail 100
# Procure por loops ou operações repetitivas

# 3. Desabilite processamento pesado:
Configurações → Performance:
   - [ ] Atualizar dashboard automaticamente
   - [ ] Calcular estatísticas em tempo real
```

**Solução**:
```powershell
# 1. Reinicie sistema

# 2. Reporte bug com logs:
# GitHub Issues + logs/integragal.log

# 3. Solução temporária:
# Use modo de baixo consumo (se disponível em v1.1)
```

---

## Erros de Interface

### ❌ Botões não respondem

**Sintoma**: Clica mas nada acontece.

**Causas**:
- Processamento em background (aguarde)
- Interface travada (bug)
- Modo debug ativo

**Solução**:
```powershell
# 1. Aguarde 10 segundos:
# Pode estar processando

# 2. Verifique barra de status:
# Rodapé mostra "Processando..."

# 3. Se travou:
# Ctrl+Q (sair forçado)
# Reinicie: python main.py

# 4. Desabilite modo debug:
$env:DEBUG=""
python main.py
```

---

### ❌ Texto cortado ou sobreposto

**Sintoma**: Interface com texto truncado ou elementos sobrepostos.

**Causa**: Resolução baixa ou DPI alto.

**Solução**:
```powershell
# 1. Ajuste escala do sistema:
# Windows: Configurações → Sistema → Tela → Escala: [125%] → [100%]

# 2. Aumente tamanho da janela:
# Maximize ou redimensione

# 3. Ajuste fonte no sistema:
Configurações → Aparência → Tamanho da fonte: [13] → [12]

# 4. Para telas 4K:
# Use Windows scaling em vez de mudar fonte do app
```

---

### ❌ Cores incorretas ou modo dark não funciona

**Sintoma**: Tema não muda ou cores estranhas.

**Causa**: Configuração incorreta ou bug no CustomTkinter.

**Solução**:
```powershell
# 1. Troque tema manualmente:
Configurações → Aparência → Modo: [Dark] ↔ [Light]

# 2. Troque cor:
Configurações → Aparência → Cor: [Blue] → [Dark-Blue] → [Green]

# 3. Resete tema padrão:
Copy-Item ".\config\default_config.json" ".\config\config.json" -Force

# 4. Reinstale CustomTkinter:
pip install --upgrade --force-reinstall customtkinter
```

---

### ❌ Gráficos não carregam

**Sintoma**: Área de gráficos fica em branco.

**Causa**: Matplotlib ou erro nos dados.

**Solução**:
```powershell
# 1. Verifique Matplotlib:
python -c "import matplotlib; matplotlib.use('TkAgg'); print('OK')"

# 2. Reinstale:
pip install --upgrade matplotlib

# 3. Altere backend:
# Edite main.py:
import matplotlib
matplotlib.use('TkAgg')

# 4. Teste separadamente:
python
>>> from analise.relatorios_qualidade_gerenciais import gerar_graficos
>>> gerar_graficos()
```

---

## Problemas de Configuração

### ❌ Configurações não salvam

**Sintoma**: Mudanças em configurações não persistem após reinício.

**Causa**: Permissão de escrita ou erro na persistência.

**Solução**:
```powershell
# 1. Verifique permissões:
icacls "C:\IntegRAGal\config\config.json"
# Deve ter (M) - Modify

# 2. Execute como Admin:
# Botão direito no PowerShell → Executar como Administrador

# 3. Verifique se arquivo existe:
Test-Path ".\config\config.json"

# 4. Recrie configuração:
Copy-Item ".\config\default_config.json" ".\config\config.json"

# 5. Teste salvamento:
python
>>> from config.settings import config_manager
>>> config_manager.set("teste", "valor")
>>> config_manager.salvar()
>>> print("Config salva!")
```

---

### ❌ Importar configuração falha

**Sintoma**: Erro ao importar JSON de configuração.

**Causa**: JSON inválido ou incompatível.

**Solução**:
```powershell
# 1. Valide JSON:
python -m json.tool seu_config.json

# Se erro: JSON está malformado

# 2. Verifique versão:
# Abra JSON e procure: "version": "1.0.0"
# Deve ser compatível com sua versão do IntegRAGal

# 3. Use editor JSON:
# https://jsonlint.com
# Cole seu JSON e valide

# 4. Exporte configuração atual e compare:
Configurações → [Exportar] → Compare estruturas
```

---

### ❌ Reset de configuração não funciona

**Sintoma**: Botão "Restaurar Padrões" não tem efeito.

**Solução**:
```powershell
# Manual reset:
Copy-Item ".\config\default_config.json" ".\config\config.json" -Force

# Ou delete para recriar:
Remove-Item ".\config\config.json" -Force
python main.py  # Recria automaticamente
```

---

## Diagnóstico Avançado

### 🔍 Coleta de Logs

Para reportar bugs ou problemas complexos:

```powershell
# 1. Crie pasta de diagnóstico:
New-Item -ItemType Directory -Path ".\diagnostico" -Force

# 2. Copie logs:
Copy-Item ".\logs\*.log" ".\diagnostico\"
Copy-Item ".\logs\*.csv" ".\diagnostico\"

# 3. Exporte configuração:
Copy-Item ".\config\config.json" ".\diagnostico\config.json"

# 4. Info do sistema:
systeminfo > ".\diagnostico\systeminfo.txt"
python --version > ".\diagnostico\python_version.txt"
pip list > ".\diagnostico\pip_list.txt"

# 5. Compacte tudo:
Compress-Archive -Path ".\diagnostico\*" -DestinationPath ".\diagnostico_integragal.zip"

# 6. Envie para suporte ou anexe em GitHub Issue
```

---

### 🔍 Modo Debug

Ative logs detalhados:

```powershell
# 1. Ative debug no ambiente:
$env:DEBUG="1"
$env:LOG_LEVEL="DEBUG"

# 2. Execute:
python main.py

# 3. Logs estarão mais verbosos:
Get-Content .\logs\integragal.log -Wait  # Modo "tail -f"

# 4. Para desativar:
$env:DEBUG=""
$env:LOG_LEVEL="INFO"
```

---

### 🔍 Teste de Integridade

Verifique sistema completo:

```powershell
# Execute suite de testes:
pytest tests/ -v

# Ou teste específico:
pytest tests/test_integracao_completa.py -v

# Verifique imports:
python -c "
from main import *
from extração.busca_extracao import *
from analise.relatorios_qualidade_gerenciais import *
print('Todos imports OK!')
"

# Valide banco de dados:
python
>>> from db.db_utils import validar_banco
>>> validar_banco()
>>> print('Banco OK!')
```

---

### 🔍 Limpeza Completa (Last Resort)

Se tudo falhar, reset completo:

```powershell
# ⚠️ ATENÇÃO: Isso apaga TODOS os dados locais!

# 1. Backup:
Copy-Item ".\banco\" "C:\Backup\IntegRAGal\banco\" -Recurse
Copy-Item ".\reports\" "C:\Backup\IntegRAGal\reports\" -Recurse

# 2. Limpe dados:
Remove-Item ".\data\*" -Recurse -Force
Remove-Item ".\logs\*" -Recurse -Force

# 3. Resete config:
Copy-Item ".\config\default_config.json" ".\config\config.json" -Force

# 4. Reinstale dependências:
pip install --upgrade --force-reinstall -r requirements.txt

# 5. Reinicie:
python main.py
```

---

## 📞 Quando Buscar Suporte

Busque ajuda se:

1. ✅ Seguiu TODAS as soluções acima
2. ✅ Coletou logs de diagnóstico
3. ✅ Problema persiste após reinstalação
4. ✅ Impacta operação crítica

**Canais de Suporte**:
- **GitHub Issues**: https://github.com/Marciopachecolab/IntegRAGal/issues (preferencial para bugs)
- **Email**: suporte@integragal.com (problemas urgentes)
- **Documentação**: `docs/MANUAL_USUARIO.md`, `docs/FAQ.md`

**Inclua sempre**:
- Descrição detalhada do problema
- Passos para reproduzir
- Mensagem de erro completa
- Logs (`diagnostico_integragal.zip`)
- Versão do sistema (`python main.py --version`)

---

**Atualizado**: Dezembro 2025  
**Versão**: 1.0.0  
**Cobertura**: 100+ problemas comuns
