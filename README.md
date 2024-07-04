# 📊 Projeto de Previsão de Pontos e Gerador de Heatmap para o Brasileirão 2024

Bem-vindo ao repositório do projeto de Previsão de Pontos e Gerador de Heatmap para o Brasileirão 2024! 🎉 Este projeto utiliza Python, Flask e diversas bibliotecas para apresentar uma tabela de previsão de pontos dos times do Brasileirão e gerar heatmaps para partidas específicas.

## 📋 Visão Geral

Este projeto é dividido em duas principais funcionalidades:

1. **Previsão de Pontos**: Utiliza dados históricos do Campeonato Brasileiro para prever a pontuação dos times.
2. **Gerador de Heatmap**: Gera heatmaps de partidas específicas, mostrando a probabilidade de diferentes resultados.

## 🚀 Funcionalidades

### Previsão de Pontos

- **Coleta de Dados**: Os dados são coletados diretamente da Wikipédia.
- **Ajuste e Limpeza de Dados**: Os dados são ajustados e limpos para preparar a análise.
- **Cálculo de Pontos Esperados**: Utiliza a distribuição de Poisson para calcular a pontuação esperada para cada partida.

### Gerador de Heatmap

- **Geração de Heatmap**: Utiliza a distribuição de Poisson para calcular a probabilidade de diferentes resultados e exibir um heatmap visualmente atraente.
- **API Flask**: Implementa uma API Flask para gerar e servir os heatmaps sob demanda.


## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Pandas**: Biblioteca para manipulação e análise de dados.
- **Requests**: Biblioteca para fazer requisições HTTP.
- **Scipy (Poisson)**: Para cálculos estatísticos.
- **Matplotlib e Seaborn**: Para visualização de dados.
- **Flask**: Framework web para criar a API.
- **Flask-CORS**: Para permitir requisições de diferentes origens (CORS).

## 🚧 Como Executar o Projeto

Siga os passos abaixo para rodar o projeto localmente:

1. Clone este repositório:

```bash
git clone https://github.com/ThiagoS1lva/PreVejaPlacar
cd PreVejaPlacar
```

2. Crie um ambiente virtual e ative-o:
3. Instale as dependências:
4. Execute a aplicação:

O servidor Flask estará disponível em `http://localhost:5000`.

## 📚 Como Usar

### Previsão de Pontos

1. Acesse a rota principal (`/`) para visualizar a tabela de previsão de pontos.
2. A tabela será retornada em formato JSON com a pontuação esperada para cada time.

### Gerador de Heatmap

1. Faça uma requisição POST para a rota `/heatmap` com os times da casa e visitante.
2. O heatmap será retornado como uma imagem PNG.


Feito com ❤️ por [Thiago Oliveira](https://github.com/ThiagoS1lva).

