import json
import os
from time import sleep
from prettytable import PrettyTable
import argparse
import schedule
from datetime import datetime, timedelta
import re

class Cor:
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIANO = '\033[96m'
    RESET = '\033[0m'

arquivo = os.path.join(os.path.dirname(__file__), 'restaurantes.json')
arquivo_reservas = os.path.join(os.path.dirname(__file__), 'reservas.json')

def enviar_email(destinatario, assunto, corpo):
    print(f"{Cor.CIANO}Enviando email de confirmação para {destinatario}...{Cor.RESET}")
    print(f"Assunto: {assunto}")
    print(f"Corpo:\n{corpo}")
    sleep(2)
    print(f"{Cor.VERDE}Email de confirmação enviado com sucesso!{Cor.RESET}")

def validar_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def validar_data(data):
    try:
        data_reserva = datetime.strptime(data, '%d/%m/%Y')
        if data_reserva.date() >= datetime.now().date():
            return True
        else:
            return False
    except ValueError:
        return False

def validar_horario(horario):
    try:
        datetime.strptime(horario, '%H:%M')
        return True
    except ValueError:
        return False

def carregar_arquivo(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            return json.load(f)
    else:
        return []

def salvar_arquivo(arquivo, dados):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=4)

def adicionar_reserva(nome, data, horario, restaurante, email):
    reservas = carregar_arquivo(arquivo_reservas)

    nova_reserva = {'nome': nome, 'data': data, 'horario': horario, 'restaurante': restaurante, 'email': email}
    reservas.append(nova_reserva)

    salvar_arquivo(arquivo_reservas, reservas)

    print(f"{Cor.VERDE}😎 RESERVA ADICIONADA COM SUCESSO!{Cor.RESET}")

    assunto = "Confirmação de Reserva"
    corpo = f"Olá {nome},\n\nSua reserva foi confirmada para o dia {data} às {horario} no restaurante {restaurante}.\n\nObrigado!"
    enviar_email(email, assunto, corpo)

def listar_restaurantes():
    restaurantes = carregar_arquivo(arquivo)

    if restaurantes:
        print("=" * 50)
        print("LISTA DE RESTAURANTES:")
        print("-" * 50)
        tabela = PrettyTable(['id', 'Nome', 'Cozinha', 'Horário', 'Avaliação'])
        for restaurante in restaurantes:
            tabela.add_row([restaurante['id'], restaurante['nome'], restaurante['cozinha'], restaurante['horario'], restaurante['avaliacao']])
        print(tabela)
    else:
        print("😒 NENHUM RESTAURANTE ENCONTRADO.")

def atualizar_reserva(nome_antigo, novo_nome, nova_data, novo_horario, novo_restaurante, novo_email):
    reservas = carregar_arquivo(arquivo_reservas)

    for reserva in reservas:
        if reserva['nome'] == nome_antigo:
            reserva['nome'] = novo_nome
            reserva['data'] = nova_data
            reserva['horario'] = novo_horario
            reserva['restaurante'] = novo_restaurante
            reserva['email'] = novo_email
            salvar_arquivo(arquivo_reservas, reservas)
            print(f"{Cor.VERDE}😙 RESERVA ATUALIZADA COM SUCESSO!{Cor.RESET}")
            return

    print(f"{Cor.VERMELHO}😒 RESERVA NÃO ENCONTRADA.{Cor.RESET}")

def excluir_reserva(nome, data, horario, restaurante):
    reservas = carregar_arquivo(arquivo_reservas)

    reservas = [reserva for reserva in reservas if not (
        reserva['nome'] == nome and
        reserva['data'] == data and
        reserva['horario'] == horario and
        reserva['restaurante'] == restaurante
    )]

    salvar_arquivo(arquivo_reservas, reservas)
    print(f"{Cor.VERDE}😡 RESERVA EXCLUÍDA COM SUCESSO!{Cor.RESET}")

def buscar_reserva(nome, data, horario, restaurante):
    reservas = carregar_arquivo(arquivo_reservas)

    encontrado = False

    for reserva in reservas:
        if (reserva['nome'] == nome and
            reserva['data'] == data and
            reserva['horario'] == horario and
            reserva['restaurante'] == restaurante):
            print(f"NOME: {reserva['nome']}, DATA: {reserva['data']}, HORÁRIO: {reserva['horario']}, RESTAURANTE: {reserva['restaurante']}")
            encontrado = True

    if not encontrado:
        print(f"{Cor.VERMELHO}😒 NENHUMA RESERVA CADASTRADA.{Cor.RESET}")

def listar_reservas():
    reservas = carregar_arquivo(arquivo_reservas)

    if reservas:
        print("=" * 50)
        print("LISTA DE RESERVAS:")
        print("-" * 50)
        tabela = PrettyTable(['Nome', 'Data', 'Horário', 'Restaurante', 'Email'])
        for reserva in reservas:
            tabela.add_row([reserva['nome'], reserva['data'], reserva['horario'], reserva['restaurante'], reserva['email']])
        print(tabela)
    else:
        print("😒 NENHUMA RESERVA ENCONTRADA.")

def menu_inicial():
    print(Cor.CIANO + "=" * 55 + Cor.RESET)
    print(Cor.VERMELHO + " ---->>> BEM VINDO AO RESERVA JÁ <<<---- ")
    print("          1 - MÓDULO RESERVAS ")
    print("          2 - MÓDULO RESTAURANTES ")
    print("          3 - SAIR ")
    print(Cor.CIANO + "=" * 55 + Cor.RESET)

def exibir_menu():
    print("\nMENU:")
    print("1. ADICIONAR RESERVA")
    print("2. LISTAR RESTAURANTES")
    print("3. ATUALIZAR RESERVA")
    print("4. EXCLUIR RESERVA")
    print("5. LISTAR UMA RESERVA")
    print("6. LISTAR TODAS AS RESERVAS")
    print("7. VOLTAR AO MENU ANTERIOR")

def enviar_lembrete():
    reservas = carregar_arquivo(arquivo_reservas)

    agora = datetime.now()
    para_lembrete = agora + timedelta(days=1)

    for reserva in reservas:
        data_reserva = datetime.strptime(reserva['data'], "%d/%m/%Y")
        if data_reserva.date() == para_lembrete.date():
            assunto = "Lembrete de Reserva"
            corpo = f"Olá {reserva['nome']},\n\nLembramos que você tem uma reserva para amanhã, dia {reserva['data']} às {reserva['horario']} no restaurante {reserva['restaurante']}.\n\nObrigado!"
            enviar_email(reserva['email'], assunto, corpo)

def obter_input(validacao_func, mensagem, mensagem_erro):
    while True:
        valor = input(mensagem)
        if validacao_func(valor):
            return valor
        else:
            print(f"{Cor.VERMELHO}{mensagem_erro}{Cor.RESET}")

def main():
    parser = argparse.ArgumentParser(description='Sistema de Gerenciamento de Reservas de Restaurantes')
    parser.parse_args()

    schedule.every().day.at("08:00").do(enviar_lembrete)

    while True:
        schedule.run_pending()
        menu_inicial()
        try:
            opcao_inicial = int(input("INFORME UMA OPÇÃO: "))
        except ValueError:
            print(f"{Cor.VERMELHO}😡 OPÇÃO INVÁLIDA. TENTE NOVAMENTE!{Cor.RESET}")
            continue

        if opcao_inicial == 1:
            while True:
                exibir_menu()
                opcao = input("ESCOLHA UMA OPÇÃO:\n>>>")

                if opcao == "1":
                    nome = input(" DIGITE O SEU NOME COMPLETO:\n>>>")
                    data = obter_input(validar_data, " DIGITE A DATA (DD/MM/AAAA):\n>>>", "Data inválida! Use o formato DD/MM/AAAA.")
                    horario = obter_input(validar_horario, " DIGITE O HORÁRIO (HH:MM):\n>>>", "Horário inválido! Use o formato HH:MM.")
                    restaurante = input("DIGITE O RESTAURANTE ESCOLHIDO:\n>>>")
                    email = obter_input(validar_email, "DIGITE SEU EMAIL:\n>>>", "Email inválido!")
                    adicionar_reserva(nome, data, horario, restaurante, email)
                elif opcao == "2":
                    listar_restaurantes()
                elif opcao == "3":
                    nome_antigo = input("DIGITE O NOME A SER ATUALIZADO:\n>>>")
                    novo_nome = input("DIGITE O NOVO NOME:\n>>>")
                    nova_data = obter_input(validar_data, "DIGITE A NOVA DATA (DD/MM/AAAA):\n>>>", "Data inválida! Use o formato DD/MM/AAAA.")
                    novo_horario = obter_input(validar_horario, "DIGITE O NOVO HORÁRIO (HH:MM):\n>>>", "Horário inválido! Use o formato HH:MM.")
                    novo_restaurante = input("DIGITE O NOVO RESTAURANTE:\n>>>")
                    novo_email = obter_input(validar_email, "DIGITE O NOVO EMAIL:\n>>>", "Email inválido!")
                    atualizar_reserva(nome_antigo, novo_nome, nova_data, novo_horario, novo_restaurante, novo_email)
                elif opcao == "4":
                    nome = input("DIGITE O NOME QUE CONSTA NA RESERVA A SER EXCLUÍDA:\n>>>")
                    data = obter_input(validar_data, "DIGITE A DATA QUE CONSTA NA RESERVA A SER EXCLUÍDA (DD/MM/AAAA):\n>>>", "Data inválida! Use o formato DD/MM/AAAA.")
                    horario = obter_input(validar_horario, "DIGITE O HORARIO QUE CONSTA NA RESERVA A SER EXCLUÍDA (HH:MM):\n>>>", "Horário inválido! Use o formato HH:MM.")
                    restaurante = input("DIGITE O NOME DO RESTAURANTE QUE CONSTA NA RESERVA A SER EXCLUÍDA:\n>>>")
                    excluir_reserva(nome, data, horario, restaurante)
                elif opcao == "5":
                    nome = input("DIGITE O NOME QUE CONSTA NA RESERVA:\n>>>")
                    data = obter_input(validar_data, "DIGITE A DATA QUE CONSTA NA RESERVA (DD/MM/AAAA):\n>>>", "Data inválida! Use o formato DD/MM/AAAA.")
                    horario = obter_input(validar_horario, "DIGITE O HORARIO QUE CONSTA NA RESERVA (HH:MM):\n>>>", "Horário inválido! Use o formato HH:MM.")
                    restaurante = input("DIGITE O RESTAURANTE QUE CONSTA NA RESERVA:\n>>>")
                    buscar_reserva(nome, data, horario, restaurante)
                elif opcao == '6':
                    listar_reservas()
                elif opcao == "7":
                    print("VOLTAR AO MENU ANTERIOR...")
                    sleep(3)
                    break
                else:
                    print(f"{Cor.VERMELHO}😡 OPÇÃO INVÁLIDA. TENTE NOVAMENTE!{Cor.RESET}")
        elif opcao_inicial == 2:
            listar_restaurantes()
        elif opcao_inicial == 3:
            print("🚀 SAINDO...")
            sleep(3)
            break
        else:
            print(f"{Cor.VERMELHO}😡 OPÇÃO INVÁLIDA. TENTE NOVAMENTE!{Cor.RESET}")

if __name__ == "__main__":
    main()