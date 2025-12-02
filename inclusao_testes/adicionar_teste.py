# FileName: /Integragal/inclusao_testes/adicionar_teste.py
# No inÃ­cio do arquivo inclusao_testes/adicionar_teste.py
import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox
import csv
import os
import sys


# Adiciona o diretÃ³rio base no sys.path para imports locais
# Isso Ã© importante para que as importaÃ§Ãµes absolutas funcionem corretamente
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.config_service import config_service
from utils.logger import registrar_log

# Caminho para o arquivo CSV de configuraÃ§Ã£o de exames
# Usar os.path.join com BASE_DIR para garantir caminho absoluto e robusto
CSV_PATH = os.path.join(BASE_DIR, "banco", "exames_config.csv")

def adicionar_novo_teste():
    """
    Permite ao usuÃ¡rio adicionar um novo exame ao sistema, atualizando
    tanto o arquivo de configuraÃ§Ã£o JSON (config.json) quanto o CSV
    de exames (exames_config.csv).
    """
    registrar_log("InclusÃ£o Teste", "Iniciando processo de adiÃ§Ã£o de novo exame.", level='INFO')
    config = config_service.load() if hasattr(config_service, 'load') else getattr(config_service, '_config', {})
    exames_ativos = config.get("exames_ativos", [])
    exames_config = config.get("exames_config", {})

    # Cria uma janela root temporÃ¡ria para os diÃ¡logos
    root = ctk.CTk() # Usar CTk para consistÃªncia com o resto da aplicaÃ§Ã£o
    root.withdraw() # Esconde a janela principal

    nome_exame = simpledialog.askstring("Novo Exame", "Digite o nome do novo exame:", parent=root)
    if not nome_exame:
        registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: Nome do exame vazio.", level='WARNING')
        messagebox.showerror("Erro", "Nome do exame nÃ£o pode estar vazio.", parent=root)
        root.destroy()
        return

    nome_exame = nome_exame.strip() # Remove espaÃ§os em branco

    # Verificar duplicidade no JSON (exames_ativos)
    if nome_exame in exames_ativos:
        registrar_log("InclusÃ£o Teste", f"AdiÃ§Ã£o de exame cancelada: Exame '{nome_exame}' jÃ¡ existe em exames_ativos (JSON).", level='WARNING')
        messagebox.showwarning("Aviso", f"O exame '{nome_exame}' jÃ¡ estÃ¡ cadastrado na lista de exames ativos (JSON).", parent=root)
        root.destroy()
        return

    # Verificar duplicidade no CSV
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Normaliza para comparaÃ§Ã£o case-insensitive e sem espaÃ§os
                if any(row['exame'].strip().lower() == nome_exame.lower() for row in reader):
                    registrar_log("InclusÃ£o Teste", f"AdiÃ§Ã£o de exame cancelada: Exame '{nome_exame}' jÃ¡ existe no CSV.", level='WARNING')
                    messagebox.showwarning("Aviso", f"O exame '{nome_exame}' jÃ¡ existe no arquivo de configuraÃ§Ã£o CSV!", parent=root)
                    root.destroy()
                    return
        except Exception as e:
            registrar_log("Erro InclusÃ£o Teste", f"Falha ao verificar duplicidade no CSV '{CSV_PATH}': {str(e)}", level='ERROR')
            messagebox.showerror("Erro", f"Erro ao verificar arquivo de exames CSV: {e}", parent=root)
            root.destroy()
            return

    try:
        modulo_funcao = simpledialog.askstring(
            "Novo Exame",
            "Digite o caminho completo da funÃ§Ã£o de anÃ¡lise (ex: analise.vr1.analisar_placa_vr1):",
            parent=root
        )
        if not modulo_funcao:
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: MÃ³dulo de anÃ¡lise vazio.", level='WARNING')
            messagebox.showerror("Erro", "MÃ³dulo de anÃ¡lise Ã© obrigatÃ³rio.", parent=root)
            root.destroy()
            return
        modulo_funcao = modulo_funcao.strip()

        tipo_placa = simpledialog.askstring(
            "Novo Exame",
            "Digite o tipo de placa (ex: 96, 48, 32, etc.):",
            parent=root
        )
        if not tipo_placa:
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: Tipo de placa vazio.", level='WARNING')
            messagebox.showerror("Erro", "Tipo de placa Ã© obrigatÃ³rio.", parent=root)
            root.destroy()
            return
        tipo_placa = tipo_placa.strip()
        if not tipo_placa.isdigit():
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: Tipo de placa invÃ¡lido (nÃ£o numÃ©rico).", level='WARNING')
            messagebox.showerror("Erro", "Tipo de placa deve ser um nÃºmero (ex: 96, 48).", parent=root)
            root.destroy()
            return

        numero_kit = simpledialog.askstring(
            "Novo Exame",
            "Digite o nÃºmero do Kit (cÃ³digo numÃ©rico):",
            parent=root
        )
        if not numero_kit:
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: NÃºmero do kit vazio.", level='WARNING')
            messagebox.showerror("Erro", "NÃºmero do Kit Ã© obrigatÃ³rio.", parent=root)
            root.destroy()
            return
        numero_kit = numero_kit.strip()
        if not numero_kit.isdigit():
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: NÃºmero do kit invÃ¡lido (nÃ£o numÃ©rico).", level='WARNING')
            messagebox.showerror("Erro", "NÃºmero do Kit deve ser um nÃºmero.", parent=root)
            root.destroy()
            return

        equipamento = simpledialog.askstring(
            "Novo Exame",
            "Digite o nome do equipamento (ex: 7500 Real-Time):",
            parent=root
        )
        if not equipamento:
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: Nome do equipamento vazio.", level='WARNING')
            messagebox.showerror("Erro", "Nome do equipamento Ã© obrigatÃ³rio.", parent=root)
            root.destroy()
            return
        equipamento = equipamento.strip()

        campos_resultado = simpledialog.askstring(
            "Novo Exame",
            "Digite os nomes dos campos de resultado separados por vÃ­rgula\n(ex: dengue, chikungunya, zika):",
            parent=root
        )
        if not campos_resultado:
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: Nenhum campo de resultado informado.", level='WARNING')
            messagebox.showerror("Erro", "Ã‰ necessÃ¡rio informar ao menos um campo de resultado.", parent=root)
            root.destroy()
            return
        lista_campos = [campo.strip() for campo in campos_resultado.split(',') if campo.strip()]
        if not lista_campos:
            registrar_log("InclusÃ£o Teste", "AdiÃ§Ã£o de exame cancelada: Lista de campos de resultado vazia apÃ³s processamento.", level='WARNING')
            messagebox.showerror("Erro", "A lista de campos de resultado nÃ£o pode estar vazia.", parent=root)
            root.destroy()
            return

        # ---- Atualiza config.json ----
        exames_ativos.append(nome_exame)
        exames_config[nome_exame] = {
            "kit_codigo": int(numero_kit), # Salva como int
            "export_fields": lista_campos,
            "tipo_placa": int(tipo_placa), # Salva como int
            "equipamento": equipamento
        }
        config["exames_ativos"] = exames_ativos
        config["exames_config"] = exames_config
        # persiste via ConfigService
        try:
            if hasattr(config_service, 'update'):
                config_service.update(config)
            else:
                setattr(config_service, '_config', config)
                if hasattr(config_service, '_save_config'):
                    config_service._save_config()
        except Exception:
            pass
        registrar_log("InclusÃ£o Teste", f"ConfiguraÃ§Ã£o JSON atualizada para o exame '{nome_exame}'.", level='INFO')

        # ---- Atualiza exames_config.csv ----
        arquivo_existe = os.path.exists(CSV_PATH)
        try:
            with open(CSV_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not arquivo_existe or os.stat(CSV_PATH).st_size == 0: # Verifica se o arquivo estÃ¡ vazio tambÃ©m
                    writer.writerow(['exame', 'modulo_analise', 'tipo_placa', 'numero_kit', 'equipamento'])
                    registrar_log("InclusÃ£o Teste", f"CabeÃ§alho CSV criado em '{CSV_PATH}'.", level='INFO')
                writer.writerow([nome_exame, modulo_funcao, tipo_placa, numero_kit, equipamento])
            registrar_log("InclusÃ£o Teste", f"Exame '{nome_exame}' adicionado ao CSV '{CSV_PATH}'.", level='INFO')
        except Exception as e_csv:
            registrar_log("Erro InclusÃ£o Teste", f"Falha ao escrever no CSV '{CSV_PATH}': {str(e_csv)}", level='CRITICAL')
            messagebox.showerror("Erro CSV", f"Erro crÃ­tico ao salvar no arquivo de exames CSV: {e_csv}\n\nO exame foi salvo no JSON, mas nÃ£o no CSV. Por favor, corrija manualmente.", parent=root)
            root.destroy()
            return

        registrar_log("InclusÃ£o Teste", f"Exame '{nome_exame}' adicionado com sucesso. MÃ³dulo: {modulo_funcao}, Kit: {numero_kit}, Campos: {lista_campos}", level='INFO')
        messagebox.showinfo("Sucesso", f"âœ”ï¸ Novo exame '{nome_exame}' adicionado com sucesso!", parent=root)

    except Exception as e:
        registrar_log("Erro InclusÃ£o Teste", f"Erro inesperado ao adicionar exame '{nome_exame}': {str(e)}", level='ERROR')
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado ao adicionar o exame: {str(e)}", parent=root)
    finally:
        root.destroy() # Garante que a janela temporÃ¡ria seja destruÃ­da

