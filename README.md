<div align="center">

# Sigaa-Scraper

**Web scraper de alta eficiência para extração de dados acadêmicos do SIGAA/UnB**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.21-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://selenium.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-Unlicense-lightgrey?style=for-the-badge)](LICENSE)

</div>

---

## Sobre o Projeto

O **Sigaa-Scraper** é um software de web scraping desenvolvido para extrair automaticamente os dados de turmas disponíveis no portal público do SIGAA da Universidade de Brasília (UnB), disponível em:

> 🔗 [https://sigaa.unb.br/sigaa/public/turmas/listar.jsf](https://sigaa.unb.br/sigaa/public/turmas/listar.jsf)

Todos os dados extraídos são persistidos em um banco de dados **PostgreSQL**, com estrutura relacional otimizada via DDL e triggers de banco.

### Destaques técnicos

- **Complexidade O(N)** — o scraper nunca visita a mesma categoria mais de uma vez, garantindo eficiência máxima independente do volume de dados
- **Proxy rotativo** — sistema de rotação e validação de proxies para distribuir as requisições e evitar bloqueios
- **Browser headless** — utiliza Selenium com Chrome em modo headless, permitindo execução completa em containers Docker sem interface gráfica
- **Multithreading** — uso de `threading` e `queue` para processamento paralelo e maior throughput
- **Menor impacto possível** — projetado para minimizar requisições ao sistema da UnB, respeitando a infraestrutura do servidor

---

## Estrutura do Projeto

```
Sigaa-Scraper/
├── src/
│   ├── main.py                  # Entrypoint principal do scraper
│   ├── check_proxies.py         # Validação e filtragem de proxies
│   ├── proxies_funcionais.txt   # Lista de proxies validados
│   ├── proxy_list.txt           # Pool de proxies brutos
│   └── Dockerfile               # Imagem do serviço scraper
├── db/
│   ├── ddl.sql                  # Criação das tabelas (schema)
│   └── triggers.sql             # Triggers do banco de dados
├── docs/                        # Documentação adicional
├── compose.yml                  # Orquestração Docker
├── requirements.txt             # Dependências Python
└── README.md
```

---

## Sistema de Proxy Rotativo

Um dos pilares do projeto é o sistema de proxy rotativo, que garante a continuidade do scraping mesmo em execuções longas.

**Fluxo de funcionamento:**

```
proxy_list.txt  ──►  check_proxies.py  ──►  proxies_funcionais.txt  ──►  main.py
  (pool bruto)         (validação)            (proxies vivos)           (rotação)
```

1. **`proxy_list.txt`** — contém a lista completa de proxies candidatos
2. **`check_proxies.py`** — testa cada proxy fazendo requisições reais, filtrando os que respondem dentro do timeout esperado
3. **`proxies_funcionais.txt`** — resultado da validação; apenas proxies funcionais chegam aqui
4. **`main.py`** — consome a lista funcional com rotação automática, trocando de proxy em caso de falha ou bloqueio

Essa abordagem evita banimentos de IP e distribui a carga das requisições entre múltiplos endereços.

---

## Stack & Dependências

| Biblioteca             | Versão | Uso                                     |
|------------------------|--------|-----------------------------------------|
| `selenium`             | 4.21.0 | Automação do browser (Chrome headless)  |
| `psycopg2-binary`      | 2.9.9  | Conexão com PostgreSQL                  |
| `requests`             | 2.32.3 | Validação de proxies e requisições HTTP |
| `threading` *(nativo)* | —      | Processamento paralelo                  |
| `queue` *(nativo)*     | —      | Controle de fila entre threads          |

---

## Executando com Docker

O projeto está totalmente containerizado. O `compose.yml` orquestra dois serviços:

- **`db`** — PostgreSQL 16 com inicialização automática via `ddl.sql` e `triggers.sql`
- **`scraper`** — serviço Python com Chrome headless instalado

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/) instalados

### Subindo o ambiente

```bash
# Clone o repositório
git clone https://github.com/i-JSS/Sigaa-Scraper.git
cd Sigaa-Scraper

# Suba os serviços
docker compose up -d
```

O banco de dados será inicializado automaticamente com o schema e os triggers na primeira execução.

> **Atenção:** os scripts de init só rodam quando o volume está vazio. Para reinicializar o banco:
> ```bash
> docker compose down -v
> docker compose up -d
> ```

### Variáveis de ambiente

| Variável      | Valor padrão | Descrição                                  |
|---------------|--------------|--------------------------------------------|
| `DB_HOST`     | `db`         | Host do banco (nome do serviço no Compose) |
| `DB_PORT`     | `5432`       | Porta do PostgreSQL                        |
| `DB_USER`     | `kd_user`    | Usuário do banco                           |
| `DB_PASSWORD` | `123`        | Senha do banco                             |
| `DB_NAME`     | `KDmeuSS`    | Nome do banco de dados                     |

---

## Executando localmente (sem Docker)

```bash
# Instale as dependências
pip install -r requirements.txt

# Certifique-se de ter o ChromeDriver compatível com seu Chrome instalado
# https://chromedriver.chromium.org/downloads

# Execute o scraper
python src/main.py
```

Certifique-se de ter um PostgreSQL local rodando com as credenciais configuradas no `src/main.py`, ou exporte as variáveis de ambiente correspondentes.

---

## Banco de Dados

A estrutura do banco é definida em dois arquivos dentro da pasta `db/`:

- **`ddl.sql`** — criação das tabelas, índices e relacionamentos
- **`triggers.sql`** — triggers para automação de regras de negócio no banco

No ambiente Docker, ambos são executados automaticamente na inicialização do container PostgreSQL, na ordem correta (`ddl` antes de `triggers`).

---

## Licença

Este projeto está sob a licença [Unlicense](LICENSE) — você é livre para usar, copiar, modificar e distribuir sem restrições.

---

<div align="center">

Feito por [João Ginuino](https://github.com/i-JSS) - UnB

</div>