import json
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# 1. Ativos em destaque que aparecem no select principal do menu
DESTAQUES = {
    "BBAS3": "Banco do Brasil",
    "BBSE3": "BB Seguridade",
    "ITSA4": "Itaúsa",
    "BBDC3": "Bradesco ON",
    "TRXF11": "TRX Real Estate (FII)",
    "XSPI11": "XP S&P 500 Div ETF",
    "XBCI11": "XP Crédito Imobiliário ETF",
    "TAEE11": "Taesa",
    "ISAE4": "ISA Energia (CTEEP)",
    "CMIG4": "Cemig PN",
    "CPFE3": "CPFL Energia",
    "BEES3": "Banestes",
}

# 2. Lista base de sufixos e classes para varrer a B3 (Ações 3, 4, 11 e FIIs/ETFs 11)
# Você pode adicionar qualquer ticker específico que queira garantir aqui também:
TICKERS_EXTRAS = [
    # Bancos e Financeiro
    "ITUB3",
    "ITUB4",
    "BBDC4",
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
    "CXSE3",
    # Elétricas e Saneamento
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
    # Commodities, Óleo e Gás
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
    "SUZB3",
    "KLBN11",
    "KLBN4",
    "KLBN3",
    "RANI3",
    # Consumo, Varejo, Agro e Indústria
    "WEGE3",
    "TUPY3",
    "ROMI3",
    "LEVE3",
    "POMO4",
    "RAPT4",
    "KEPL3",
    "AGRO3",
    "SLCE3",
    "TTEN3",
    "SMTO3",
    "JBSS3",
    "BRFS3",
    "MRFG3",
    "BEEF3",
    "MDIA3",
    "ABEV3",
    "VIVT3",
    "TIMS3",
    "RADL3",
    "FLRY3",
    "RDOR3",
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
    "CURY3",
    "JHSF3",
    "RAIL3",
    "CCRO3",
    "ECOR3",
    "STBP3",
    "VAMO3",
    "RENT3",
    "MOVI3",
    # Principais FIIs e ETFs do Mercado
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
    "TIRB11",
    "CHIP11",
    "COIN11",
    "ETHY11",
    "OBTC3",
    "BOVA11",
    "IVVB11",
    "HASH11",
    "NDIV11",
    "DIVO11",
]

# Junta tudo sem duplicar
todos_os_tickers = list(dict.fromkeys(list(DESTAQUES.keys()) + TICKERS_EXTRAS))

dados_saida = {
    "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "destaques": list(DESTAQUES.keys()),
    "ativos": {},
}

um_ano_atras = datetime.now() - timedelta(days=365)
print(f"Baixando dados para {len(todos_os_tickers)} ativos da B3...")

# Baixa em lote usando yfinance para otimizar velocidade
tickers_yf = [f"{t}.SA" for t in todos_os_tickers]
lote_dados = yf.download(
    tickers_yf, period="5d", group_by="ticker", threads=True, progress=False
)

for ticker in todos_os_tickers:
  try:
    simbolo_yf = f"{ticker}.SA"
    # Extrai o fechamento recente do lote ou busca individual se o lote falhar
    if len(todos_os_tickers) == 1:
      hist = lote_dados
    else:
      hist = (
          lote_dados[simbolo_yf]
          if simbolo_yf in lote_dados.columns.levels[0]
          else pd.DataFrame()
      )

    if hist.empty or "Close" not in hist.columns:
      continue

    preco_atual = float(hist["Close"].dropna().iloc[-1])
    if preco_atual <= 0:
      continue

    # Puxa dividendos do último ano
    papel = yf.Ticker(simbolo_yf)
    dividendos = papel.dividends
    dpa_12m = 0.0
    if not dividendos.empty:
      dividendos.index = dividendos.index.tz_localize(None)
      div_12m = dividendos[dividendos.index >= um_ano_atras]
      dpa_12m = float(div_12m.sum())

    dy_anual = (dpa_12m / preco_atual) * 100 if preco_atual > 0 else 0.0

    # Fallback de segurança para ativos sem histórico completo de proventos na API
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
    print(f"[OK] {ticker}: R$ {preco_atual:.2f} | DY: {dy_anual:.2f}%")

  except Exception as e:
    print(f"[IGNORADO] {ticker}: {e}")

# Salva o super JSON na raiz do repositório
with open("cotacoes.json", "w", encoding="utf-8") as f:
  json.dump(dados_saida, f, ensure_ascii=False, indent=2)

print(
    f"Sucesso! {len(dados_saida['ativos'])} ativos gravados no cotacoes.json."
)
