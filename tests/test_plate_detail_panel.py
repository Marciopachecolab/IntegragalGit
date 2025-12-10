import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Ajuste de sys.path para permitir imports do pacote de serviços
# ---------------------------------------------------------------------------
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent  # diretório raiz do projeto (onde fica 'services')

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Esperado: Integragal/services/plate_viewer.py
    from services.plate_viewer import PlateModel, PlateView
except ImportError as exc:  # pragma: no cover - falha estrutural de ambiente
    raise ImportError(
        "Não foi possível importar PlateModel/PlateView de 'services.plate_viewer'. "
        "Verifique se o arquivo 'services/plate_viewer.py' existe e se o patch foi "
        "aplicado sobre a pasta correta (Downloads/Integragal)."
    ) from exc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_model() -> PlateModel:
    """Carrega o PlateModel a partir do historico_analises.csv mais recente.

    Usa o mesmo mecanismo lógico já empregado no visualizador de placa: considera
    o arquivo 'reports/historico_analises.csv' que está sob o diretório raiz do
    projeto (PROJECT_ROOT).
    """
    # Caminho padrão: <raiz>/reports/historico_analises.csv
    csv_path = PROJECT_ROOT / "reports" / "historico_analises.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Arquivo de histórico não encontrado em {csv_path}. "
            "Confirme se o teste está sendo executado dentro da pasta correta "
            "(Downloads/Integragal) e se já existem análises salvas."
        )

    # PlateModel.from_historico_csv é a API usada também no resto do projeto
    model = PlateModel.from_historico_csv(str(csv_path))
    return model


def _get_first_well_with_targets(model: PlateModel):
    """Retorna o primeiro poço que possuir alvos (targets) configurados.

    O teste não depende de qual poço exato é usado, apenas precisa de um poço
    que tenha pelo menos um alvo com CT definido.
    """
    wells_attr = getattr(model, "wells", None)
    if not isinstance(wells_attr, dict):
        raise AssertionError(
            "PlateModel.wells deveria ser um dicionário de poços, "
            f"mas foi encontrado: {type(wells_attr)!r}."
        )

    for well in wells_attr.values():
        # Suporte a diferentes nomes de atributo, se o modelo mudou:
        targets = getattr(well, "target_results", None)
        if targets is None:
            targets = getattr(well, "targets", None)

        if isinstance(targets, dict) and targets:
            return well

    raise AssertionError(
        "Nenhum poço com targets foi encontrado em PlateModel.wells. "
        "Verifique se o historico_analises.csv contém dados de resultados."
    )


def _get_targets_dict(well):
    """Obtém o dicionário de alvos (TargetResult) de um poço.

    Abstrai possíveis diferenças de nome de atributo no modelo (target_results vs targets).
    """
    targets = getattr(well, "target_results", None)
    if targets is None:
        targets = getattr(well, "targets", None)

    if not isinstance(targets, dict):
        raise AssertionError(
            "O poço não expõe um dicionário de targets em "
            "'target_results' ou 'targets'."
        )
    return targets


def _parse_float_or_str(value):
    """Converte strings de CT (ex.: '32,5' ou '32.5') em float, quando possível.

    Caso não seja possível converter, retorna a string original (para permitir
    comparações mais flexíveis).
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None
        stripped = stripped.replace(",", ".")
        try:
            return float(stripped)
        except ValueError:
            return value

    return value


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


@pytest.mark.gui
def test_detail_panel_tree_values_match_target_results():
    """
    Verifica se os valores mostrados na Treeview do painel de detalhes
    são consistentes com os TargetResult do modelo (well.targets).

    Para o primeiro poço com alvos:
    - a coluna 'Alvo' (índice 0) deve corresponder à chave do dicionário de targets;
    - a coluna 'CT' (índice 2) deve refletir o mesmo CT armazenado em TargetResult.ct.

    Observação: este teste assume que o PlateView expõe:
    - um método `fill_detail_panel(well)` que popula a Treeview de detalhes;
    - um atributo `tree_targets` (ou `tree`) que é a Treeview de alvos.

    Caso essa API não exista, o teste será marcado como *xfail* com mensagem clara.
    """
    import customtkinter as ctk

    model = _load_model()
    well = _get_first_well_with_targets(model)

    root = ctk.CTk()

    # Tenta instanciar o visualizador usando a API atual do projeto.
    # Se a assinatura mudar, este ponto indicará o problema de forma objetiva.
    try:
        viewer = PlateView(root, model)
    except TypeError as exc:
        pytest.xfail(
            "Não foi possível instanciar PlateView(root, model). "
            "Verifique a assinatura de __init__ em services/plate_viewer.py. "
            f"Erro original: {exc}"
        )
        return

    # Checagem dos atributos esperados
    tree = getattr(viewer, "tree_targets", None)
    if tree is None:
        tree = getattr(viewer, "tree", None)

    fill_fn = getattr(viewer, "fill_detail_panel", None)

    if tree is None or fill_fn is None:
        pytest.xfail(
            "PlateView precisa expor 'tree_targets' (ou 'tree') e "
            "um método 'fill_detail_panel(well)' para que este teste funcione."
        )
        return

    # Popula o painel de detalhes para o poço selecionado
    fill_fn(well)

    targets = _get_targets_dict(well)

    # Para cada alvo configurado nesse poço, garantimos que a treeview
    # está refletindo o mesmo conteúdo de TargetResult para o CT.
    for target_name, target_result in targets.items():
        item_id = target_name
        try:
            item = tree.item(item_id)
        except Exception:
            pytest.fail(
                f"A Treeview não possui item com id '{target_name}'. "
                "Certifique-se de que o método fill_detail_panel utiliza "
                "o nome do alvo como 'iid' na Treeview."
            )
        values = list(item.get("values", []))

        assert len(values) >= 3, (
            "Esperava-se pelo menos 3 colunas na Treeview "
            f"para o alvo '{target_name}'. Valores atuais: {values}"
        )

        alvo_tree = values[0]
        ct_tree = values[2]

        # 1) Nome do alvo deve bater com a chave do dicionário
        assert (
            str(alvo_tree) == str(target_name)
        ), f"Nome do alvo na Treeview ('{alvo_tree}') difere da chave '{target_name}'."

        # 2) CT exibido deve ser coerente com TargetResult.ct
        expected_ct = _parse_float_or_str(getattr(target_result, "ct", None))
        tree_ct = _parse_float_or_str(ct_tree)

        assert (
            expected_ct == tree_ct
        ), f"CT do alvo '{target_name}' diverge entre modelo ({expected_ct}) e Treeview ({tree_ct})."


@pytest.mark.gui
def test_detail_panel_entry_ct_follows_selected_tree_item():
    """
    Simula a seleção de um alvo na Treeview e verifica se o campo de CT
    (`entry_ct`) é preenchido com o mesmo valor de TargetResult.ct.

    Este teste assume que o PlateView expõe:
    - atributo `tree_targets` (ou `tree`) com os alvos;
    - atributo `entry_ct` representando o campo de edição de CT;
    - um método `on_tree_select` ou similar que responda à seleção na Treeview.

    Se a API ainda não estiver implementada dessa forma, o teste será marcado
    como *xfail* com uma mensagem clara para orientar o ajuste.
    """
    import customtkinter as ctk

    model = _load_model()
    well = _get_first_well_with_targets(model)
    targets = _get_targets_dict(well)

    root = ctk.CTk()

    try:
        viewer = PlateView(root, model)
    except TypeError as exc:
        pytest.xfail(
            "Não foi possível instanciar PlateView(root, model). "
            "Verifique a assinatura de __init__ em services/plate_viewer.py. "
            f"Erro original: {exc}"
        )
        return

    tree = getattr(viewer, "tree_targets", None)
    if tree is None:
        tree = getattr(viewer, "tree", None)

    entry_ct = getattr(viewer, "entry_ct", None)

    # Procura um handler de seleção na treeview com nomes comuns
    on_select = None
    for candidate in [
        "on_tree_select",
        "on_target_select",
        "_on_tree_select",
        "_on_target_select",
    ]:
        if hasattr(viewer, candidate):
            on_select = getattr(viewer, candidate)
            break

    if tree is None or entry_ct is None or on_select is None:
        pytest.xfail(
            "PlateView precisa expor 'tree_targets' (ou 'tree'), 'entry_ct' "
            "e um handler de seleção (on_tree_select / on_target_select) "
            "para que este teste funcione."
        )
        return

    # Popula o painel de detalhes para o poço de teste
    fill_fn = getattr(viewer, "fill_detail_panel", None)
    if fill_fn is None:
        pytest.xfail(
            "PlateView não possui 'fill_detail_panel(well)'; ajuste a API "
            "para permitir preencher o painel de detalhes a partir de um poço."
        )
        return

    fill_fn(well)

    # Seleciona o primeiro alvo disponível na tree
    all_items = list(tree.get_children())
    assert all_items, "Nenhum item encontrado na Treeview do painel de detalhes."

    first_item_id = all_items[0]
    tree.selection_set(first_item_id)

    # Dispara o callback de seleção (simulando evento de clique)
    try:
        on_select(event=None)
    except TypeError:
        # Alguns handlers esperam um objeto de evento; usamos um stub simples
        class _DummyEvent:
            def __init__(self, widget):
                self.widget = widget

        on_select(_DummyEvent(tree))

    # Recupera o nome do alvo selecionado a partir da Treeview
    item = tree.item(first_item_id)
    values = list(item.get("values", []))
    assert len(values) >= 3, "Item selecionado na Treeview não possui colunas suficientes."
    target_name = values[0]

    target_result = targets.get(target_name)
    assert target_result is not None, f"Target '{target_name}' não encontrado em well.targets."

    expected_ct = _parse_float_or_str(getattr(target_result, "ct", None))

    # entry_ct pode ser um CTkEntry / Entry padrão; em ambos os casos, usamos .get()
    try:
        entry_value_raw = entry_ct.get()
    except Exception as exc:
        pytest.fail(f"Não foi possível obter valor de entry_ct.get(): {exc}")

    entry_ct_value = _parse_float_or_str(entry_value_raw)

    assert (
        expected_ct == entry_ct_value
    ), f"CT no entry_ct ({entry_ct_value}) difere do CT do modelo ({expected_ct})."
