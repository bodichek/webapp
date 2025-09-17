from django.http import HttpResponse
from parsing.utils import extract_tables

def export_csv(request):
    pdf_path = "sample.pdf"  # TODO: nahradit cestou k nahranému souboru
    df = extract_tables(pdf_path)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="output.csv"'
    df.to_csv(response, index=False)
    return response
