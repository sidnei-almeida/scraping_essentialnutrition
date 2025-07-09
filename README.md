# 🚀 Web Scraping Essential Nutrition

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

Sistema automatizado para coleta de dados nutricionais do site Essential Nutrition. O projeto utiliza técnicas avançadas de web scraping para extrair informações detalhadas sobre produtos nutricionais.

## 📋 Índice

- [Recursos](#-recursos)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Dados Coletados](#-dados-coletados)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## ✨ Recursos

- 🔍 Coleta automática de URLs de produtos de 15 categorias diferentes
- 📊 Extração detalhada de dados nutricionais
- 💾 Exportação em formatos JSON e CSV
- 🎯 Sistema de teste para validação rápida
- 🌐 Suporte multi-navegador (Chrome, Firefox, Edge, Opera)
- 🖥️ Compatível com Windows e Linux
- 🤖 Modo headless para execução em segundo plano
- 🛡️ Tratamento robusto de erros e exceções

## 📦 Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web (Chrome, Firefox, Edge ou Opera)
- WebDriver correspondente ao navegador (instalado automaticamente)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/scraping_essentialnutrition.git
cd scraping_essentialnutrition
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Uso

Execute o programa principal:
```bash
python main.py
```

O programa oferece as seguintes opções:

1. 🔍 **Coletar URLs**: Busca URLs dos produtos
2. 📊 **Coletar Dados**: Extrai dados nutricionais
3. 🎯 **Coleta Completa**: URLs + Dados nutricionais
4. 🧪 **Teste Rápido**: Testa com 3 produtos
5. 📋 **Ver Arquivos**: Lista arquivos gerados
6. 🗑️ **Limpar Dados**: Remove arquivos antigos
7. 📖 **Sobre**: Informações do programa
8. ❌ **Sair**: Encerrar programa

## 📁 Estrutura do Projeto

```
scraping_essentialnutrition/
├── config/
│   ├── browser.py       # Gerenciador de navegadores
│   ├── scraper.py       # Extrator de dados nutricionais
│   ├── url_collector.py # Coletor de URLs
│   └── teste_coleta.py  # Módulo de testes
├── dados/
│   ├── urls_produtos.json      # URLs coletadas
│   └── csv/
│       └── dados_nutricionais.csv  # Dados extraídos
├── main.py             # Programa principal
├── requirements.txt    # Dependências
└── README.md          # Documentação
```

## 📊 Dados Coletados

O sistema coleta os seguintes dados nutricionais:

- Nome do produto
- Categoria
- Porção
- Calorias
- Carboidratos
- Proteínas
- Gorduras totais
- Gorduras saturadas
- Fibras
- Açúcares
- Sódio

Os dados são salvos em dois formatos:
- `dados/urls_produtos.json`: Lista de URLs coletadas
- `dados/csv/dados_nutricionais.csv`: Dados nutricionais em formato tabular

## 🔧 Recursos Técnicos

### BrowserManager

O sistema inclui um gerenciador de navegadores inteligente que:
- Detecta automaticamente navegadores instalados
- Suporta Chrome, Firefox, Edge e Opera
- Funciona em Windows e Linux
- Configura WebDrivers automaticamente
- Oferece modo headless para todos os navegadores

### Tratamento de Erros

- Detecção e remoção automática de popups
- Ajuste automático de zoom
- Múltiplas tentativas de clique em elementos
- Tratamento de timeouts e elementos não encontrados
- Logs detalhados do processo

### Performance

- Execução em modo headless
- Detecção e tratamento de URLs duplicadas
- Otimização de requisições
- Paralelização de coletas (quando possível)

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

Sidnei Almeida
- GitHub: [@sidnei-junior](https://github.com/sidnei-junior)

---

⭐️ Se este projeto te ajudou, considere dar uma estrela!
