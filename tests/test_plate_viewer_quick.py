import pandas as pd

from services.plate_viewer import PlateModel, STATUS_COLORS

from services.exam_registry import get_exam_cfg



# Cria DataFrame de exemplo com RP, controles e um alvo anal√≠tico

records = [

    {"Poco": "A01", "Amostra": "S_RP_OK", "Codigo": "C1", "RP": 36.5, "Resultado_INFA": "ND", "INFA": ""},

    {"Poco": "A02", "Amostra": "S_RP_INC", "Codigo": "C2", "RP": 39.0, "Resultado_INFA": "ND", "INFA": ""},

    {"Poco": "A03", "Amostra": "CN_CONTROL", "Codigo": "CN", "RP": 37.0, "Resultado_INFA": "ND", "INFA": ""},

    {"Poco": "A04", "Amostra": "CP_CONTROL", "Codigo": "CP", "RP": 37.5, "Resultado_INFA": "ND", "INFA": ""},

    {"Poco": "A05", "Amostra": "S_POS", "Codigo": "P5", "RP": None, "Resultado_INFA": "Detectado", "INFA": 22.4},

]



df = pd.DataFrame(records)



# Use exam known from prior checks (fallbacks present)

exame = "vr1e2_biomanguinhos_7500"



print("Loading exam_cfg for:", exame)

try:

    cfg = get_exam_cfg(exame)

    print("exam_cfg loaded: has faixas_ct =", bool(getattr(cfg, 'faixas_ct', None)))

except Exception as e:

    cfg = None

    print("exam_cfg load failed:", e)



model = PlateModel.from_df(df, exame=exame)

print(f"Model loaded, group_size={model.group_size}, exam_cfg present={model.exam_cfg is not None}")



print('\nWell statuses:')

for wid in sorted(model.wells.keys()):

    w = model.get_well(wid)

    print(wid, "sample=", w.sample_id, "code=", w.code, "is_control=", w.is_control, "control_type=", w.metadata.get('control_type'), "status=", w.status)



print('\nSTATUS_COLORS sample:')

for k,v in STATUS_COLORS.items():

    print(k, v)

