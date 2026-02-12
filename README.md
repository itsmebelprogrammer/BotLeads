
# BotLeads (CLI)

Coletor **MVP** (minimal) de leads do **Google Maps** usando **Selenium**, com export para **CSV/XLSX**.

A ideia é simples e fácil de entender: ele coleta somente **Nome**, **Telefone** (quando disponível) e **Site** (quando disponível), e gera um link `wa.me` para facilitar o contato via WhatsApp.

## Funcionalidades

- Busca no Google Maps por um termo (ex.: `"pizzaria Curitiba"`)
- Coleta os campos:
  - Nome
  - Telefone (best-effort)
  - Site (best-effort)
  - Link do WhatsApp (`wa.me`) baseado no telefone normalizado
- Exporta para:
  - CSV (padrão)
  - XLSX (opcional)


## Requisitos

- Python \( \ge 3.x \)
- Google Chrome instalado

## Instalação

1) Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

2) Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como usar (CLI)

Exemplo (Chrome invisível):

```bash
python main.py --q "pizzaria Curitiba" --n 30 --fmt csv --headless
```

Exemplo (Chrome visível):

```bash
python main.py --q "advocacia Londrina" --n 20 --fmt xlsx --no-headless
```

### Parâmetros

- `--q` / `--query`: termo de busca (obrigatório)
- `--n` / `--limit`: quantidade de leads (padrão: `30`)
- `--fmt`: `csv` ou `xlsx` (padrão: `csv`)
- `--headless`: roda sem abrir janela
- `--no-headless`: força rodar com janela
- `--delay`: atraso entre cliques (padrão: `0.3`)

## Saída

Os arquivos são criados na pasta `output/` com timestamp:

- `output/leads_YYYYMMDD_HHMMSS.csv`
- `output/leads_YYYYMMDD_HHMMSS.xlsx`

## Notas técnicas

- O Google Maps muda com frequência; seletores podem quebrar e exigir ajustes no `maps_scraper.py`.
- Use com moderação para evitar bloqueios/limites.

## Contribuições

PRs são bem-vindos, especialmente para:

- Melhorar a robustez dos seletores do Maps
- Melhorar normalização de telefone e URL
- Adicionar mais campos opcionais (ex.: categoria)

## Aviso

Este projeto é para fins educacionais e de automação interna. Você é responsável por respeitar os termos de uso do Google e a legislação aplicável ao coletar e usar dados de contato.

---