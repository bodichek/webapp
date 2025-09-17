import pdfplumber
import pandas as pd
from decimal import Decimal

def extract_tables(pdf_file):
    """
    Extrahuje tabulky z PDF souboru pomocí pdfplumber.
    pdf_file může být path nebo file-like objekt (InMemoryUploadedFile).
    """
    tables = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            found_tables = page.extract_tables()
            if found_tables:
                tables.extend(found_tables)

    # Pokud byly nalezeny tabulky
    if tables:
        # Pro jednoduchost vezmeme všechny tabulky a složíme je pod sebe
        df_list = []
        for table in tables:
            df_tmp = pd.DataFrame(table[1:], columns=table[0])
            df_list.append(df_tmp)
        df = pd.concat(df_list, ignore_index=True)
        return df

    return None

def parse_decimal(value_str):
    """
    Převede string na Decimal, očistí od mezer a převede čárky na tečky.
    """
    if not value_str or value_str.strip() == '':
        return None

    clean_str = value_str.replace(' ', '').replace(',', '.')
    try:
        return Decimal(clean_str)
    except:
        return None
