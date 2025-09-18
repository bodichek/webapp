import os
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.files import File
from .models import FinancialFile, FinancialRow
from csvapp.utils import extract_pdf_to_csv
from .utils.calculations import compute_financials, compute_growth


YEARS = [2025, 2024, 2023, 2022, 2021]


# 🔹 uloží data z CSV do tabulky FinancialRow
@login_required
def save_csv_to_db(file_obj, year, user):
    try:
        df = pd.read_csv(file_obj.csv_file.path, sep=";")
    except Exception:
        df = pd.read_csv(file_obj.csv_file.path, sep=",")

    print(">>> Sloupce CSV:", df.columns.tolist())

    line_col = [c for c in df.columns if "řádku" in c.lower() or "číslo" in c.lower()]
    value_col = [c for c in df.columns if "Netto" in c]
    desc_col = [c for c in df.columns if "Označení" in c or "Popis" in c]

    if not line_col or not value_col:
        print("⚠️ CSV nemá očekávané sloupce:", df.columns)
        return

    line_col, value_col = line_col[0], value_col[0]
    desc_col = desc_col[0] if desc_col else None

    FinancialRow.objects.filter(file=file_obj).delete()

    for _, row in df.iterrows():
        if pd.notnull(row[line_col]):
            FinancialRow.objects.create(
                user=user,
                file=file_obj,
                year=year,
                line=str(row[line_col]).strip(),
                description=row[desc_col] if desc_col else "",
                value=float(row[value_col]) if pd.notnull(row[value_col]) else 0.0,
            )


# 🔹 nahrání PDF + uložení do DB
@login_required
def upload_files(request):
    if request.method == "POST":
        file_type = request.POST.get("file_type")
        year = int(request.POST.get("year", 0))
        uploaded = request.FILES.get("file")

        if not uploaded:
            messages.error(request, "Žádný soubor nebyl nahrán.")
            return redirect("upload_files")

        f, created = FinancialFile.objects.update_or_create(
            user=request.user, year=year, file_type=file_type,
            defaults={"file": uploaded}
        )

        csv_path = extract_pdf_to_csv(f.file.path)
        if csv_path:
            with open(csv_path, "rb") as f_csv:
                f.csv_file.save(os.path.basename(csv_path), File(f_csv), save=True)
            save_csv_to_db(f, year, request.user)

        messages.success(request, f"Soubor {file_type.upper()} {year} byl uložen.")
        return redirect("upload_files")

    uploaded = FinancialFile.objects.filter(user=request.user)
    context = {
        "years": YEARS,
        "rozvaha": {f.year: f for f in uploaded.filter(file_type="rozvaha")},
        "vysledovka": {f.year: f for f in uploaded.filter(file_type="vysledovka")},
    }
    return render(request, "files/upload.html", context)


# 🔹 seznam souborů
@login_required
def file_list(request):
    files = FinancialFile.objects.filter(user=request.user).order_by("-year", "file_type")
    return render(request, "files/file_list.html", {"files": files})


# 🔹 mazání souboru
@login_required
def file_delete(request, pk):
    file = get_object_or_404(FinancialFile, pk=pk)
    if file.user != request.user:
        return HttpResponseForbidden("Nemáš oprávnění mazat tento soubor.")

    if request.method == "POST":
        file.file.delete(save=False)
        if file.csv_file:
            file.csv_file.delete(save=False)
        file.delete()
        messages.success(request, f"Soubor {file.file.name} byl smazán.")
        return redirect("file_list")

    messages.error(request, "Mazání je povoleno pouze metodou POST.")
    return redirect("file_list")


# 🔹 zobrazení dat z DB
@login_required
def show_data(request):
    user = request.user
    files = FinancialFile.objects.filter(user=user).order_by("-year", "file_type")
    tables = []

    for f in files:
        rows = FinancialRow.objects.filter(file=f).order_by("line")
        if rows.exists():
            tables.append({
                "title": f"{f.get_file_type_display()} – {f.year}",
                "headers": ["Řádek", "Popis", "Hodnota"],
                "rows": [[r.line, r.description, r.value] for r in rows],
            })
        else:
            tables.append({
                "title": f"{f.get_file_type_display()} – {f.year}",
                "error": "⚠️ Žádná data nebyla uložena do tabulky FinancialRow."
            })

    return render(request, "files/show_data.html", {"tables": tables})


# 🔹 pomocná funkce pro dashboard
def get_df_from_db(user, year):
    rows = FinancialRow.objects.filter(user=user, year=year)
    data = {"Line": [], str(year): []}
    for r in rows:
        data["Line"].append(r.line)
        data[str(year)].append(r.value)
    return pd.DataFrame(data)


# 🔹 dashboard s metrikami
@login_required
def dashboard(request):
    user = request.user
    files = FinancialFile.objects.filter(user=user).order_by("year")

    metrics_by_year = {}
    for f in files:
        df = get_df_from_db(user, f.year)
        if not df.empty:
            metrics = compute_financials(df, f.year)
            metrics_by_year[f.year] = metrics

    growth = compute_growth(metrics_by_year)

    years = sorted(metrics_by_year.keys())
    chart_data = {
        "years": years,
        "Revenue": [metrics_by_year[y]["Revenue"] for y in years] if years else [],
        "COGS": [metrics_by_year[y]["COGS"] for y in years] if years else [],
        "Gross Margin %": [metrics_by_year[y]["Gross Margin %"] for y in years] if years else [],
        "Operating Profit %": [metrics_by_year[y]["Operating Profit %"] for y in years] if years else [],
        "Net Profit %": [metrics_by_year[y]["Net Profit %"] for y in years] if years else [],
    }

    growth_years = sorted(growth.keys())
    growth_data = {
        "years": growth_years,
        "Revenue Growth %": [growth[y]["Revenue Growth %"] for y in growth_years] if growth_years else [],
        "COGS Growth %": [growth[y]["COGS Growth %"] for y in growth_years] if growth_years else [],
        "Overheads Growth %": [growth[y]["Overheads Growth %"] for y in growth_years] if growth_years else [],
    }

    return render(request, "files/dashboard.html", {
        "metrics_by_year": metrics_by_year,
        "growth": growth,
        "chart_data": chart_data,
        "growth_data": growth_data,
    })

from .models import FinancialAnalysis

def save_analysis(user, year, file_type, metrics):
    # smaž staré výpočty pro tento rok/uživatele/typ
    FinancialAnalysis.objects.filter(user=user, year=year, file_type=file_type).delete()

    # ulož všechny metriky
    rows = [
        FinancialAnalysis(
            user=user,
            year=year,
            file_type=file_type,
            key=k,
            value=v if v is not None else 0.0,
        )
        for k, v in metrics.items()
    ]
    FinancialAnalysis.objects.bulk_create(rows)
