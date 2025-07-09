import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from urllib.parse import urlparse
from collections import defaultdict
import os
import re
from .browser import BrowserManager

# Selecionando apenas 2 categorias para teste
CATEGORIAS_TESTE = {
    'PROTEINAS': 'https://www.essentialnutrition.com.br/produtos/proteinas',
    'AMINOACIDOS': 'https://www.essentialnutrition.com.br/produtos/aminoacidos'
}

def iniciar_driver():
    """Configura e inicia o driver do navegador em modo headless"""
    print("Configurando driver do navegador...")
    
    driver, browser_name = BrowserManager.setup_driver(headless=True)
    
    if driver is None:
        print(f"Erro ao configurar driver: {browser_name}")
        return None
        
    print(f"Driver configurado com sucesso usando {browser_name}")
    return driver

def esperar_elemento(driver, seletor, timeout=20):
    """Espera um elemento ficar visível e retorna ele"""
    try:
        wait = WebDriverWait(driver, timeout)
        elemento = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, seletor))
        )
        return elemento
    except TimeoutException:
        print(f"Timeout esperando pelo elemento: {seletor}")
        return None
    except Exception as e:
        print(f"Erro ao esperar elemento {seletor}: {e}")
        return None

def ajustar_zoom(driver, zoom_percent=60):
    """Ajusta o zoom da página"""
    try:
        driver.execute_script(f"document.body.style.zoom = '{zoom_percent}%'")
        time.sleep(2)  # Aumentado para 2 segundos para garantir que o zoom seja aplicado
        print(f"Zoom ajustado para {zoom_percent}%")
    except Exception as e:
        print(f"Erro ao ajustar zoom: {e}")
        # Tenta método alternativo de zoom
        try:
            driver.execute_script(f"document.documentElement.style.zoom = '{zoom_percent}%'")
            time.sleep(2)
            print("Zoom ajustado usando método alternativo")
        except Exception as e:
            print(f"Erro ao ajustar zoom (método alternativo): {e}")

def coletar_urls_teste():
    """Coleta URLs de produtos das categorias de teste"""
    driver = None
    try:
        # Configurar o driver
        driver = iniciar_driver()
        if not driver:
            return None
        
        # Lista para armazenar as URLs coletadas
        urls_coletadas = []
        
        # Processar cada categoria
        for categoria, url in CATEGORIAS_TESTE.items():
            print(f"\nColetando URLs da categoria: {categoria}")
            
            # Acessar a página da categoria
            driver.get(url)
            time.sleep(2)
            
            # Encontrar todos os links de produtos
            links = driver.find_elements(By.CSS_SELECTOR, 'a.product-item-link')
            urls = [link.get_attribute('href') for link in links]
            
            print(f"Encontrados {len(urls)} produtos")
            urls_coletadas.extend(urls)
        
        return list(set(urls_coletadas))  # Remover duplicatas
        
    except Exception as e:
        print(f"Erro durante coleta de URLs: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def coletar_dados_nutricionais_teste(urls):
    """Coleta dados nutricionais dos produtos de teste"""
    driver = None
    try:
        # Configurar driver para coleta de dados
        print("\n2. Iniciando coleta de dados nutricionais...")
        driver = iniciar_driver()
        if not driver:
            return None
        
        # Lista para armazenar os dados coletados
        dados_nutricionais = []
        
        # Processar cada URL
        for url in urls:
            try:
                # Extrair dados do produto
                dados = extrair_dados_nutricionais(driver, url)
                if dados:
                    dados_nutricionais.append(dados)
                time.sleep(1)
            except Exception as e:
                print(f"Erro ao processar URL {url}: {e}")
                continue
        
        # Criar DataFrame
        if dados_nutricionais:
            df = pd.DataFrame(dados_nutricionais)
            
            # Criar diretório se não existir
            os.makedirs('dados/csv', exist_ok=True)
            
            # Salvar em CSV
            caminho_csv = 'dados/csv/dados_nutricionais_teste.csv'
            df.to_csv(caminho_csv, index=False, encoding='utf-8')
            print(f"\nDados salvos em '{caminho_csv}'")
            
            return df
        else:
            print("Nenhum dado nutricional foi coletado!")
            return None
            
    except Exception as e:
        print(f"Erro durante coleta de dados: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def testar_extracao_unica(url_teste="https://www.essentialnutrition.com.br/produtos/proteinas/whey-protein-isolate"):
    """Testa a extração de dados de um único produto"""
    driver = None
    try:
        driver = iniciar_driver()
        if not driver:
            return None
            
        dados = extrair_dados_nutricionais(driver, url_teste)
        if dados:
            print("\nDados extraídos:")
            for chave, valor in dados.items():
                print(f"{chave}: {valor}")
        return dados
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()

def extrair_dados_nutricionais(driver, url):
    """Extrai os dados nutricionais de um produto"""
    print("\nIniciando extração de dados...")
    print(f"URL: {url}")
    
    dados = {
        'nome': '',
        'url': url,
        'porcao': '',
        'calorias': 0.0,
        'carboidratos': 0.0,
        'proteinas': 0.0,
        'gorduras_totais': 0.0,
        'gorduras_saturadas': 0.0,
        'fibras': 0.0,
        'sodio': 0.0
    }
    
    try:
        print("Acessando página...")
        driver.get(url)
        
        print("Aguardando página carregar...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        print("Página carregada!")
        
        # Ajustar zoom
        print("Ajustando zoom...")
        driver.execute_script("document.body.style.zoom='50%'")
        print("Zoom ajustado!")
        
        # Coletar nome do produto
        print("Buscando nome do produto...")
        nome_element = driver.find_element(By.TAG_NAME, "h1")
        dados['nome'] = nome_element.text.strip()
        print(f"Nome do produto encontrado: {dados['nome']}\n")
        
        # Remover modal de cookies se existir
        try:
            botao_cookies = driver.find_element(By.ID, "btn-cookie-allow")
            driver.execute_script("arguments[0].click();", botao_cookies)
            print("Modal de cookies removido")
        except:
            pass
        
        # Clicar no botão de informação nutricional usando JavaScript
        print("Procurando botão de informação nutricional...")
        try:
            botao = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.content-tabela"))
            )
            driver.execute_script("arguments[0].click();", botao)
            print("Botão encontrado e clicado!")
        except:
            print("Botão não encontrado, tentando alternativa...")
            try:
                botao = driver.find_element(By.CSS_SELECTOR, "div.content-tabela")
                driver.execute_script("arguments[0].click();", botao)
                print("Botão encontrado e clicado (alternativa)!")
            except:
                print("Não foi possível encontrar o botão")
                return None
        
        # Aguardar tabela nutricional carregar
        time.sleep(2)
        
        # Extrair porção
        try:
            porcao_element = driver.find_element(By.CSS_SELECTOR, "td.porcao")
            dados['porcao'] = porcao_element.text.strip()
            print(f"Porção encontrada: {dados['porcao']}")
        except:
            print("Porção não encontrada")
        
        # Função auxiliar para extrair valor numérico
        def extrair_valor(texto):
            if not texto:
                return 0.0
            match = re.search(r'(\d+[.,]?\d*)', texto.replace(',', '.'))
            return float(match.group(1)) if match else 0.0
        
        # Extrair dados nutricionais
        elementos_nutricionais = driver.find_elements(By.CSS_SELECTOR, "tr.nutriente")
        for elemento in elementos_nutricionais:
            try:
                nome_nutriente = elemento.find_element(By.CSS_SELECTOR, "td.name").text.strip()
                valor_nutriente = elemento.find_element(By.CSS_SELECTOR, "td.valor").text.strip()
                
                print(f"Encontrado nutriente: '{nome_nutriente}'")
                
                if 'Valor Energético' in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['calorias'] = valor
                    print(f"Coletado Valor Energético: {valor_nutriente} -> {valor}")
                    
                elif 'Carboidratos' in nome_nutriente and 'Fibras' not in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['carboidratos'] = valor
                    print(f"Coletado Carboidratos: {valor_nutriente} -> {valor}")
                    
                elif 'Proteínas' in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['proteinas'] = valor
                    print(f"Coletado Proteínas: {valor_nutriente} -> {valor}")
                    
                elif 'Gorduras totais' in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['gorduras_totais'] = valor
                    print(f"Coletado Gorduras totais: {valor_nutriente} -> {valor}")
                    
                elif 'Gorduras saturadas' in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['gorduras_saturadas'] = valor
                    print(f"Coletado Gorduras saturadas: {valor_nutriente} -> {valor}")
                    
                elif 'Fibras' in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['fibras'] = valor
                    print(f"Coletado Fibras alimentares: {valor_nutriente} -> {valor}")
                    
                elif 'Sódio' in nome_nutriente:
                    valor = extrair_valor(valor_nutriente)
                    dados['sodio'] = valor
                    print(f"Coletado Sódio: {valor_nutriente} -> {valor}")
                    
            except Exception as e:
                print(f"Erro ao processar nutriente: {e}")
                continue
        
        return dados
        
    except Exception as e:
        print(f"Erro durante extração: {e}")
        return None

def executar_teste():
    """Executa o teste completo de coleta"""
    print("\n1. Iniciando coleta de URLs de teste...")
    urls = coletar_urls_teste()
    
    if urls:
        print(f"\nURLs coletadas com sucesso: {len(urls)} produtos")
        df = coletar_dados_nutricionais_teste(urls)
        
        if df is not None:
            print("\nTeste concluído com sucesso!")
            print(f"Total de produtos processados: {len(df)}")
        else:
            print("\nErro durante coleta de dados nutricionais")
    else:
        print("\nErro durante coleta de URLs")

def testar_produto_especifico():
    """Testa a coleta em um produto específico"""
    from scraper import configurar_driver, extrair_dados_nutricionais
    
    url_teste = "https://www.essentialnutrition.com.br/cappuccino-whey-protein-box"
    
    print("\n=== Iniciando Teste de Coleta ===")
    print(f"URL: {url_teste}")
    
    try:
        driver = iniciar_driver()
        dados = extrair_dados_nutricionais(driver, url_teste)
        
        print("\nDados coletados:")
        print("-" * 40)
        for campo, valor in dados.items():
            print(f"{campo}: {valor}")
            
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
    
    print("\n=== Teste Finalizado ===")

if __name__ == "__main__":
    testar_produto_especifico() 