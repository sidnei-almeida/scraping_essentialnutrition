import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import os
from datetime import datetime

# Dicionário com as categorias e suas URLs
CATEGORIAS = {
    'ADOCANTES NATURAIS': 'https://www.essentialnutrition.com.br/produtos/adocantes-naturais',
    'AMINOACIDOS': 'https://www.essentialnutrition.com.br/produtos/aminoacidos',
    'BEBIDAS': 'https://www.essentialnutrition.com.br/produtos/bebidas',
    'CHOCOLATES': 'https://www.essentialnutrition.com.br/produtos/chocolates',
    'COLAGENOS': 'https://www.essentialnutrition.com.br/produtos/colagenos',
    'FIBRAS': 'https://www.essentialnutrition.com.br/produtos/fibras',
    'INFANCIA SAUDAVEL': 'https://www.essentialnutrition.com.br/produtos/infancia-saudavel',
    'LINHA CLINICA': 'https://www.essentialnutrition.com.br/produtos/linha-clinica',
    'OMEGA3': 'https://www.essentialnutrition.com.br/produtos/omega-3',
    'PROTEINAS': 'https://www.essentialnutrition.com.br/produtos/proteinas',
    'SAUDE INTESTINAL': 'https://www.essentialnutrition.com.br/produtos/saude-intestinal',
    'SHAKES': 'https://www.essentialnutrition.com.br/produtos/shakes',
    'SNACKS': 'https://www.essentialnutrition.com.br/produtos/snacks',
    'TREINO': 'https://www.essentialnutrition.com.br/produtos/treino',
    'VITAMINAS': 'https://www.essentialnutrition.com.br/produtos/vitaminas'
}

def configurar_driver():
    """Configura e retorna o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def verificar_pagina_vazia(driver):
    """Verifica se a página atual está vazia (sem produtos)"""
    try:
        mensagem = driver.find_element(By.CSS_SELECTOR, "div.message.info.empty")
        return "Não encontramos produtos correspondentes" in mensagem.text
    except:
        return False

def coletar_urls_pagina(driver):
    """Coleta as URLs dos produtos na página atual"""
    if verificar_pagina_vazia(driver):
        return set()
    
    urls = set()
    wait = WebDriverWait(driver, 10)
    
    try:
        # Aguardar até que pelo menos um produto esteja visível
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.product.photo.product-item-photo")))
        
        # Rolar a página para garantir que todos os produtos sejam carregados
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Aguardar o carregamento dinâmico
        
        # Coletar URLs usando o seletor específico
        links = driver.find_elements(By.CSS_SELECTOR, "a.product.photo.product-item-photo")
        
        for link in links:
            url = link.get_attribute('href')
            if url and 'essentialnutrition.com.br' in url and '/produtos/' not in url:
                # Normalizar a URL removendo parâmetros de query e fragmentos
                parsed_url = urlparse(url)
                url_normalizada = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                urls.add(url_normalizada)
    except Exception as e:
        print(f"Erro ao coletar URLs da página: {e}")
    
    return urls

def coletar_urls_produtos(driver, url_categoria):
    """Coleta todas as URLs dos produtos de uma categoria"""
    driver.get(url_categoria)
    urls_produtos = set()  # Usando set para evitar duplicatas
    pagina = 1
    
    while True:
        print(f"Processando página {pagina}")
        
        if pagina > 1:
            # Construir URL da página
            url_paginada = f"{url_categoria}?p={pagina}"
            driver.get(url_paginada)
        
        # Verificar se a página está vazia
        if verificar_pagina_vazia(driver):
            print(f"Página {pagina} está vazia. Finalizando coleta desta categoria.")
            break
        
        # Coletar URLs da página atual
        urls_pagina = coletar_urls_pagina(driver)
        
        # Se não encontrou produtos e a página não está explicitamente vazia,
        # pode ser um erro de carregamento
        if not urls_pagina and not verificar_pagina_vazia(driver):
            print(f"Aviso: Nenhum produto encontrado na página {pagina}, mas a página não está marcada como vazia")
            # Tentar mais uma vez após uma pausa
            time.sleep(3)
            urls_pagina = coletar_urls_pagina(driver)
            if not urls_pagina:
                print("Ainda não encontrou produtos. Finalizando coleta desta categoria.")
                break
        
        urls_produtos.update(urls_pagina)
        print(f"Encontrados {len(urls_pagina)} produtos na página {pagina}")
        
        pagina += 1
        time.sleep(1)  # Pequena pausa entre páginas
    
    return list(urls_produtos)

def analisar_duplicatas(resultados):
    """Analisa e retorna estatísticas sobre URLs duplicadas entre categorias"""
    # Mapear cada URL para suas categorias
    url_categorias = defaultdict(list)
    for categoria, dados in resultados.items():
        for url in dados['produtos']:
            url_categorias[url].append(categoria)
    
    # Identificar URLs duplicadas
    duplicatas = {url: cats for url, cats in url_categorias.items() if len(cats) > 1}
    
    return {
        'total_urls_unicas': len(url_categorias),
        'total_urls_duplicadas': len(duplicatas),
        'urls_duplicadas': duplicatas
    }

def coletar_urls():
    """Coleta URLs de todos os produtos do site"""
    driver = configurar_driver()
    if not driver:
        return None

    todas_urls = []  # Lista simples para armazenar todas as URLs
    total_categorias = len(CATEGORIAS)
    
    try:
        print(f"\nIniciando coleta de URLs de {total_categorias} categorias...")
        
        # Barra de progresso para as categorias
        for categoria, url_categoria in tqdm(CATEGORIAS.items(), desc="Processando categorias"):
            print(f"\nColetando URLs da categoria: {categoria}")
            
            # Acessar a página da categoria
            driver.get(url_categoria)
            time.sleep(2)  # Aguardar carregamento
            
            pagina = 1
            while True:
                print(f"Processando página {pagina}")
                
                # Encontrar todos os links de produtos na página atual
                links_produtos = driver.find_elements(By.CSS_SELECTOR, 'a.product-item-link')
                
                if not links_produtos:
                    print(f"Página {pagina} está vazia. Finalizando coleta desta categoria.")
                    break
                
                # Coletar URLs
                urls_pagina = [link.get_attribute('href') for link in links_produtos]
                todas_urls.extend(urls_pagina)  # Adicionar à lista principal
                
                print(f"Encontrados {len(urls_pagina)} produtos na página {pagina}")
                
                # Tentar ir para a próxima página
                try:
                    pagina += 1
                    url_proxima = f"{url_categoria}?p={pagina}"
                    driver.get(url_proxima)
                    time.sleep(2)  # Aguardar carregamento
                except Exception as e:
                    print(f"Erro ao acessar página {pagina}: {e}")
                    break
        
        # Remover duplicatas
        todas_urls = list(set(todas_urls))
        print(f"\nTotal de URLs únicas coletadas: {len(todas_urls)}")
        
        # Salvar URLs em formato JSON
        os.makedirs('dados', exist_ok=True)
        with open('dados/urls_produtos.json', 'w', encoding='utf-8') as f:
            json.dump({
                'urls': todas_urls,
                'total': len(todas_urls),
                'data_coleta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
        
        return todas_urls
        
    except Exception as e:
        print(f"Erro durante a coleta de URLs: {e}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    coletar_urls() 