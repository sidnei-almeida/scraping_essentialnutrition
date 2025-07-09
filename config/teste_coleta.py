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

# Selecionando apenas 2 categorias para teste
CATEGORIAS_TESTE = {
    'PROTEINAS': 'https://www.essentialnutrition.com.br/produtos/proteinas',
    'AMINOACIDOS': 'https://www.essentialnutrition.com.br/produtos/aminoacidos'
}

def configurar_driver():
    """Configura e retorna o driver do Selenium"""
    chrome_options = Options()
    # Removendo a opção headless para mostrar o navegador
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
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

def coletar_urls_para_teste(driver, url_categoria, max_urls=3):
    """Coleta um número limitado de URLs de produtos de uma categoria"""
    print(f"\nAcessando categoria: {url_categoria}")
    driver.get(url_categoria)
    time.sleep(3)  # Aguarda carregamento inicial
    ajustar_zoom(driver)  # Ajusta o zoom
    urls_coletadas = set()
    
    try:
        # Aguardar carregamento dos produtos
        produtos = esperar_elemento(driver, "div.products.wrapper.grid.products-grid")
        if not produtos:
            print("Não foi possível encontrar a lista de produtos")
            return list(urls_coletadas)
            
        # Coletar links
        links = driver.find_elements(By.CSS_SELECTOR, "a.product-item-link")
        
        for link in links:
            if len(urls_coletadas) >= max_urls:
                break
                
            try:
                url = link.get_attribute('href')
                if url and 'essentialnutrition.com.br' in url:
                    # Normalizar URL
                    parsed_url = urlparse(url)
                    url_normalizada = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                    urls_coletadas.add(url_normalizada)
                    print(f"URL coletada: {url_normalizada}")
            except Exception as e:
                print(f"Erro ao processar link: {e}")
                continue
    
    except Exception as e:
        print(f"Erro ao coletar URLs de teste: {e}")
    
    return list(urls_coletadas)

def extrair_valor_nutricional(texto):
    """Extrai o valor numérico de um texto nutricional"""
    try:
        # Remove caracteres não numéricos, exceto vírgula e ponto
        valor = ''.join(c for c in texto if c.isdigit() or c in ',.').replace(',', '.')
        return float(valor) if valor else 0.0
    except ValueError:
        return 0.0

def extrair_dados_nutricionais(driver, url, categoria):
    """Extrai dados nutricionais de um produto"""
    print(f"\nProcessando produto: {url}")
    
    dados = {
        'nome': '',
        'categoria': categoria,
        'url': url,
        'porcao': '',
        'calorias': 0.0,
        'carboidratos': 0.0,
        'proteinas': 0.0,
        'gorduras_totais': 0.0,
        'gorduras_saturadas': 0.0,
        'fibras': 0.0,
        'acucares': 0.0,
        'sodio': 0.0
    }
    
    try:
        driver.get(url)
        time.sleep(3)  # Aguarda carregamento inicial
        ajustar_zoom(driver)  # Ajusta o zoom
        
        # Extrair nome do produto
        nome_element = esperar_elemento(driver, "h1.page-title span")
        if nome_element:
            dados['nome'] = nome_element.text.strip()
            print(f"Nome do produto: {dados['nome']}")
        
        # Clicar no botão de Informação Nutricional
        try:
            # Tenta primeiro seletor
            botao_info = esperar_elemento(driver, "a[href='#information']")
            if not botao_info:
                # Tenta seletores alternativos
                seletores_alternativos = [
                    "a.data.switch[href='#information']",
                    "div.data.item.title a[href='#information']",
                    "a:contains('Informação Nutricional')",
                    "a.switch[data-toggle='switch']"
                ]
                for seletor in seletores_alternativos:
                    botao_info = esperar_elemento(driver, seletor, timeout=5)
                    if botao_info:
                        break

            if botao_info:
                print("Botão de Informação Nutricional encontrado, tentando clicar...")
                # Tenta clicar de várias formas
                try:
                    botao_info.click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", botao_info)
                    except:
                        driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}))", botao_info)
                
                # Aumenta o tempo de espera após o clique
                time.sleep(4)  # Aumentado para 4 segundos
                print("Clique realizado com sucesso")
            else:
                print("Botão de Informação Nutricional não encontrado após tentar todos os seletores")
                
        except Exception as e:
            print(f"Erro ao clicar no botão de informação nutricional: {e}")
            print("Tentando scroll até o elemento...")
            try:
                # Tenta rolar até a seção de informação nutricional
                driver.execute_script("document.querySelector('#information').scrollIntoView(true);")
                time.sleep(2)
            except Exception as scroll_error:
                print(f"Erro ao tentar scroll: {scroll_error}")
        
        # Encontrar a tabela nutricional
        tabela = esperar_elemento(driver, "div.tabela-nutri table.table")
        if not tabela:
            print("Tabela nutricional não encontrada")
            return dados
        
        # Extrair porção do cabeçalho da tabela
        try:
            porcao_header = tabela.find_element(By.CSS_SELECTOR, "thead tr th:first-child")
            if porcao_header:
                dados['porcao'] = porcao_header.text.strip()
                print(f"Porção: {dados['porcao']}")
        except:
            print("Não foi possível extrair a porção do cabeçalho")
        
        # Mapear nutrientes
        mapeamento = {
            'valor energético': 'calorias',
            'carboidratos': 'carboidratos',
            'proteínas': 'proteinas',
            'gorduras totais': 'gorduras_totais',
            'gorduras saturadas': 'gorduras_saturadas',
            'fibras alimentares': 'fibras',
            'açúcares totais': 'acucares',
            'sódio': 'sodio'
        }
        
        # Extrair valores nutricionais
        linhas = tabela.find_elements(By.CSS_SELECTOR, "tbody tr")
        for linha in linhas:
            try:
                colunas = linha.find_elements(By.TAG_NAME, "td")
                if len(colunas) >= 2:
                    nutriente = colunas[0].text.strip().lower()
                    for chave, campo in mapeamento.items():
                        if chave in nutriente:
                            valor = colunas[1].text.strip()
                            dados[campo] = extrair_valor_nutricional(valor)
                            print(f"{chave.title()}: {dados[campo]}")
                            break
            except Exception as e:
                print(f"Erro ao processar linha da tabela: {e}")
                continue
    
    except Exception as e:
        print(f"Erro ao processar produto: {e}")
    
    return dados

def iniciar_coleta_teste():
    """Inicia o processo de coleta de URLs de teste"""
    try:
        # Configurar o driver
        driver = configurar_driver()
        
        # Lista para armazenar as URLs coletadas
        todas_urls = []
        
        # Coletar URLs de cada categoria de teste
        for categoria, url in CATEGORIAS_TESTE.items():
            print(f"\nColetando URLs da categoria {categoria}")
            urls_categoria = coletar_urls_para_teste(driver, url, max_urls=2)
            todas_urls.extend(urls_categoria)
            
            # Se já temos 3 URLs, podemos parar
            if len(todas_urls) >= 3:
                todas_urls = todas_urls[:3]  # Garantir apenas 3 URLs
                break
        
        # Criar diretório de dados se não existir
        os.makedirs('dados', exist_ok=True)
        
        # Salvar URLs em arquivo JSON
        with open('dados/urls_produtos_teste.json', 'w', encoding='utf-8') as f:
            json.dump(todas_urls, f, ensure_ascii=False, indent=4)
            
        print(f"\n✅ URLs coletadas e salvas: {len(todas_urls)}")
        for url in todas_urls:
            print(f"  • {url}")
            
        driver.quit()
        return todas_urls
        
    except Exception as e:
        print(f"❌ Erro ao coletar URLs de teste: {e}")
        if 'driver' in locals():
            driver.quit()
        return []

def extrair_dados_nutricionais_teste(driver, url):
    """Extrai os dados nutricionais de um produto de teste"""
    try:
        driver.get(url)
        time.sleep(2)
        
        # Extrair nome do produto
        nome = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text.strip()
        
        # Tentar clicar no botão "Informação Nutricional" se existir
        try:
            botao = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-title='Informação Nutricional']"))
            )
            botao.click()
            time.sleep(1)
        except:
            pass
        
        # Extrair dados da tabela nutricional
        dados = {
            'nome': nome,
            'categoria': 'TESTE',
            'url': url,
            'porcao': None,
            'calorias': None,
            'carboidratos': None,
            'proteinas': None,
            'gorduras_totais': None,
            'fibras': None,
            'acucares': None,
            'sodio': None
        }
        
        try:
            tabela = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.nutricional-table"))
            )
            
            # Extrair porção
            try:
                porcao = driver.find_element(By.CSS_SELECTOR, "td.portion").text.strip()
                dados['porcao'] = porcao
            except:
                pass
            
            # Extrair valores nutricionais
            linhas = tabela.find_elements(By.CSS_SELECTOR, "tr")
            for linha in linhas:
                try:
                    info = linha.find_element(By.CSS_SELECTOR, "td.name").text.strip().lower()
                    valor = linha.find_element(By.CSS_SELECTOR, "td.value").text.strip()
                    
                    if 'valor energético' in info or 'calorias' in info:
                        dados['calorias'] = valor
                    elif 'carboidratos' in info:
                        dados['carboidratos'] = valor
                    elif 'proteínas' in info:
                        dados['proteinas'] = valor
                    elif 'gorduras totais' in info:
                        dados['gorduras_totais'] = valor
                    elif 'fibras' in info:
                        dados['fibras'] = valor
                    elif 'açúcares' in info:
                        dados['acucares'] = valor
                    elif 'sódio' in info:
                        dados['sodio'] = valor
                except:
                    continue
            
        except Exception as e:
            print(f"Aviso: Não foi possível encontrar tabela nutricional para {url}")
            print(f"Erro: {e}")
        
        return dados
    
    except Exception as e:
        print(f"Erro ao processar URL {url}")
        print(f"Erro: {e}")
        return None

def executar_teste():
    """Executa o teste de coleta de dados"""
    try:
        # Coletar URLs de teste
        print("\n1. Coletando URLs de teste...")
        urls_teste = iniciar_coleta_teste()
        
        if not urls_teste:
            print("❌ Não foi possível coletar URLs para teste")
            return
            
        # Configurar driver para coleta de dados
        print("\n2. Iniciando coleta de dados nutricionais...")
        driver = configurar_driver()
        
        # Lista para armazenar os dados coletados
        dados_coletados = []
        
        # Coletar dados de cada URL
        for url in urls_teste:
            dados = extrair_dados_nutricionais_teste(driver, url)
            if dados:
                dados_coletados.append(dados)
        
        # Criar DataFrame e salvar CSV
        if dados_coletados:
            df = pd.DataFrame(dados_coletados)
            
            # Criar diretório para CSV se não existir
            os.makedirs('dados/csv', exist_ok=True)
            
            # Salvar CSV
            caminho_csv = 'dados/csv/dados_nutricionais_teste.csv'
            df.to_csv(caminho_csv, index=False, encoding='utf-8')
            print(f"\n✅ Dados salvos em: {caminho_csv}")
        else:
            print("\n❌ Nenhum dado foi coletado durante o teste")
        
        driver.quit()
        
    except Exception as e:
        print(f"\n❌ Erro durante execução do teste: {e}")
        if 'driver' in locals():
            driver.quit()

def testar_produto_especifico():
    """Testa a coleta em um produto específico"""
    from scraper import configurar_driver, extrair_dados_nutricionais
    
    url_teste = "https://www.essentialnutrition.com.br/cappuccino-whey-protein-box"
    
    print("\n=== Iniciando Teste de Coleta ===")
    print(f"URL: {url_teste}")
    
    try:
        driver = configurar_driver()
        dados = extrair_dados_nutricionais(driver, url_teste, "PROTEINAS")
        
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