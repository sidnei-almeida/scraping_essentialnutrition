#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Web Scraping Essential Nutrition
==================================
Sistema automatizado para coleta de dados nutricionais do site Essential Nutrition

FUNCIONALIDADES:
1. Coleta URLs de produtos de 15 categorias diferentes
2. Extrai dados nutricionais detalhados
3. Salva dados em formatos JSON e CSV
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
from config.url_collector import coletar_urls
from config.scraper import coletar_dados_nutricionais
from config.teste_coleta import executar_teste

# ============================================================================
# 🎨 SISTEMA DE CORES ANSI PARA TERMINAL
# ============================================================================
class Cores:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    VERDE = '\033[92m'
    AZUL = '\033[94m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    CIANO = '\033[96m'
    MAGENTA = '\033[95m'
    BRANCO = '\033[97m'

def limpar_terminal():
    """Limpa o terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    """Pausa a execução até o usuário pressionar Enter"""
    input(f"\n{Cores.AMARELO}Pressione Enter para continuar...{Cores.RESET}")

def mostrar_barra_progresso(mensagem: str, duracao: float):
    """Exibe uma barra de progresso simples"""
    print(f"\n{mensagem}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    time.sleep(duracao)

def mostrar_banner():
    """Exibe o banner principal do programa"""
    banner = f"""
{Cores.CIANO}{Cores.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                🚀 Web Scraping Essential Nutrition            ║
║                                                              ║
║          Coleta de Dados Nutricionais Automatizada           ║
║                                                              ║
║  📊 Coleta URLs de 15 categorias diferentes                  ║
║  🎯 Extrai dados nutricionais detalhados                     ║
║  📝 Salva em formatos JSON e CSV                            ║
╚══════════════════════════════════════════════════════════════╝
{Cores.RESET}"""
    print(banner)

def mostrar_menu():
    """Exibe o menu principal"""
    menu = f"""
{Cores.AZUL}{Cores.BOLD}═══════════════════ MENU PRINCIPAL ═══════════════════{Cores.RESET}

{Cores.VERDE}🚀 OPERAÇÕES PRINCIPAIS:{Cores.RESET}
  {Cores.AMARELO}1.{Cores.RESET} 🔍 {Cores.BRANCO}Coletar URLs{Cores.RESET} - Busca URLs dos produtos
  {Cores.AMARELO}2.{Cores.RESET} 📊 {Cores.BRANCO}Coletar Dados{Cores.RESET} - Extrai dados nutricionais
  {Cores.AMARELO}3.{Cores.RESET} 🎯 {Cores.BRANCO}Coleta Completa{Cores.RESET} - URLs + Dados nutricionais
  {Cores.AMARELO}4.{Cores.RESET} 🧪 {Cores.BRANCO}Teste Rápido{Cores.RESET} - Testa com 3 produtos

{Cores.VERDE}📁 GERENCIAR DADOS:{Cores.RESET}
  {Cores.AMARELO}5.{Cores.RESET} 📋 {Cores.BRANCO}Ver Arquivos{Cores.RESET} - Lista arquivos gerados
  {Cores.AMARELO}6.{Cores.RESET} 🗑️  {Cores.BRANCO}Limpar Dados{Cores.RESET} - Remove arquivos antigos

{Cores.VERDE}ℹ️  INFORMAÇÕES:{Cores.RESET}
  {Cores.AMARELO}7.{Cores.RESET} 📖 {Cores.BRANCO}Sobre{Cores.RESET} - Informações do programa
  {Cores.AMARELO}8.{Cores.RESET} ❌ {Cores.BRANCO}Sair{Cores.RESET} - Encerrar programa

{Cores.AZUL}══════════════════════════════════════════════════════{Cores.RESET}
"""
    print(menu)

def obter_escolha() -> str:
    """Obtém e valida a escolha do usuário"""
    while True:
        try:
            escolha = input(f"\n{Cores.VERDE}Escolha uma opção (1-8):{Cores.RESET} ").strip()
            if escolha in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return escolha
            print(f"{Cores.VERMELHO}❌ Opção inválida. Digite um número entre 1 e 8.{Cores.RESET}")
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)

def coletar_urls_produtos():
    """Coleta URLs dos produtos"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}🔍 COLETANDO URLs DOS PRODUTOS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    try:
        mostrar_barra_progresso("Iniciando coleta de URLs", 1.0)
        dados_urls = coletar_urls()
        if dados_urls:
            print(f"{Cores.VERDE}✅ URLs coletadas com sucesso!{Cores.RESET}")
            return dados_urls
        else:
            print(f"\n{Cores.VERMELHO}❌ Erro ao coletar URLs dos produtos{Cores.RESET}")
            return None
    except Exception as e:
        print(f"\n{Cores.VERMELHO}❌ Erro durante coleta de URLs: {e}{Cores.RESET}")
        return None

def coletar_dados_nutricionais_produtos():
    """Coleta dados nutricionais dos produtos"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}📊 COLETANDO DADOS NUTRICIONAIS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    if not os.path.exists('dados/urls_produtos.json'):
        print(f"{Cores.VERMELHO}❌ Arquivo de URLs não encontrado. Execute a coleta de URLs primeiro.{Cores.RESET}")
        return None
    
    try:
        mostrar_barra_progresso("Iniciando coleta de dados nutricionais", 1.0)
        df_dados = coletar_dados_nutricionais()
        if df_dados is not None:
            print(f"{Cores.VERDE}✅ Dados nutricionais coletados com sucesso!{Cores.RESET}")
            return df_dados
        else:
            print(f"\n{Cores.VERMELHO}❌ Erro ao coletar dados nutricionais{Cores.RESET}")
            return None
    except Exception as e:
        print(f"\n{Cores.VERMELHO}❌ Erro durante coleta de dados: {e}{Cores.RESET}")
        return None

def listar_arquivos():
    """Lista os arquivos gerados"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}📋 ARQUIVOS GERADOS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    # Criar diretórios se não existirem
    os.makedirs('dados/csv', exist_ok=True)
    
    # Listar arquivos JSON
    print(f"\n{Cores.VERDE}📁 Arquivos JSON:{Cores.RESET}")
    json_files = [f for f in os.listdir('dados') if f.endswith('.json')]
    for file in json_files:
        tamanho = os.path.getsize(os.path.join('dados', file)) / 1024  # KB
        data_mod = datetime.fromtimestamp(os.path.getmtime(os.path.join('dados', file)))
        print(f"  • {file} ({tamanho:.1f} KB) - {data_mod.strftime('%d/%m/%Y %H:%M')}")
    
    # Listar arquivos CSV
    print(f"\n{Cores.VERDE}📁 Arquivos CSV:{Cores.RESET}")
    csv_files = [f for f in os.listdir('dados/csv') if f.endswith('.csv')]
    for file in csv_files:
        tamanho = os.path.getsize(os.path.join('dados/csv', file)) / 1024  # KB
        data_mod = datetime.fromtimestamp(os.path.getmtime(os.path.join('dados/csv', file)))
        print(f"  • {file} ({tamanho:.1f} KB) - {data_mod.strftime('%d/%m/%Y %H:%M')}")

def limpar_dados():
    """Remove arquivos de dados antigos"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}🗑️ LIMPANDO DADOS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    try:
        # Remover arquivos JSON
        for file in os.listdir('dados'):
            if file.endswith('.json'):
                os.remove(os.path.join('dados', file))
                print(f"{Cores.VERDE}✅ Removido: {file}{Cores.RESET}")
        
        # Remover arquivos CSV
        for file in os.listdir('dados/csv'):
            if file.endswith('.csv'):
                os.remove(os.path.join('dados/csv', file))
                print(f"{Cores.VERDE}✅ Removido: {file}{Cores.RESET}")
        
        print(f"\n{Cores.VERDE}✅ Todos os arquivos foram removidos com sucesso!{Cores.RESET}")
    except Exception as e:
        print(f"\n{Cores.VERMELHO}❌ Erro ao limpar dados: {e}{Cores.RESET}")

def mostrar_sobre():
    """Exibe informações sobre o programa"""
    sobre = f"""
{Cores.CIANO}{Cores.BOLD}📖 SOBRE O PROGRAMA{Cores.RESET}
{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}

{Cores.VERDE}🎯 Objetivo:{Cores.RESET}
Este programa realiza web scraping automatizado do site Essential Nutrition
para coletar dados nutricionais de todos os produtos disponíveis.

{Cores.VERDE}📊 Funcionalidades:{Cores.RESET}
• Coleta URLs de produtos de 15 categorias diferentes
• Extrai dados nutricionais detalhados de cada produto
• Salva os dados em formatos JSON e CSV para análise
• Detecta e trata URLs duplicadas entre categorias
• Interface amigável com menus coloridos
• Sistema de teste para validação rápida

{Cores.VERDE}🔧 Tecnologias:{Cores.RESET}
• Python 3.8+
• Selenium WebDriver
• Chrome Driver
• Pandas
• Beautiful Soup 4

{Cores.VERDE}📝 Dados Coletados:{Cores.RESET}
• Nome do produto
• Categoria
• Porção
• Calorias
• Carboidratos
• Proteínas
• Gorduras totais
• Gorduras saturadas
• Fibras
• Açúcares
• Sódio

{Cores.VERDE}👨‍💻 Desenvolvido por:{Cores.RESET}
Sidnei Almeida
https://github.com/sidnei-junior
"""
    print(sobre)

# ============================================================================
# 🚀 FUNÇÃO PRINCIPAL
# ============================================================================
def main():
    """Função principal do programa"""
    try:
        while True:
            limpar_terminal()
            mostrar_banner()
            mostrar_menu()
            
            escolha = obter_escolha()
            
            if escolha == "1":
                coletar_urls_produtos()
                pausar()
                
            elif escolha == "2":
                coletar_dados_nutricionais_produtos()
                pausar()
                
            elif escolha == "3":
                print(f"\n{Cores.CIANO}{Cores.BOLD}🎯 EXECUTANDO COLETA COMPLETA{Cores.RESET}")
                print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
                
                # Primeira etapa: Coletar URLs
                print(f"\n{Cores.VERDE}📍 ETAPA 1: Coletando URLs dos produtos...{Cores.RESET}")
                dados_urls = coletar_urls_produtos()
                
                if dados_urls:
                    # Segunda etapa: Coletar dados nutricionais
                    print(f"\n{Cores.VERDE}📍 ETAPA 2: Coletando dados nutricionais...{Cores.RESET}")
                    df_dados = coletar_dados_nutricionais_produtos()
                    
                    if df_dados is not None:
                        print(f"\n{Cores.VERDE}✅ Coleta completa finalizada com sucesso!{Cores.RESET}")
                    else:
                        print(f"\n{Cores.VERMELHO}❌ Erro ao coletar dados nutricionais{Cores.RESET}")
                else:
                    print(f"\n{Cores.VERMELHO}❌ Erro ao coletar URLs dos produtos{Cores.RESET}")
                
                pausar()
                
            elif escolha == "4":
                print(f"\n{Cores.CIANO}{Cores.BOLD}🧪 EXECUTANDO TESTE RÁPIDO{Cores.RESET}")
                print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
                executar_teste()
                pausar()
                
            elif escolha == "5":
                listar_arquivos()
                pausar()
                
            elif escolha == "6":
                limpar_dados()
                pausar()
                
            elif escolha == "7":
                mostrar_sobre()
                pausar()
                
            elif escolha == "8":
                print(f"\n{Cores.VERDE}✅ Programa finalizado. Até logo!{Cores.RESET}\n")
                break
    
    except KeyboardInterrupt:
        print(f"\n\n{Cores.AMARELO}⚠️  Programa interrompido pelo usuário.{Cores.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Cores.VERMELHO}❌ Erro inesperado: {e}{Cores.RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    # Criar diretórios necessários
    os.makedirs('dados/csv', exist_ok=True)
    main() 