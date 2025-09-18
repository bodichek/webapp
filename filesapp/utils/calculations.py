import pandas as pd

def compute_financials(df: pd.DataFrame, year: int):
    """
    df: DataFrame, kde 'Line' obsahuje čísla řádků (např. '01', '02', '04', ...)
        a sloupce jsou roky (např. '2023', '2024')
    year: rok, pro který počítáme
    """
    year_col = str(year)

    def get(code):
        try:
            return float(df.loc[df["Line"].astype(str) == code, year_col].values[0])
        except IndexError:
            return 0.0

    # --- Výsledovka ---
    revenue = get("01") + get("02")
    cogs = get("04") + get("05")
    gross_margin = revenue - cogs
    gross_margin_pct = gross_margin / revenue * 100 if revenue else 0

    overheads = (get("12") + get("13")) + get("16") + get("17") + get("18")
    operating_profit = gross_margin - overheads
    operating_profit_pct = operating_profit / revenue * 100 if revenue else 0

    # EBIT – varianta B
    ebit = (revenue + get("15")) - (get("04") + get("05") + get("12") +
                                    get("13") + get("16") + get("17") + get("18"))

    # EBT
    ebt = ebit + (get("20") - get("21"))

    # Net Profit
    net_profit = ebt - get("40")
    net_profit_pct = net_profit / revenue * 100 if revenue else 0

    return {
        "year": year,
        "Revenue": revenue,
        "COGS": cogs,
        "Gross Margin": gross_margin,
        "Gross Margin %": gross_margin_pct,
        "Overheads": overheads,
        "Operating Profit": operating_profit,
        "Operating Profit %": operating_profit_pct,
        "EBIT": ebit,
        "EBT": ebt,
        "Net Profit": net_profit,
        "Net Profit %": net_profit_pct,
    }


def compute_growth(metrics_by_year):
    """
    metrics_by_year: dict {year: metrics_dict}
    Vrací meziroční růstové ukazatele.
    """
    growth = {}
    years = sorted(metrics_by_year.keys())
    for i in range(1, len(years)):
        y, prev_y = years[i], years[i-1]
        m, pm = metrics_by_year[y], metrics_by_year[prev_y]

        def growth_pct(curr, prev):
            return ((curr - prev) / prev * 100) if prev else 0

        growth[y] = {
            "Revenue Growth %": growth_pct(m["Revenue"], pm["Revenue"]),
            "COGS Growth %": growth_pct(m["COGS"], pm["COGS"]),
            "Overheads Growth %": growth_pct(m["Overheads"], pm["Overheads"]),
            "Gross Margin %": m["Gross Margin %"],
            "Operating Profit %": m["Operating Profit %"],
            "Net Profit %": m["Net Profit %"],
        }
    return growth
