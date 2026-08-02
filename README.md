# Agregador de pesquisas · Eleições 2026

Painel próprio de agregação de pesquisas eleitorais de 2026, inspirado no RealClearPolitics
(visual) e no FiveThirtyEight (estatística). No ar em
https://rafaelcortopassi.pythonanywhere.com/electoralpolls/

Este repositório é a **fonte de verdade** do painel desde 02/08/2026. A cópia que existia na
pasta do Google Drive virou arquivo morto e não deve mais ser editada.

## O que tem aqui

| arquivo | o que é |
|---|---|
| `electoralpolls.html` | o painel inteiro, HTML autossuficiente com os dados embutidos no JS |
| `METODOLOGIA_AGREGADOR_PESQUISAS_2026.md` | metodologia e histórico de decisões. Leia antes de mexer |
| `AGENTS.md` | instruções da rotina automática que atualiza o painel |
| `radar_tse.py` | o que o TSE registrou de pesquisa, com desempate nacional x estadual |
| `mercados.py` | cotações do Polymarket e do Kalshi |
| `deploy_agregador.py` | sobe o painel para o PythonAnywhere pela API |
| `_gera_icones_agregador.py` | gera os ícones (favicon, apple-touch-icon) |

## Como publicar

Dar push na `main` com alteração em `electoralpolls.html` já publica: o workflow
`.github/workflows/deploy.yml` valida o JS e sobe pela API. Se o JS estiver quebrado, aborta e
nada vai ao ar.

Publicar da máquina, quando precisar:

```bash
PA_TOKEN=... PA_USER=rafaelcortopassi python3 deploy_agregador.py
```

## Segredos

O workflow precisa de dois segredos em Settings > Secrets and variables > Actions:

- `PA_TOKEN`: token da API do PythonAnywhere
- `PA_USER`: `rafaelcortopassi`

Nenhum token fica no repositório.
