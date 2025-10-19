import tkinter as tk
from tkinter import simpledialog, messagebox
from config import carregar_config, salvar_config
from utils.logger import registrar_log

def abrir_configuracao():
    config = carregar_config()

    root = tk.Tk()
    root.withdraw()

    nova_pasta_csv = simpledialog.askstring("ConfiguraÃ§Ã£o", f"Pasta de CSVs atual: {config['diretorios']['pasta_csv']}\nDigite o novo caminho (ou deixe vazio para manter):")
    if nova_pasta_csv:
        config['diretorios']['pasta_csv'] = nova_pasta_csv

    novo_nome_lab = simpledialog.askstring("ConfiguraÃ§Ã£o", f"Nome do laboratÃ³rio atual: {config['laboratorio']['nome']}\nDigite o novo nome (ou deixe vazio para manter):")
    if novo_nome_lab:
        config['laboratorio']['nome'] = novo_nome_lab

    novos_exames = simpledialog.askstring("ConfiguraÃ§Ã£o", f"Exames ativos atuais: {', '.join(config['exames_ativos'])}\nDigite os exames ativos separados por vÃ­rgula:")
    if novos_exames:
        config['exames_ativos'] = [x.strip() for x in novos_exames.split(',') if x.strip()]

    # Editar configuraÃ§Ã£o PostgreSQL
    nova_dbname = simpledialog.askstring("ConfiguraÃ§Ã£o PostgreSQL", f"Nome do banco atual: {config['postgres']['dbname']}\nNovo nome do banco:")
    if nova_dbname:
        config['postgres']['dbname'] = nova_dbname

    novo_user = simpledialog.askstring("ConfiguraÃ§Ã£o PostgreSQL", f"UsuÃ¡rio atual: {config['postgres']['user']}\nNovo usuÃ¡rio:")
    if novo_user:
        config['postgres']['user'] = novo_user

    novo_host = simpledialog.askstring("ConfiguraÃ§Ã£o PostgreSQL", f"Host atual: {config['postgres']['host']}\nNovo host:")
    if novo_host:
        config['postgres']['host'] = novo_host

    salvar_config(config)
    registrar_log("ConfiguraÃ§Ã£o Alterada", "ConfiguraÃ§Ãµes do sistema atualizadas.")
    messagebox.showinfo("ConfiguraÃ§Ã£o", "âœ”ï¸ ConfiguraÃ§Ã£o salva com sucesso.")
