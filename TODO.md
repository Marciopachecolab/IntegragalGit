TODO: Cadastro de Exames (fonte de verdade: JSON/YAML do registry com fallback nos CSVs; RP padrão 15–35)

Fase 1 — Normalização dos CSVs (definir semântica; ainda sem migrar)
- (feito) Definir semântica: tipo_placa nos CSVs = placa analítica (48, 36, 96...).
- (feito) Mapear exames existentes (VR1e2=48; ZDC=36; demais) e planejar ajustes.
- (feito) Ajustes nos CSVs:
  - (feito) exames_config.csv: uma linha por exame; campos coerentes (exame, modulo_analise/universal, tipo_placa analítica, numero_kit/kit_codigo, equipamento).
  - (feito) exames_metadata.csv: mesma semântica; corrigir VR1e2 para 48; incluir ZDC 36; opcional: colunas kit_codigo/export_fields.
  - (feito) placas.csv: prever entradas 48 (96->48, pares) e 36 (96->36, trios).
  - (feito) placas_metadata.csv: prever linhas 48 (relacao_extracao_analise=1:2, suporta_parte=sim) e 36 (1:3, suporta_parte=sim) com observações.
  - (feito) equipamentos.csv/equipamentos_metadata.csv: verificar cobertura de exames/equipamentos; listar novos se preciso.
  - (feito) regras_analise_metadata.csv: listar alvos e faixas CT por exame; definir RP_min=15, RP_max=35 (override específico se necessário).

Fase 2 — Metadados por exame em JSON/YAML (design)
- (feito) Definir schema em config/exams/<slug>.json (ou .yaml):
  nome_exame, slug, equipamento, tipo_placa_analitica ("48"/"36"/...), esquema_agrupamento ("96->48"/"96->36"/...), kit_codigo,
  alvos, mapa_alvos, faixas_ct (detect_max, inconc_min/max, rp_min/max), rps, export_fields, panel_tests_id, controles (CN/CP).
- (feito) Criar exemplos: VR1e2 e ZDC; template genérico para futuros exames.

Fase 3 — ExamRegistry híbrido
- (feito) Implementar services/exam_registry.py:
  - (feito) Carregar dados mínimos dos CSVs (todos exames).
  - (feito) Se existir JSON/YAML, sobrescrever/complementar dados do CSV.
  - (feito) Expor: alvos, mapa_alvos, faixas_ct, rps, tipo_placa_analitica, esquema_agrupamento (helper bloco), kit_codigo, export_fields, panel_tests_id, controles, equipamento.
  - (feito) Auxiliares: normalizar target_name via mapa_alvos; descobrir tamanho de bloco via esquema_agrupamento/placa.

Fase 4 — Integração do Registry no código
- Engine (universal_engine.py):
  - Usar registry para alvos/faixas CT/RP/agrupamento (cfg = exam_registry.get(exame); fallback CSV).
  - Normalizar target_name via cfg.normalize_target(); resultado/cor considerando todos alvos cfg.alvos; blocos via gabarito/parte_placa e cfg.bloco_size().
- Histórico (services/history_report.py):
  - Gerar colunas ALVO - R / ALVO - CT para todos alvos+RPs de cfg (nomes normalizados via mapa_alvos).
  - status_gal “tipo nao enviavel” para CN/CP/não numéricos; CT com 3 casas (vírgula).
- Mapa (services/plate_viewer.py):
  - Cor/contorno por alvos do exame; RP conforme cfg.faixas_ct; controles azuis.
  - Blocos conforme cfg.bloco_size()/esquema_agrupamento; mostrar alvos do poço e RP uma vez.
- Exportação GAL (menu_handler/main):
  - Usar cfg.export_fields/panel_tests_id/kit_codigo; mapear 1/2/3/""; não exportar CN/CP/não numéricos; gerar CSV do painel correspondente.

Fase 5 — UI de cadastro/edição
- Tela “Gerenciar Exames”: lista exames carregados; formulário Novo/Editar com campos do schema; validar e salvar em config/exams/<slug>.json; recarregar registry.

Fase 6 — Aplicar ajustes e migrar
- (feito) Corrigir exames_metadata.csv (VR1e2->48; incluir ZDC->36; demais).
- (feito) Adicionar placas 36/48 em placas.csv; metadados em placas_metadata.csv.
- (feito) Incluir/atualizar regras_analise_metadata.csv (alvos/faixas; RP 15–35 padrão).
- Criar JSONs em config/exams/ para todos os exames (VR1e2, ZDC, futuros).
- Validar equipamentos_metadata.csv e exames_config.csv coerentes com nomes de equipamento.
- Decidir fonte de export_fields/painel: registry (JSON) como principal; config.json apenas lista de exames ativos ou sincronizado.

Fase 7 — Testes faseados
- Após normalizar CSVs: testar VR1e2 (CSV ajustado, sem JSON).
- Após registry+JSON (ZDC): testar VR1e2 (CSV+registry) e ZDC (CSV+JSON+registry).
- Após integração completa: fixtures de corrida/gabarito para cada exame; validar df_final, histórico, mapa GUI/Excel, CSV GAL.
