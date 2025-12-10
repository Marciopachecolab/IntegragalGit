# ❓ FAQ - Perguntas Frequentes

**IntegRAGal - Respostas para as dúvidas mais comuns**

---

## 📑 Índice

- [Instalação e Configuração](#instalação-e-configuração)
- [Uso Básico](#uso-básico)
- [Análise de Resultados](#análise-de-resultados)
- [Alertas e Notificações](#alertas-e-notificações)
- [Exportação e Relatórios](#exportação-e-relatórios)
- [Integração com GAL](#integração-com-gal)
- [Performance e Otimização](#performance-e-otimização)
- [Segurança e Backup](#segurança-e-backup)
- [Troubleshooting](#troubleshooting)

---

## Instalação e Configuração

### 1. Qual versão do Python é necessária?

**R**: Python 3.10 ou superior. Recomendamos **Python 3.13** para melhor performance.

Verifique sua versão:
```powershell
python --version
```

### 2. Posso instalar em qualquer diretório?

**R**: Sim, mas recomendamos `C:\IntegRAGal` para facilitar manutenção e seguir as convenções do manual.

### 3. O sistema funciona no Linux ou Mac?

**R**: O sistema foi desenvolvido para Windows, mas pode funcionar em Linux/Mac com Python 3.10+ instalado. Algumas funcionalidades (como caminhos de arquivo) podem precisar de ajustes.

### 4. Preciso de conexão com internet para usar?

**R**: Não para uso local. Internet é necessária apenas para:
- Envio de resultados para GAL
- Verificação de atualizações (se habilitado)
- Download de dependências na instalação

### 5. Como mudo o idioma do sistema?

**R**: Atualmente o sistema está disponível apenas em Português. Suporte multilíngue está planejado para versões futuras.

### 6. Posso usar em múltiplos computadores?

**R**: Sim. Instale o sistema em cada computador. Você pode exportar e importar configurações para manter consistência entre máquinas.

---

## Uso Básico

### 7. Esqueci minha senha. Como recupero?

**R**: Entre em contato com o administrador do sistema. Ele pode resetar sua senha no arquivo `banco/usuarios.csv`.

**Admin**: Para resetar senha de usuário:
1. Abra `banco/usuarios.csv`
2. Localize o usuário
3. Altere a senha (será hasheada no próximo login)

### 8. Posso ter múltiplos usuários?

**R**: Sim! O sistema suporta múltiplos usuários com controle de acesso individual. Configure em `Configurações → Usuários`.

### 9. Como funciona o sistema de alertas?

**R**: O sistema monitora automaticamente:
- CTs fora dos limites configurados
- Controles positivos/negativos inválidos
- Placas não mapeadas
- Amostras com dados inconsistentes
- Erros de extração

Alertas aparecem no badge 🔔 no topo da tela.

### 10. Posso desativar os alertas?

**R**: Sim. Em `Configurações → Alertas`, desmarque "Habilitar Sistema de Alertas". **Não recomendado** para uso em produção.

### 11. O que são "placas não mapeadas"?

**R**: São placas cujo identificador não está cadastrado no sistema. Você precisa mapear a placa para associá-la às amostras corretas.

Para mapear: `Extração → [Mapear Manualmente]`

### 12. Posso editar resultados após análise?

**R**: Sim, com ressalvas:
- Duplo clique na amostra abre editor
- Todas as edições são registradas no log de auditoria
- Amostras já enviadas para GAL não podem ser editadas

---

## Análise de Resultados

### 13. Quais equipamentos são suportados?

**R**: Atualmente:
- ✅ QuantStudio 3
- ✅ QuantStudio 5  
- ✅ QuantStudio 7

Outros equipamentos serão adicionados em futuras atualizações.

### 14. Qual formato de arquivo devo usar?

**R**: Arquivos Excel (`.xlsx` ou `.xls`) exportados diretamente do software do QuantStudio. CSV também é aceito, mas Excel é preferível por conter mais metadados.

### 15. O que significa "CT Undetermined"?

**R**: "Undetermined" (Und) significa que não houve amplificação detectada. A amostra é interpretada como **negativa**.

### 16. Como o sistema calcula se uma amostra é positiva ou negativa?

**R**: Regras padrão:
- **Positivo**: CT detectado e abaixo do limite superior (padrão: 35)
- **Negativo**: CT Undetermined ou acima do limite
- **Inconclusivo**: Situações ambíguas (ex: apenas 1 de 2 alvos positivo)

Regras podem ser personalizadas em `Configurações → Análise`.

### 17. O que são outliers e como são detectados?

**R**: Outliers são valores estatisticamente muito diferentes do padrão. O sistema usa o método **IQR (Interquartile Range)** por padrão:

```
Outlier se: valor < Q1 - 1.5*IQR  OU  valor > Q3 + 1.5*IQR
```

Pode indicar erro técnico ou amostra atípica.

### 18. Posso processar múltiplas placas de uma vez?

**R**: Atualmente não. Você deve processar uma placa por vez. Processamento em lote está planejado para v1.1.

### 19. Como validar controles positivos e negativos?

**R**: O sistema valida automaticamente ao aplicar regras:
- **Controle Positivo**: DEVE amplificar (CT < 30, configurável)
- **Controle Negativo**: NÃO deve amplificar (CT = Und)

Se falhar, alerta é gerado automaticamente.

### 20. O que fazer quando controle negativo amplifica?

**R**: **Suspeita de contaminação**:
1. Verificar curva de amplificação (pode ser artefato)
2. Comparar com outras amostras da placa
3. Verificar CT (se muito alto, pode ser background)
4. **Se confirmado**: Invalidar placa e repetir análise
5. Investigar fonte de contaminação

---

## Alertas e Notificações

### 21. Quantos tipos de alertas existem?

**R**: 9 tipos:
1. 🔴 CT Alto
2. 🟡 CT Baixo
3. 🔵 Placa Não Mapeada
4. ⚪ Amostra Inválida
5. 🟠 Erro Extração
6. 🟣 Aviso Qualidade
7. 🔵 Info Sistema
8. 🟢 Operação Sucesso
9. 🔴 Erro Crítico

### 22. Qual a diferença entre "Marcar como Lido" e "Resolver"?

**R**:
- **Marcar como Lido**: Remove da contagem de não lidos, mas mantém alerta ativo
- **Resolver**: Marca o alerta como completamente tratado (com observação opcional)

### 23. Alertas antigos são deletados automaticamente?

**R**: Sim, se configurado em `Configurações → Performance → Limpar alertas antigos`. Padrão: 7 dias. Alertas críticos e não resolvidos são sempre mantidos.

### 24. Posso exportar histórico de alertas?

**R**: Sim! `Centro de Notificações → [Exportar]`. Formatos: Excel, CSV, PDF.

### 25. Badge de alertas está sempre vermelho. É normal?

**R**: Badge muda de cor conforme quantidade:
- **Verde**: 0 alertas
- **Amarelo**: 1-5 alertas
- **Vermelho**: >5 alertas

Se sempre vermelho, você pode estar acumulando muitos alertas. Revise e resolva-os periodicamente.

---

## Exportação e Relatórios

### 26. Qual formato de exportação devo usar?

**R**: Depende do uso:
- **PDF**: Documentação oficial, impressão, arquivamento
- **Excel**: Análise posterior, compartilhamento, edição
- **CSV**: Importação em outros sistemas, análise estatística

### 27. Posso personalizar o relatório PDF?

**R**: Sim! `Configurações → Exportação`:
- Incluir/excluir seções
- DPI dos gráficos (150-600)
- Orientação (retrato/paisagem)
- Logo da instituição

### 28. Relatórios incluem gráficos?

**R**: Sim, se habilitado em `Configurações → Exportação → [✓] Incluir gráficos`. Inclui:
- Histograma de CT
- Gráficos de amplificação
- Mapa de calor da placa
- Estatísticas descritivas

### 29. Posso exportar apenas amostras positivas?

**R**: Sim! Use filtros antes de exportar:
1. Na tela de análise: `Resultado → [Positivo]`
2. Exportar → Apenas dados filtrados serão incluídos

Ou crie template customizado: `Configurações → Exportação → Templates → [+ Novo]`

### 30. Onde os relatórios são salvos?

**R**: Por padrão em `reports/`. Você pode mudar em `Configurações → Exportação → Diretório padrão`.

### 31. Posso incluir observações no relatório?

**R**: Sim! Antes de exportar, adicione observações gerais na tela de análise. Elas serão incluídas no relatório.

---

## Integração com GAL

### 32. O que é GAL?

**R**: GAL (Gerenciador de Ambiente Laboratorial) é o sistema do Ministério da Saúde brasileiro para gerenciar resultados laboratoriais em saúde pública.

### 33. Preciso configurar algo antes de enviar para GAL?

**R**: Sim. `Configurações → GAL`:
- URL do servidor GAL
- Suas credenciais (usuário e senha)
- Teste a conexão antes do primeiro envio

### 34. Todos os resultados devem ser enviados para GAL?

**R**: Depende da sua instituição e tipo de exame. Geralmente, testes de vigilância epidemiológica (COVID-19, Influenza, etc.) devem ser enviados.

### 35. O que acontece se envio para GAL falhar?

**R**: O sistema:
1. Registra o erro no log
2. Mantém os dados localmente
3. Permite reenvio posterior em `Histórico → Envios GAL → [Reenviar]`

### 36. Posso enviar resultados parciais?

**R**: Sim. Durante o envio, você pode:
- [ ] Incluir amostras com alertas
- Enviar apenas amostras validadas

### 37. Como rastrear envios para GAL?

**R**: `Histórico → Envios GAL`. Você verá:
- Data/hora do envio
- Status (Sucesso, Parcial, Erro)
- Protocolo GAL
- Log detalhado

### 38. GAL rejeitou minhas amostras. O que fazer?

**R**: Verifique o log de erro. Motivos comuns:
- Amostra já cadastrada
- CPF inválido
- Data fora do período permitido
- Campos obrigatórios faltando

Corrija no sistema e reenvie.

---

## Performance e Otimização

### 39. Sistema está lento. O que fazer?

**R**: Verificações:
1. **Memória**: Fechar outros programas
2. **Cache**: `Configurações → Performance → [Limpar Cache]`
3. **Alertas**: Limpar alertas antigos
4. **Histórico**: Remover análises antigas

Se persistir, veja `docs/TROUBLESHOOTING.md`.

### 40. Quantas análises posso ter no histórico?

**R**: Não há limite fixo, mas para melhor performance recomendamos:
- Manter últimos 3 meses (~90 dias)
- Arquivar análises antigas
- Limpar periodicamente

Configure em: `Configurações → Sessão → Manter histórico por: [90] dias`

### 41. Sistema usa muita memória?

**R**: Uso normal: 100-200 MB. Se ultrapassar:
- Reduza `Configurações → Performance → Máximo de alertas na memória`
- Desabilite `Configurações → Avançado → Habilitar cache`
- Diminua `Tamanho do cache`

### 42. Posso usar em computador antigo?

**R**: Requisitos mínimos:
- Windows 10
- 4 GB RAM
- CPU dual-core

Funciona, mas pode ser mais lento. Recomendamos 8 GB RAM e CPU quad-core para melhor experiência.

---

## Segurança e Backup

### 43. Onde ficam armazenados meus dados?

**R**: Localmente no computador:
```
C:\IntegRAGal\
├── banco\          # Banco de dados CSV
├── reports\        # Relatórios exportados
├── config\         # Configurações
├── data\           # Dados de estado e cache
└── logs\           # Logs do sistema
```

**Não há armazenamento em nuvem** por padrão.

### 44. Como fazer backup?

**R**: Manualmente:
1. Copie a pasta `C:\IntegRAGal\banco\` para local seguro
2. Copie `C:\IntegRAGal\config\` (configurações)
3. Opcional: `reports\` (relatórios)

Automático (planejado para v1.1): Backup agendado em pasta externa ou nuvem.

### 45. Senhas são armazenadas com segurança?

**R**: Sim. Senhas são **hasheadas** (SHA-256) antes de serem armazenadas. Nunca são salvas em texto puro.

### 46. Posso restringir acesso de usuários?

**R**: Sistema básico de controle de acesso está implementado. Recursos avançados (perfis, permissões granulares) estão planejados para v1.2.

### 47. Dados são transmitidos criptografados para GAL?

**R**: Sim. Conexão com GAL usa **HTTPS** (TLS/SSL), garantindo criptografia dos dados em trânsito.

### 48. Como restaurar backup?

**R**: Feche o sistema e copie arquivos de backup sobre os atuais:
```powershell
# Backup manual
Copy-Item "D:\Backup\banco\*" "C:\IntegRAGal\banco\" -Force

# Reinicie o sistema
python main.py
```

---

## Troubleshooting

### 49. Erro: "ModuleNotFoundError: No module named 'customtkinter'"

**R**: Dependências não instaladas. Execute novamente:
```powershell
.\install.bat
```
Ou manualmente:
```powershell
pip install -r requirements.txt
```

### 50. Erro: "PermissionError: [Errno 13]"

**R**: Sistema sem permissão para escrever. Causas:
- Arquivo aberto em outro programa (Excel, PDF)
- Pasta protegida (execute como Administrador)
- Antivírus bloqueando

### 51. Gráficos não aparecem no relatório PDF

**R**: Verifique:
1. `Configurações → Exportação → [✓] Incluir gráficos`
2. Matplotlib instalado: `pip install matplotlib`
3. Espaço em disco suficiente

### 52. Sistema não abre após atualização

**R**: Limpe cache:
```powershell
Remove-Item "C:\IntegRAGal\data\state\cache\*" -Force
python main.py
```

### 53. Arquivos Excel não são reconhecidos

**R**: Certifique-se que:
- Arquivo é do QuantStudio (formato correto)
- Extensão é `.xlsx` ou `.xls`
- Arquivo não está corrompido
- Tente "Salvar Como" do Excel para recriar arquivo

### 54. "Erro ao conectar com GAL: Timeout"

**R**: Verificações:
1. Conexão com internet está OK?
2. Servidor GAL está online? (teste em navegador)
3. Firewall/antivírus bloqueando?
4. Aumente timeout: `Configurações → GAL → Timeout: [60] seg`

### 55. Dashboard não carrega análises recentes

**R**: Cache corrompido. Solução:
```powershell
python -c "from utils.persistence import persistence; persistence.limpar_cache()"
```
Ou: `Configurações → Avançado → [Limpar Cache]`

---

## Perguntas Técnicas

### 56. Qual linguagem o sistema é desenvolvido?

**R**: **Python 3.13** com:
- CustomTkinter (interface)
- Pandas (análise de dados)
- Matplotlib (gráficos)
- ReportLab (PDF)

### 57. Posso ver o código-fonte?

**R**: Sim! Sistema é open-source:
https://github.com/Marciopachecolab/IntegRAGal

### 58. Como contribuir com o projeto?

**R**: 
1. Fork o repositório
2. Crie branch para sua feature
3. Faça suas mudanças
4. Envie Pull Request

Veja `CONTRIBUTING.md` para detalhes.

### 59. Há API para integração externa?

**R**: API REST está em desenvolvimento para v1.2. Permitirá:
- Submeter resultados programaticamente
- Consultar análises
- Exportar dados
- Gerenciar alertas

### 60. Posso personalizar cores e layout?

**R**: Parcialmente. `Configurações → Aparência`:
- Modo (Dark/Light)
- Cor do tema (Blue/Green/Dark-Blue)
- Tamanho da fonte

Customização completa de temas planejada para v1.3.

---

## 📞 Não Encontrou Sua Pergunta?

- **Manual Completo**: `docs/MANUAL_USUARIO.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Email**: suporte@integragal.com
- **GitHub Issues**: https://github.com/Marciopachecolab/IntegRAGal/issues

---

**Atualizado**: Dezembro 2025  
**Versão**: 1.0.0  
**Total de Perguntas**: 60
