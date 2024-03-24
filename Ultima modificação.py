import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import requests
import json
import os

# Defini uma variável global para rastrear se começamos a pesquisa ou não
pesquisa_iniciada = False

# Criei uma função para fazer a pesquisa
def fazer_pesquisa(data_inicial, data_final):
    try:
        url = 'URL_DA_API_AQUI'  # Aqui tem que preencher com o Link da API

        headers = {
            'código': 'JONATHAN.SANTOS',
            'token': 'E7747A94-497E-4DE6-ACE5-AA5CC5CC1ABF'
        }

        payload = {
            "servico": "pesq_geral",
            "DataInicial": data_inicial,
            "DataFinal": data_final
        }
        # Faço a solicitação a API nessa função

        response = requests.post(url, headers=headers, json=payload)

        # Essa função verifica se a solicitação foi bem-sucedida, se for igual a 200 é porque deu certo
        # Se não vai gerar um erro
        if response.status_code == 200:
            return response.json()  # Retorna os dados obtidos
        else:
            print("Erro ao fazer a solicitação:", response.status_code)
            return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
        return None

# Aqui eu criei uma função para parar a pesquisa se for necessário
def abortar_pesquisa():
    global pesquisa_abortada
    pesquisa_abortada = True

# Aqui eu criei a função principal para executar a pesquisa
def executar_pesquisa():
    global pesquisa_abortada
    global pesquisa_iniciada

    # Aqui informo que começamos a pesquisa
    pesquisa_iniciada = True

    # Mostra o botão "Abortar Pesquisa"
    button_abortar.grid(row=4, column=1, padx=5, pady=5)

    pesquisa_abortada = False

    # Aqui esse bloco de códigos pega os valores inseridos nos campos de data e hora
    data_inicio = entry_data_inicio.get()
    hora_inicio = entry_hora_inicio.get()
    data_fim = entry_data_fim.get()
    hora_fim = entry_hora_fim.get()

    try:
        # Esse bloco faz a coversçao dos valores para o formato de data e hora
        data_inicial = datetime.strptime(data_inicio + ' ' + hora_inicio, "%d/%m/%Y %H:%M:%S")
        data_final = datetime.strptime(data_fim + ' ' + hora_fim, "%d/%m/%Y %H:%M:%S")

        # Nessa parte é aonde é definida o inetrvalo para as pesquisas
        intervalo = timedelta(hours=3)

        # Aqui é necessário colocar a paste que os arquivos vai ser salvos
        pasta_destino = r'C:\Users\Leona\Desktop\Pesquisa_LisNet'

        # Essa função cira uma pasta de destino se não existir
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        # Criei essa função para ver o progresso da pesquisa
        progresso.config(maximum=100, value=0)

        total_iteracoes = (data_final - data_inicial) // intervalo
        iteracao_atual = 0

        while data_inicial < data_final and not pesquisa_abortada:
            resultado = fazer_pesquisa(data_inicial.strftime("%d/%m/%Y %H:%M:%S"), (data_inicial + intervalo).strftime("%d/%m/%Y %H:%M:%S"))

            # Aqui eu criei o Loop para fazer as pesquisas

            if resultado:
                # Esaa função cria o nome do arquivo com a data e hora atual
                nome_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S") + '.json'
                caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

                # Salva o resultado no arquivo json
                with open(caminho_arquivo, 'w') as arquivo:
                    json.dump(resultado, arquivo, indent=4)

                print(f"Resultado salvo em {caminho_arquivo}")
            else:
                print("Erro ao fazer a busca")

            data_inicial += intervalo
            iteracao_atual += 1

            # Atualiza a barra de progresso
            progresso.config(value=(iteracao_atual / total_iteracoes) * 100)
            root.update()

        # Essa função eu criei para verificar se a pesquisa foi abortada ou concluída
        if pesquisa_abortada:
            messagebox.showinfo("Pesquisa Abortada", "A pesquisa foi abortada pelo usuário!")
        else:
            messagebox.showinfo("Pesquisa Concluída", "A pesquisa foi concluída com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Interface gráfica, aqui eu criei a janela principal
root = tk.Tk()
root.title("Pesquisa LisNet")

# Aqui eu defino as dimensões e a posição da janela
largura_janela = 400
altura_janela = 300
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
posicao_x = (largura_tela - largura_janela) // 2
posicao_y = (altura_tela - altura_janela) // 2
root.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")

#Aqui eu crio e posiciono os widgets na janela
label_data_inicio = tk.Label(root, text="Data de Início (dd/mm/aaaa):")
label_data_inicio.grid(row=0, column=0, padx=5, pady=5)
entry_data_inicio = tk.Entry(root)
entry_data_inicio.grid(row=0, column=1, padx=5, pady=5)

label_hora_inicio = tk.Label(root, text="Hora de Início (hh:mm:ss):")
label_hora_inicio.grid(row=1, column=0, padx=5, pady=5)
entry_hora_inicio = tk.Entry(root)
entry_hora_inicio.grid(row=1, column=1, padx=5, pady=5)

label_data_fim = tk.Label(root, text="Data de Fim (dd/mm/aaaa):")
label_data_fim.grid(row=2, column=0, padx=5, pady=5)
entry_data_fim = tk.Entry(root)
entry_data_fim.grid(row=2, column=1, padx=5, pady=5)

label_hora_fim = tk.Label(root, text="Hora de Fim (hh:mm:ss):")
label_hora_fim.grid(row=3, column=0, padx=5, pady=5)
entry_hora_fim = tk.Entry(root)
entry_hora_fim.grid(row=3, column=1, padx=5, pady=5)

button_executar = tk.Button(root, text="Executar Pesquisa", command=executar_pesquisa)
button_executar.grid(row=4, column=0, padx=5, pady=5)

# Aqui eu coloco meu copyright no rodapé
copyright_label = tk.Label(root, text="Copyright © 2024 - Todos os Direitos Reservados - Leonardo Dias Pereira", anchor="w")
copyright_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# Aqui eu crio o botão "Abortar Pesquisa" (inicialmente oculto)
button_abortar = tk.Button(root, text="Abortar Pesquisa", command=abortar_pesquisa)
button_abortar.grid(row=4, column=1, padx=5, pady=5)
button_abortar.grid_remove()

# Barra de progresso
progresso = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progresso.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Iniciar o loop principal da aplicação
root.mainloop()
