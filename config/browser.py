#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Browser Manager
==============
Módulo para detecção e configuração automática de navegadores web.
Suporta Chrome, Firefox, Edge e Opera nos sistemas Windows e Linux.
"""

import os
import sys
import subprocess
from typing import Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager

class BrowserManager:
    """Gerenciador de navegadores para automação web"""
    
    # Caminhos padrão dos navegadores no Windows
    WINDOWS_PATHS = {
        'chrome': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ],
        'firefox': [
            r'C:\Program Files\Mozilla Firefox\firefox.exe',
            r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
        ],
        'edge': [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        ],
        'opera': [
            r'C:\Program Files\Opera\launcher.exe',
            r'C:\Program Files (x86)\Opera\launcher.exe',
        ]
    }
    
    # Caminhos padrão dos navegadores no Linux
    LINUX_PATHS = {
        'chrome': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
        ],
        'firefox': [
            '/usr/bin/firefox',
            '/usr/lib/firefox/firefox',
        ],
        'edge': [
            '/usr/bin/microsoft-edge',
            '/usr/bin/microsoft-edge-stable',
        ],
        'opera': [
            '/usr/bin/opera',
            '/usr/lib/opera/opera',
        ]
    }

    @staticmethod
    def is_windows() -> bool:
        """Verifica se o sistema é Windows"""
        return sys.platform.startswith('win')

    @staticmethod
    def check_browser_linux(browser_name: str) -> Optional[str]:
        """Verifica se um navegador está instalado no Linux usando 'which'"""
        try:
            result = subprocess.run(['which', browser_name], 
                                 capture_output=True, 
                                 text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def find_browser_path(browser_type: str) -> Optional[str]:
        """Encontra o caminho do executável do navegador"""
        paths = BrowserManager.WINDOWS_PATHS if BrowserManager.is_windows() else BrowserManager.LINUX_PATHS
        
        # Verificar caminhos padrão
        for path in paths.get(browser_type, []):
            if os.path.isfile(path):
                return path
        
        # No Linux, tentar encontrar usando 'which'
        if not BrowserManager.is_windows():
            if browser_type == 'chrome':
                path = BrowserManager.check_browser_linux('google-chrome')
                if not path:
                    path = BrowserManager.check_browser_linux('chromium')
            elif browser_type == 'edge':
                path = BrowserManager.check_browser_linux('microsoft-edge')
            else:
                path = BrowserManager.check_browser_linux(browser_type)
            
            if path:
                return path
        
        return None

    @staticmethod
    def get_available_browsers() -> Dict[str, str]:
        """Retorna um dicionário com os navegadores disponíveis e seus caminhos"""
        browsers = {}
        for browser in ['chrome', 'firefox', 'edge', 'opera']:
            path = BrowserManager.find_browser_path(browser)
            if path:
                browsers[browser] = path
        return browsers

    @staticmethod
    def setup_driver(browser_type: str = None, headless: bool = True) -> Tuple[Optional[webdriver.Remote], str]:
        """
        Configura e retorna um driver do Selenium para o navegador especificado
        
        Args:
            browser_type: Tipo de navegador ('chrome', 'firefox', 'edge', 'opera')
            headless: Se True, executa o navegador em modo headless
        
        Returns:
            Tupla (driver, browser_name) ou (None, error_message)
        """
        available_browsers = BrowserManager.get_available_browsers()
        
        # Se nenhum navegador foi especificado, usar o primeiro disponível
        if not browser_type:
            if not available_browsers:
                return None, "Nenhum navegador compatível encontrado no sistema"
            browser_type = list(available_browsers.keys())[0]
        
        # Verificar se o navegador solicitado está disponível
        if browser_type not in available_browsers:
            return None, f"Navegador {browser_type} não encontrado no sistema"
        
        try:
            if browser_type == 'chrome':
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                
            elif browser_type == 'firefox':
                options = FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
                
            elif browser_type == 'edge':
                options = EdgeOptions()
                if headless:
                    options.add_argument('--headless')
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
                
            elif browser_type == 'opera':
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                service = ChromeService(OperaDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            
            else:
                return None, f"Tipo de navegador não suportado: {browser_type}"
            
            return driver, browser_type
            
        except Exception as e:
            return None, f"Erro ao configurar o driver para {browser_type}: {str(e)}"

    @staticmethod
    def print_browser_info():
        """Imprime informações sobre os navegadores disponíveis"""
        print("\n🔍 Navegadores encontrados no sistema:")
        print("=" * 50)
        
        browsers = BrowserManager.get_available_browsers()
        if not browsers:
            print("❌ Nenhum navegador compatível encontrado!")
            return
        
        for browser, path in browsers.items():
            print(f"\n✅ {browser.upper()}:")
            print(f"   📂 Caminho: {path}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    # Exemplo de uso
    BrowserManager.print_browser_info()
    
    print("\n🚀 Testando configuração do driver...")
    driver, browser_name = BrowserManager.setup_driver(headless=True)
    
    if driver:
        print(f"✅ Driver configurado com sucesso usando {browser_name}")
        driver.quit()
    else:
        print(f"❌ Erro: {browser_name}") 