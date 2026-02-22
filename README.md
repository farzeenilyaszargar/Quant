# 📊 Quant Stock Analysis Bot

An automated quantitative equity analysis pipeline for Indian stocks (NSE/BSE), with a Next.js portfolio dashboard.

---

## Project Structure

```
StocksPortfolioBuyBot/
├── main.py                  # 🚀 Main pipeline entry point (run this)
├── stockFetch.py            # Scrapes financial data from screener.in
├── processData.py           # Computes metrics, ratios & sub-scores
├── calcEngine.py            # DCF valuation + composite score weighting
├── aiAnalysis.py            # DeepSeek AI qualitative scoring
├── portfolioOptimizer.py    # Portfolio filtering & weight allocation
├── updateStockList.py       # Downloads latest NSE / Nifty 500 stock list
├── updateNifty500.py        # Shim → updateStockList.py --nifty500
├── listOfStocks.json        # Active symbol universe (input to pipeline)
├── nifty500Stocks.json      # Nifty 500 snapshot
├── stockData.json           # Output: full analysis results
├── .env                     # API keys (not committed)
└── website/                 # Next.js dashboard
    ├── app/
    │   ├── portfolio/       # Main portfolio overview
    │   ├── insights/        # Deep dive per company
    │   └── rankings/        # Full quant ranking table
    └── components/
        ├── PortfolioView.tsx
        ├── InsightView.tsx
        └── RankingView.tsx
```

---

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 pandas urllib3
```

Add your DeepSeek API key to `.env`:
```
DEEPSEEK_API_KEY=sk-...
```

---

## Usage

### 1. Update stock universe
```bash
# Full NSE (~5000 stocks, takes many hours to analyse)
python updateStockList.py

# Nifty 500 only (recommended for daily runs)
python updateStockList.py --nifty500
```

### 2. Run analysis pipeline
```bash
python main.py
```
The pipeline is **resumable** — it skips already-processed stocks.  
To restart from scratch, delete `stockData.json`.

### 3. View dashboard
```bash
cd website
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000)

---

## Scoring Model

| Component | Weight | Source |
|---|---|---|
| DCF Valuation | 30% | Screener.in financial tables |
| Revenue + Profit CAGR | 20% | Screener.in P&L |
| ROCE | 10% | Screener.in ratios |
| Moat + Customer Score | 15% | DeepSeek AI |
| FII/DII Activity + D/E | 5% | Screener.in shareholding |
| Sector Tailwind | 10% | DeepSeek AI |
| Management Quality | 10% | DeepSeek AI |

---

## Portfolio Allocation
- Stocks scoring **< 45** are excluded
- Stocks trading **>15% above intrinsic value** are excluded
- Top 50 are allocated using **score² weighting** for conviction-proportional positions
