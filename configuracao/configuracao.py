import tkinter as tk
from tkinter import simpledialog, messagebox
from services.config_service import config_service
from utils.logger import registrar_log


def abrir_configuracao():
    # carrega configuracao atual do ConfigService
    config = config_service.load() if hasattr(config_service, "load") else getattr(config_service, "_config", {})

    root = tk.Tk()
    root.withdraw()

    nova_pasta_csv = simpledialog.askstring(
        "Configuração",
        f"Pasta de CSVs atual: {config['paths'].get('exams_catalog_csv', '')}\nDigite o novo caminho (ou deixe vazio para manter):",
        parent=root,
    )
    if nova_pasta_csv:
        # mantém chave compatível com ConfigService (paths)
        config.setdefault('paths', {})['exams_catalog_csv'] = nova_pasta_csv

    novo_nome_lab = simpledialog.askstring(
        "Configuração",
        f"Nome do laboratório atual: {config.get('laboratorio', {}).get('nome', 'LACEN')}\nDigite o novo nome (ou deixe vazio para manter):",
        parent=root,
    )
    if novo_nome_lab:
        config.setdefault('laboratorio', {})['nome'] = novo_nome_lab

    exames_ativos = config.get('exames_ativos', [])
    novos_exames = simpledialog.askstring(
        "Configuração",
        f"Exames ativos atuais: {', '.join(exames_ativos)}\nDigite os exames ativos separados por vírgula:",
        parent=root,
    )
    if novos_exames:
        config['exames_ativos'] = [x.strip() for x in novos_exames.split(',') if x.strip()]

    # Editar configuração PostgreSQL
    pg = config.setdefault('postgres', {})
    nova_dbname = simpledialog.askstring(
        "Configuração PostgreSQL",
        f"Nome do banco atual: {pg.get('dbname', '')}\nNovo nome do banco:",
        parent=root,
    )
    if nova_dbname:
        pg['dbname'] = nova_dbname

    novo_user = simpledialog.askstring(
        "Configuração PostgreSQL",
        f"Usuário atual: {pg.get('user', '')}\nNovo usuário:",
        parent=root,
    )
    if novo_user:
        pg['user'] = novo_user

    novo_host = simpledialog.askstring(
        "Configuração PostgreSQL",
        f"Host atual: {pg.get('host', '')}\nNovo host:",
        parent=root,
    )
    if novo_host:
        pg['host'] = novo_host

    # salvar via ConfigService
    try:
        if hasattr(config_service, 'update'):
            config_service.update(config)  # salva e persiste
        else:
            # fallback para métodos privados
            setattr(config_service, '_config', config)
            if hasattr(config_service, '_save_config'):
                config_service._save_config()
    except Exception:
        pass

    registrar_log("Configuração Alterada", "Configurações do sistema atualizadas.")
    messagebox.showinfo("Configuração", "Configuração salva com sucesso.", parent=root)

