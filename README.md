# Scraping Essential Nutrition

Este projeto realiza web scraping do site da Essential Nutrition para coletar dados nutricionais dos produtos.

## Estrutura do Projeto

```
.
├── config/
│   ├── url_collector.py    # Coleta URLs dos produtos
│   ├── scraper.py         # Extrai dados nutricionais
│   └── teste_coleta.py    # Script de testes
├── dados/
│   ├── csv/              # Arquivos CSV com dados nutricionais
│   └── urls_produtos.json # URLs coletadas
└── main.py               # Script principal de execução
```

## Funcionalidades

- Coleta URLs de produtos de 15 categorias diferentes
- Extrai dados nutricionais incluindo:
  - Nome do produto
  - Categoria
  - Porção
  - Calorias
  - Carboidratos
  - Proteínas
  - Gorduras totais
  - Fibras
  - Açúcares
  - Sódio

## Como Usar

1. Instale as dependências:
```bash
pip install selenium pandas tqdm webdriver-manager
```

2. Execute o script principal:
```bash
python main.py
```

O script irá:
1. Coletar todas as URLs dos produtos
2. Extrair os dados nutricionais
3. Salvar os resultados em:
   - `dados/urls_produtos.json`
   - `dados/csv/dados_nutricionais.csv`

## Notas

- O script utiliza o Chrome em modo headless
- Inclui tratamento para URLs duplicadas
- Detecta páginas vazias automaticamente
- Ajusta o zoom para melhor visualização dos dados
- Trata diferentes formatos de tabelas nutricionais
