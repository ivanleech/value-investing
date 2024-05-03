import yfinance as yf
import pandas as pd
import numpy as np
from forex_python.converter import CurrencyRates


class Model:
    def __init__(self):
        pass

    def get_current_price(self, ticker):
        hist = yf.Ticker(ticker).history()
        return hist.iloc[-1]["Close"]
        # return hist["Close"][-1]

    def clean_tickers(self, tickers):
        tickers = [ticker.strip() for ticker in tickers]
        tickers = [ticker.upper() for ticker in tickers]
        valid = set()
        invalid = set()
        wo_cashflow = set()

        for ticker in tickers:
            try:
                yf.Ticker(ticker).info
                if yf.Ticker(ticker).get_cash_flow().empty:
                    if len(yf.Ticker(ticker).history()) != 0:
                        wo_cashflow.add(ticker)
                    else:
                        invalid.add(ticker)
                else:
                    valid.add(ticker)
            except Exception as e:
                print("Error:", e)
                invalid.add(ticker)
                continue
        return valid, wo_cashflow, invalid

    def get_valuations(self, tickers, params={}):
        mos_dcf = float(params.get("mos_dcf", 0.5))
        terminal_growth = float(params.get("terminal_growth", 0.02))
        discount_rate = float(params.get("discount_rate", 0.1))
        conservative_cagr_factor = float(params.get("conservative_cagr_factor", 0.8))
        decreasingFcf = params.get("decreasingFcf", False)

        mos_bj = float(params.get("mos_bj", 0.5))
        pe_base = float(params.get("pe_base", 8.5))

        valid, wo_cashflow, invalid = self.clean_tickers(tickers)
        df = pd.DataFrame()
        model = Model()
        for ticker in valid:
            _, dcf_mos_fair_value = model.discounted_cashflow(
                ticker,
                mos_dcf,
                terminal_growth,
                discount_rate,
                conservative_cagr_factor,
                decreasingFcf,
            )
            _, bg_mos_fair_value = model.benjamin_graham(ticker, mos_bj, pe_base)
            pegy_ratio = model.pegy(ticker)
            pl_fair_value, peg = model.peter_lynch(ticker)

            df.loc[ticker, "Ticker"] = ticker.upper()
            df.loc[ticker, "Current Price"] = yf.Ticker(ticker).info.get("currentPrice")
            df.loc[ticker, "PEG"] = peg
            df.loc[ticker, "Fair Value (Discounted Cash Flow)"] = dcf_mos_fair_value
            df.loc[ticker, "Fair Value (Benjamin Graham)"] = bg_mos_fair_value
            df.loc[ticker, "Fair Value (Peter Lynch)"] = pl_fair_value
            df.loc[ticker, "PEGY ratio"] = pegy_ratio

        for ticker in wo_cashflow:
            df.loc[ticker, "Ticker"] = ticker.upper()
            df.loc[ticker, "Current Price"] = self.get_current_price(ticker)
            df.loc[ticker, "PEG"] = "-"
            df.loc[ticker, "Fair Value (Discounted Cash Flow)"] = "-"
            df.loc[ticker, "Fair Value (Benjamin Graham)"] = "-"
            df.loc[ticker, "Fair Value (Peter Lynch)"] = "-"
            df.loc[ticker, "PEGY ratio"] = "-"

        return df, invalid

    def get_growth_estimate(self, ticker):
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
        }
        url = f"https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
        soup = BeautifulSoup(requests.get(url, headers=headers).content, "html5lib")

        # find correct table:
        table = soup.select_one('table:has(th:-soup-contains("Growth Estimate"))')

        # find correct row:
        row = table.select_one('tr:-soup-contains("Next 5 Years (per annum)")')

        # select correct cell
        growth_estimate_5y = row.select("td")[1].text
        return float(growth_estimate_5y[:-1])

    def peter_lynch(self, ticker):
        # Peter Lynch's formula
        # Peter Lynch Fair Value = {Net Income Growth Rate} * {Earnings per Share} * {PEG}
        # https://valueinvesting.io/fair-value-calculator

        eps = yf.Ticker(ticker).info.get("trailingEps")
        eps = max(0, eps)
        net_income = yf.Ticker(ticker).get_financials().loc["NetIncome"]
        net_income = net_income.sort_index()
        avg_net_income_growth = net_income.pct_change().mean() * 100
        avg_net_income_growth = max(5.0, avg_net_income_growth)
        avg_net_income_growth = min(20.0, avg_net_income_growth)

        peg_ratio = yf.Ticker(ticker).info.get("pegRatio")
        adjusted_peg_ratio = 1.0  # Peter Lynch: fair P/E ratio of the growth stock is equal to its earnings growth rate.
        fair_value = avg_net_income_growth * eps * adjusted_peg_ratio
        fair_value = round(fair_value, 2)
        return fair_value, peg_ratio

    def pegy(self, ticker):
        # PEGY Ratio
        # PEGY value = P/E Ratio / (EPS Growth Rate + Dividend Yield)
        # https://www.investopedia.com/terms/p/pegyratio.asp

        # get dividend yield
        dividend_yield = yf.Ticker(ticker).info.get("dividendYield", 0)

        # get pe ratio
        pe_ratio = yf.Ticker(ticker).info.get("trailingPE", 0)

        # get future eps
        future_eps = yf.Ticker(ticker).info.get("forwardEps")

        pegy = pe_ratio / (future_eps + dividend_yield)
        pegy = round(pegy, 2)
        return pegy

    def benjamin_graham(self, ticker, margin_of_safety=0.5, pe_base=8.5):
        # Benjamin Graham's formula
        # V = EPS * (8.5 + 2g)
        # https://www.oldschoolvalue.com/stock-valuation/benjamin-graham-formula/

        try:
            growth_rate = self.get_growth_estimate(ticker)
        except Exception as e:
            print("Error:", e)
            growth_rate = 0.05

        # get EPS
        eps = yf.Ticker(ticker).info.get("trailingEps")

        # get fair value
        fair_value = eps * (pe_base + 2 * growth_rate)
        fair_value = round(fair_value, 2)

        # get margin of safety
        mos_fair_value = margin_of_safety * fair_value
        mos_fair_value = round(mos_fair_value, 2)

        return fair_value, mos_fair_value

    def discounted_cashflow(
        self,
        ticker,
        margin_of_safety=0.5,
        terminal_growth=0.02,
        discount_rate=0.1,
        conservative_cagr_factor=0.8,
        decreasing_fcf=False,
    ):
        # Discounted Cashflow
        # DCF = CF1 / (1 + r) + CF2 / (1 + r)^2 + ... + CFn / (1 + r)^n
        # https://www.investopedia.com/terms/d/dcf.asp

        yf_financials = yf.Ticker(ticker)

        # convert to USD
        financial_currency = yf_financials.info.get("financialCurrency")
        exchange_rate = CurrencyRates().get_rate(financial_currency, "USD")

        # get outstanding shares
        shares_outstanding = yf_financials.info.get("sharesOutstanding")

        # get current price
        current_price = yf_financials.info.get("currentPrice")

        # get cashflows
        cashflows_stmt = yf_financials.get_cashflow()
        if cashflows_stmt.empty:
            return current_price, None, None
        df_fcf = cashflows_stmt.loc["FreeCashFlow"]
        df_fcf = df_fcf.sort_index()
        df_fcf = df_fcf * exchange_rate

        # get conservative cagr
        cagr = (df_fcf.iloc[-1] / df_fcf.iloc[0]) ** (1 / len(df_fcf)) - 1
        # decreasing_fcf = df_fcf.iloc[-1] < df_fcf.iloc[0]
        if cagr.imag != 0:
            cagr = cagr.real
        conservative_cagr = cagr * conservative_cagr_factor

        # forecasted cashflow
        forecasted_cf = df_fcf.iloc[-1] * (1 + conservative_cagr) ** np.arange(1, 11)

        # get terminal value
        terminal_value = (
            forecasted_cf[-1]
            * (1 + terminal_growth)
            / (discount_rate - terminal_growth)
        )

        # get fair value
        fair_value = (forecasted_cf.sum() + terminal_value) / shares_outstanding

        # get fair value with safety margin
        mos_fair_value = margin_of_safety * fair_value
        mos_fair_value = round(mos_fair_value, 2)

        return fair_value, mos_fair_value


if __name__ == "__main__":
    tickers = ["AMZN", "AAPL", "MSFT", "PDD", "GOOGL", "BABA", "D05.SI", "TSLA"]
    model = Model()
    df = model.get_valuations(tickers)
