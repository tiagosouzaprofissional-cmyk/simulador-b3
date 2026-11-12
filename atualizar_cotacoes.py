import json
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Lista de ativos do simulador (padrão B3 no Yahoo Finance termina com .SA)
ATIVOS = {
    "BBAS3": "Banco do Brasil",
    "BBSE3": "BB Seguridade",
    "ITSA4": "Itaúsa",
    "BBDC3": "Bradesco ON",
    "BBDC4": "Bradesco PN",
    "BEES3": "Banestes",
    "TAEE11": "Taesa",
    "ISAE4": "ISA Energia (ex-TRPL4)",
    "CPFE3": "CPFL Energia",
    "CMIG4": "Cemig",
    "TRXF11": "TRX Real Estate (FII)",
    "CXSE3": "Caixa Seguridade",
}

dados_saida = {
    "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "ativos": {},
}

um_ano_atras = datetime.now() - timedelta(days=365)

for ticker, nome in ATIVOS.items():
  try:
    papel = yf.Ticker(f"{ticker}.SA")

    # 1. Puxar cotação atual
    hist = papel.history(period="5d")
    if hist.empty:
      continue
    preco_atual = float(hist["Close"].iloc[-1])

    # 2. Calcular Dividendos pagos nos últimos 12 meses
    dividendos = papel.dividends
    dpa_12m = 0.0
    if not dividendos.empty:
      # Remove fuso horário do índice para comparar datas com segurança
      dividendos.index = dividendos.index.tz_localize(None)
      div_12m = dividendos[dividendos.index >= um_ano_atras]
      dpa_12m = float(div_12m.sum())

    # 3. Calcular Dividend Yield (%) e Preço-Teto Bazin (6%)
    dy_anual = (dpa_12m / preco_atual) * 100 if preco_atual > 0 else 0.0

    # Fallback caso a API do Yahoo falhe nos dividendos de algum ativo específico
    if dy_anual == 0 and "dividendYield" in papel.info and papel.info["dividendYield"]:
      dy_anual = float(papel.info["dividendYield"]) * 100
      dpa_12m = preco_atual * (dy_anual / 100)

    dados_saida["ativos"][ticker] = {
        "nome": nome,
        "preco": round(preco_atual, 2),
        "dy": round(dy_anual, 2),
        "dpa": round(dpa_12m, 2),
        "teto_bazin": round(dpa_12m / 0.06, 2),
    }
    print(f"[OK] {ticker}: R$ {preco_atual:.2f} | DY: {dy_anual:.2f}%")

  except Exception as e:
    print(f"[ERRO] Falha ao processar {ticker}: {e}")

# Salva o JSON na raiz do repositório
with open("cotacoes.json", "w", encoding="utf-8") as f:
  json.dump(dados_saida, f, ensure_ascii=False, indent=2)
