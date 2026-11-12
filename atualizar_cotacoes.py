from datetime import datetime
import json
import pandas as pd
import yfinance as yf

DESTAQUES = {
    "BBAS3": "Banco do Brasil",
    "BBSE3": "BB Seguridade",
    "ITSA4": "Itaúsa",
    "BBDC3": "Bradesco ON",
    "BBDC4": "Bradesco PN",
    "TRXF11": "TRX Real Estate (FII)",
    "XSPI11": "XP S&P 500 Dividendos ETF",
    "XBCI11": "XP Crédito Imobiliário ETF",
    "TAEE11": "Taesa",
    "ISAE4": "ISA Energia (CTEEP)",
    "CMIG4": "Cemig PN",
    "CPFE3": "CPFL Energia",
    "BEES3": "Banestes",
    "CXSE3": "Caixa Seguridade",
}

DY_REFERENCIA = {
    "XBCI11": 11.4,
    "XSPI11": 9.8,
    "TIRB11": 10.5,
    "CHIP11": 9.5,
    "COIN11": 12.0,
    "ETHY11": 11.5,
    "NDIV11": 8.5,
    "DIVO11": 7.5,
}

TICKERS_EXTRAS = [
    "XSPI11",
    "XBCI11",
    "TIRB11",
    "CHIP11",
    "COIN11",
    "ETHY11",
    "OBTC3",
    "NDIV11",
    "DIVO11",
    "BOVA11",
    "IVVB11",
    "HASH11",
    "ITUB3",
    "ITUB4",
    "SANB11",
    "SANB3",
    "SANB4",
    "BPAC11",
    "BRSR6",
    "ABCB4",
    "BMGB4",
    "BRBI11",
    "PSSA3",
    "IRBR3",
    "B3SA3",
    "CIEL3",
    "BEES4",
    "ELET3",
    "ELET6",
    "EGIE3",
    "EQTL3",
    "CPLE6",
    "CPLE3",
    "ENGI11",
    "NEOE3",
    "AURE3",
    "ALUP11",
    "CMIG3",
    "TAEE3",
    "TAEE4",
    "ISAE3",
    "SBSP3",
    "SAPR11",
    "SAPR4",
    "SAPR3",
    "CSMG3",
    "PETR4",
    "PETR3",
    "VALE3",
    "PRIO3",
    "RECV3",
    "BRAV3",
    "CSAN3",
    "UGPA3",
    "VBBR3",
    "RAIZ4",
    "GGBR4",
    "GGBR3",
    "GOAU4",
    "CSNA3",
    "USIM5",
    "CMIN3",
    "FESA4",
    "SUZB3",
    "KLBN11",
    "KLBN4",
    "KLBN3",
    "RANI3",
    "WEGE3",
    "TUPY3",
    "ROMI3",
    "LEVE3",
    "POMO4",
    "RAPT4",
    "KEPL3",
    "SHUL4",
    "AGRO3",
    "SLCE3",
    "TTEN3",
    "SMTO3",
    "JALL3",
    "JBSS3",
    "BRFS3",
    "MRFG3",
    "BEEF3",
    "MDIA3",
    "CAML3",
    "ABEV3",
    "VIVT3",
    "TIMS3",
    "UNIP6",
    "UNIP3",
    "RADL3",
    "FLRY3",
    "ODPV3",
    "HYPE3",
    "LREN3",
    "MGLU3",
    "ASAI3",
    "CRFB3",
    "MULT3",
    "IGTI11",
    "ALOS3",
    "CYRE3",
    "EZTC3",
    "MRVE3",
    "DIRR3",
    "CURY3",
    "LAVV3",
    "JHSF3",
    "RAIL3",
    "CCRO3",
    "ECOR3",
    "STBP3",
    "VAMO3",
    "RENT3",
    "MOVI3",
    "MXRF11",
    "HGLG11",
    "XPML11",
    "KNRI11",
    "KNCR11",
    "KNIP11",
    "HGRU11",
    "VISC11",
    "XPLG11",
    "BRCO11",
    "BTLG11",
    "VILG11",
    "HGBS11",
    "MALL11",
    "CPTS11",
    "IRDM11",
    "RECR11",
    "VRTA11",
    "HGCR11",
    "RBRR11",
    "KNSC11",
    "TGAR11",
    "RZTR11",
    "ALZR11",
    "GGRC11",
    "VGHF11",
    "VGIR11",
    "SNAG11",
    "KNCA11",
    "RZAG11",
    "VGIA11",
    "FGAA11",
    "XPCA11",
    "BCFF11",
    "KFOF11",
]

todos_os_tickers = list(dict.fromkeys(list(DESTAQUES.keys()) + TICKERS_EXTRAS))

dados_saida = {
    "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "destaques": list(DESTAQUES.keys()),
    "ativos": {},
}

tickers_yf = [f"{t}.SA" for t in todos_os_tickers]
lote_dados = yf.download(
    tickers_yf,
    period="1y",
    actions=True,
    group_by="ticker",
    threads=True,
    progress=False,
)

for ticker in todos_os_tickers:
  try:
    simbolo_yf = f"{ticker}.SA"
    if isinstance(lote_dados.columns, pd.MultiIndex):
      if simbolo_yf not in lote_dados.columns.levels[0]:
        continue
      hist = lote_dados[simbolo_yf]
    else:
      hist = lote_dados

    if hist.empty or "Close" not in hist.columns:
      continue

    fechamentos = hist["Close"].dropna()
    if fechamentos.empty:
      continue

    preco_atual = float(fechamentos.iloc[-1])
    if preco_atual <= 0:
      continue

    dpa_12m = 0.0
    if "Dividends" in hist.columns:
      dpa_12m = float(hist["Dividends"].dropna().sum())

    dy_anual = (dpa_12m / preco_atual) * 100.0 if preco_atual > 0 else 0.0

    if dy_anual == 0 and ticker in DY_REFERENCIA:
      dy_anual = DY_REFERENCIA[ticker]
      dpa_12m = preco_atual * (dy_anual / 100.0)

    if dy_anual == 0:
      dy_anual = 6.0
      dpa_12m = preco_atual * 0.06

    nome_empresa = DESTAQUES.get(ticker, ticker)

    dados_saida["ativos"][ticker] = {
        "nome": nome_empresa,
        "preco": round(preco_atual, 2),
        "dy": round(dy_anual, 2),
        "dpa": round(dpa_12m, 2),
        "teto_bazin": round(dpa_12m / 0.06, 2),
    }
  except Exception as e:
    print(f"Erro em {ticker}: {e}")

with open("cotacoes.json", "w", encoding="utf-8") as f:
  json.dump(dados_saida, f, ensure_ascii=False, indent=2)

print(f"Finalizado com sucesso: {len(dados_saida['ativos'])} ativos salvos!")
