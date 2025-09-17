from django.shortcuts import render
from .utils import extract_tables, parse_decimal
from finance.models import FinancialAnalysis

def parse_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        year = request.POST.get("year")
        file_type = request.POST.get("file_type")

        # Zpracování PDF
        df = extract_tables(pdf_file)
        if df is not None:
            # projdeme řádky a uložíme do DB
            for _, row in df.iterrows():
                for col in df.columns:
                    value = parse_decimal(row[col])
                    if value is not None:
                        FinancialAnalysis.objects.create(
                            user=request.user,
                            year=year,
                            file_type=file_type,
                            key=col,
                            value=value,
                        )

            return render(request, "parsing/success.html", {"year": year, "file_type": file_type})

        return render(request, "parsing/upload.html", {"error": "Nepodařilo se načíst tabulky z PDF"})

    return render(request, "parsing/upload.html")
