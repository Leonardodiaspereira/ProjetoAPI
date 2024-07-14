import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import time
from datetime import datetime, timedelta
import os
import requests
import json
import zlib

class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Pesquisa Geral")
        self.root.geometry("800x700")

        # Cabeçalho com logo
        self.logo = tk.PhotoImage(file="logo.png")  # Insira o caminho do logo aqui
        self.header = tk.Label(root, image=self.logo)
        self.header.pack()

        # Seleção do caminho da pasta
        self.pasta_label = ttk.Label(root, text="Caminho da Pasta:")
        self.pasta_label.pack(pady=(20, 5))

        self.pasta_entry = ttk.Entry(root, width=50)
        self.pasta_entry.pack()

        self.pasta_button = ttk.Button(root, text="Selecionar Pasta", command=self.selecionar_pasta)
        self.pasta_button.pack(pady=(5, 10))

        # Campos de entrada para data inicial e final
        self.data_inicial_label = ttk.Label(root, text="Data Inicial (dd/mm/yyyy):")
        self.data_inicial_label.pack(pady=(5, 5))

        self.data_inicial_entry = ttk.Entry(root, width=20)
        self.data_inicial_entry.pack()

        self.data_final_label = ttk.Label(root, text="Data Final (dd/mm/yyyy):")
        self.data_final_label.pack(pady=(5, 5))

        self.data_final_entry = ttk.Entry(root, width=20)
        self.data_final_entry.pack()

        # Botões de iniciar e interromper a pesquisa
        self.botoes_frame = ttk.Frame(root)
        self.botoes_frame.pack(pady=(10, 10))

        self.iniciar_button = ttk.Button(self.botoes_frame, text="Iniciar Pesquisa", command=self.iniciar_tarefas)
        self.iniciar_button.pack(side=tk.LEFT, padx=(0, 5))

        self.interromper_button = ttk.Button(self.botoes_frame, text="Clique no [x] para interromper a pesquisa", command=self.interromper_tarefas)
        self.interromper_button.pack(side=tk.LEFT, padx=(5, 0))

        # Área de exibição de logs
        self.log_text = tk.Text(root, height=15, width=70)
        self.log_text.pack(pady=(10, 10))

        # Barra de progresso
        self.progresso = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progresso.pack(pady=(0, 20))

        # Variável de controle para interrupção
        self.interrupcao = False

    def selecionar_pasta(self):
        # Abre o diálogo para seleção de pasta e insere o caminho no campo de entrada
        pasta = filedialog.askdirectory()
        self.pasta_entry.delete(0, tk.END)
        self.pasta_entry.insert(0, pasta)

    def fazer_chamada(self, data_inicial, data_final, posicao, quantidade, pasta):
        # Função para fazer chamadas à API com controle de interrupção
        if self.interrupcao:
            self.log_text.insert(tk.END, "Pesquisa interrompida.\n")
            return False

        # Configura os headers e o payload para a requisição
        headers = {
            'codigo': 'digitar o código aqui',
            'token': 'digitar o token aqui',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'identity'
        }

        payload = {
            "servico": "pesquisa_base_",
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "posicao": posicao,
            "quantidade": quantidade
        }

        while True:
            try:
                # Faz a requisição à API
                response = requests.post('digitar a API aqui', headers=headers,
                                         json=payload, timeout=30)

                if response.status_code == 200:
                    response_data = response.content

                    # Descomprime a resposta se necessário
                    if 'gzip' in response.headers.get('Content-Encoding', ''):
                        response_data = zlib.decompress(response.content, zlib.MAX_WBITS | 16)
                    elif 'deflate' in response.headers.get('Content-Encoding', ''):
                        response_data = zlib.decompress(response.content)

                    response_json = json.loads(response_data)

                    # Verifica o status da resposta
                    if "status" in response_json and response_json["status"] == "2":
                        self.log_text.insert(tk.END, f"Dados em processamento para posição {posicao} no dia {data_inicial}, tentando novamente em 1 minuto...\n")
                        self.log_text.see(tk.END)
                        time.sleep(60)  # Espera 1 minuto antes de tentar novamente
                        continue
                    elif "status" in response_json and response_json["status"] == "0":
                        mensagem = f"Nenhum registro encontrado para posição {posicao} no dia {data_inicial}"
                        self.log_text.insert(tk.END, mensagem + "\n")
                        self.log_text.see(tk.END)
                        return False
                    else:
                        mensagem = f"Chamada para posição {posicao} realizada com sucesso para o dia {data_inicial}"
                        descricao_arquivo = f"{data_inicial.replace('/', '.')}_{posicao}_quantidade{quantidade}.json"
                        with open(os.path.join(pasta, descricao_arquivo), 'w') as arquivo:
                            json.dump(response_json, arquivo)

                        self.log_text.insert(tk.END, mensagem + "\n")
                        self.log_text.see(tk.END)
                        return True
                else:
                    mensagem = f"Erro na chamada para posição {posicao} para o {data_inicial}: {response.text}"
                    self.log_text.insert(tk.END, mensagem + "\n")
                    self.log_text.see(tk.END)
                    return True

            except requests.exceptions.RequestException as e:
                mensagem = f"Erro na requisição: {e}"
                self.log_text.insert(tk.END, mensagem + "\n")
                self.log_text.see(tk.END)
                return True

    def executar_tarefas(self):
        # Função que controla a execução das tarefas de pesquisa
        pasta = self.pasta_entry.get()
        data_inicial_str = self.data_inicial_entry.get()
        data_final_str = self.data_final_entry.get()

        data_inicial = datetime.strptime(data_inicial_str, "%d/%m/%Y").date()
        data_final = datetime.strptime(data_final_str, "%d/%m/%Y").date()

        while data_inicial <= data_final:
            if self.interrupcao:
                self.log_text.insert(tk.END, "Pesquisa interrompida.\n")
                self.interrupcao = False
                break

            data_inicial_str = data_inicial.strftime("%d/%m/%Y")
            data_final_str = data_inicial.strftime("%d/%m/%Y")

            posicao = 1
            quantidade = 1000

            # Primeira chamada
            if not self.fazer_chamada(data_inicial_str, data_final_str, posicao, quantidade, pasta):
                break
            if self.interrupcao:
                break

            # Segunda chamada
            if not self.fazer_chamada(data_inicial_str, data_final_str, posicao, quantidade, pasta):
                break
            if self.interrupcao:
                break

            # Loop para chamadas subsequentes imediatamente após a anterior
            while True:
                posicao += 1000
                quantidade += 1000
                if not self.fazer_chamada(data_inicial_str, data_final_str, posicao, quantidade, pasta):
                    break
                if self.interrupcao:
                    break

            if self.interrupcao:
                break

            data_inicial += timedelta(days=1)

            # Segunda chamada
            if not self.fazer_chamada(data_inicial_str, data_final_str, posicao, quantidade, pasta):
                break
            if self.interrupcao:
                break

            time.sleep(60)

            # Loop para chamadas subsequentes a cada 1 minuto
            while True:
                posicao += 1000
                quantidade += 1000
                if not self.fazer_chamada(data_inicial_str, data_final_str, posicao, quantidade, pasta):
                    break
                if self.interrupcao:
                    break
                time.sleep(60)

            if self.interrupcao:
                break

            data_inicial += timedelta(days=1)

    def iniciar_tarefas(self):
        # Inicia a execução das tarefas em uma thread separada
        self.interrupcao = False
        tarefa_thread = threading.Thread(target=self.executar_tarefas)
        tarefa_thread.start()

    def interromper_tarefas(self):
        # Interrompe a execução das tarefas
        self.interrupcao = True

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
