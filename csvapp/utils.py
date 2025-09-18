import os
import pandas as pd
import pdfplumber
from django.conf import settings

def extract_pdf_to_csv(pdf_path):
    """
    Otevře PDF, vytáhne všechny tabulky a uloží je jako CSV do media/csv/.
    Vrátí absolutní cestu k CSV souboru nebo None, pokud nic nenačte.
    """
    all_rows = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        cleaned_row = [cell.strip() if cell else "" for cell in row]
                        cleaned_row.append(f"page {page_number}")  # debug info
                        all_rows.append(cleaned_row)

        if not all_rows:
            print(f"⚠️ V PDF {pdf_path} nebyly nalezeny žádné tabulky.")
            return None

        # vytvoření DataFrame
        df = pd.DataFrame(all_rows)

        # složka pro CSV
        csv_dir = os.path.join(settings.MEDIA_ROOT, "csv")
        os.makedirs(csv_dir, exist_ok=True)

        # cesta k výslednému CSV
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        csv_path = os.path.join(csv_dir, f"{base_name}.csv")

        # uložení CSV
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        print(f"✅ CSV vygenerováno: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Chyba při extrakci PDF {pdf_path}: {e}")
        return None
