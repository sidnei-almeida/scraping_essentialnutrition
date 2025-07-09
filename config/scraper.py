import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from tqdm import tqdm
import re
import os

def iniciar_driver():
    """Inicializa e retorna uma instância do driver do Chrome"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Novo modo headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--window-size=1920,1080')  # Resolução específica
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def converter_numero_br(texto):
    """Converte número no formato brasileiro (vírgula como decimal) para float"""
    if not texto or texto.strip() == '-':
        return 0.0
    
    # Remove possíveis caracteres não numéricos, exceto vírgula e ponto
    numero = re.sub(r'[^\d,.]', '', texto)
    
    # Substitui vírgula por ponto
    numero = numero.replace(',', '.')
    
    try:
        return float(numero)
    except ValueError:
        return 0.0

def extrair_dados_nutricionais(driver, url):
    """Extrai os dados nutricionais de um produto"""
    print("\nIniciando extração de dados...")
    print(f"URL: {url}")
    
    dados = {
        'nome': '',
        'categoria': '', # Adicionado para compatibilidade com a nova estrutura
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
        print("Acessando página...")
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        
        # Esperar a página carregar completamente
        print("Aguardando página carregar...")
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(5)  # Espera adicional para garantir
        print("Página carregada!")
        
        # Verificar e fechar popup de cookies se existir
        try:
            popup = driver.find_element(By.CLASS_NAME, "cookie-notice")
            if popup.is_displayed():
                print("Fechando popup de cookies...")
                fechar_btn = popup.find_element(By.CLASS_NAME, "cookie-notice__accept")
                fechar_btn.click()
        except:
            pass
        
        # Ajustar zoom para 50%
        print("Ajustando zoom...")
        driver.execute_script("document.body.style.zoom = '50%'")
        time.sleep(2)
        print("Zoom ajustado!")
        
        # Extrair nome do produto
        print("Buscando nome do produto...")
        nome_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        dados['nome'] = nome_element.text.strip()
        print(f"Nome do produto encontrado: {dados['nome']}")
        
        # Clicar no botão de Informação Nutricional
        print("\nProcurando botão de Informação Nutricional...")
        try:
            # Primeiro verificar se o menu existe
            menu = wait.until(EC.presence_of_element_located((By.ID, "menu-top-int")))
            print("Menu encontrado!")
            
            # Remover modal que pode estar interceptando o clique
            print("Verificando e removendo possíveis modais...")
            try:
                driver.execute_script("""
                    var modals = document.getElementsByClassName('modalchuvas');
                    for(var i = 0; i < modals.length; i++) {
                        modals[i].remove();
                    }
                """)
                print("Modais removidos!")
            except:
                print("Nenhum modal encontrado")
            
            # Agora procurar o botão dentro do menu
            botao_info = menu.find_element(By.XPATH, ".//a[text()='Informação Nutricional']")
            print("Botão encontrado!")
            
            # Rolar até o botão
            print("Rolando até o botão...")
            driver.execute_script("arguments[0].scrollIntoView(true);", botao_info)
            time.sleep(2)
            
            # Tentar clicar
            print("Tentando clicar...")
            driver.execute_script("arguments[0].click();", botao_info)  # Usando JavaScript click
            print("Clique realizado! Aguardando tabela carregar...")
            time.sleep(3)
            
        except Exception as e:
            print(f"Erro ao interagir com botão: {str(e)}")
            return dados
        
        # Encontrar a tabela nutricional
        try:
            tabela = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tabela-nutri table.table")))
            
            # Extrair porção do cabeçalho
            porcao_header = tabela.find_element(By.CSS_SELECTOR, "thead tr th:first-child")
            if porcao_header:
                dados['porcao'] = porcao_header.text.strip()
            
            # Mapear os nutrientes para seus respectivos campos
            mapeamento = {
                'Valor energético (kcal)': 'calorias',
                'Carboidratos (g)': 'carboidratos',
                'Proteínas (g)': 'proteinas',
                'Gorduras totais (g)': 'gorduras_totais',
                'Gorduras saturadas (g)': 'gorduras_saturadas',
                'Fibras alimentares (g)': 'fibras',
                'Açúcares totais (g)': 'acucares',
                'Sódio (mg)': 'sodio'
            }
            
            # Extrair valores nutricionais
            linhas = tabela.find_elements(By.CSS_SELECTOR, "tbody tr")
            for linha in linhas:
                colunas = linha.find_elements(By.TAG_NAME, "td")
                if len(colunas) >= 2:
                    nutriente = colunas[0].text.strip()
                    print(f"Encontrado nutriente: '{nutriente}'")  # Debug
                    for chave, campo in mapeamento.items():
                        if chave == nutriente:  # Comparação exata
                            valor = colunas[1].text.strip()  # Pegando sempre a segunda coluna (valor)
                            dados[campo] = converter_numero_br(valor)
                            print(f"Coletado {chave}: {valor} -> {dados[campo]}")
                            break
            
        except Exception as e:
            print(f"Erro ao processar tabela nutricional: {e}")
        
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
    
    return dados

def coletar_dados_nutricionais():
    """Função principal para coleta dos dados nutricionais"""
    # Carregar URLs dos produtos
    try:
        with open('dados/urls_produtos.json', 'r', encoding='utf-8') as f:
            dados_json = json.load(f)
            urls_produtos = dados_json.get('urls', [])
            total_urls = dados_json.get('total', 0)
    except FileNotFoundError:
        print("Arquivo urls_produtos.json não encontrado!")
        return None
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON!")
        return None
    
    if not urls_produtos:
        print("Nenhuma URL encontrada no arquivo!")
        return None
    
    print(f"\nIniciando coleta de dados nutricionais de {total_urls} produtos...")
    
    driver = iniciar_driver()
    if not driver:
        return None
    
    dados_nutricionais = []
    
    try:
        # Processar cada URL
        for url in tqdm(urls_produtos, desc="Processando produtos"):
            try:
                dados_produto = extrair_dados_nutricionais(driver, url)
                if dados_produto:
                    dados_nutricionais.append(dados_produto)
                time.sleep(1)  # Pequena pausa entre produtos
            except Exception as e:
                print(f"\nErro ao processar URL {url}: {e}")
                continue
        
        # Criar DataFrame com os dados coletados
        if dados_nutricionais:
            df = pd.DataFrame(dados_nutricionais)
            
            # Criar diretório se não existir
            os.makedirs('dados/csv', exist_ok=True)
            
            # Salvar dados em CSV
            caminho_csv = 'dados/csv/dados_nutricionais.csv'
            df.to_csv(caminho_csv, index=False, encoding='utf-8')
            print(f"\nDados salvos em '{caminho_csv}'")
            
            return df
        else:
            print("\nNenhum dado nutricional foi coletado!")
            return None
            
    except Exception as e:
        print(f"\nErro durante a coleta de dados: {e}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    coletar_dados_nutricionais() 