import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UploadedFile
from parsing.utils import extract_tables

@login_required(login_url="/login/")
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        year = request.POST.get("year")
        file_type = request.POST.get("file_type")

        # uložit PDF do media/pdf/
        saved_file = UploadedFile.objects.create(
            user=request.user,
            file=uploaded_file,
            year=year,
            file_type=file_type,
        )

        # cesta k souboru
        pdf_path = saved_file.file.path
        csv_path = os.path.join(settings.MEDIA_ROOT, "csv", f"{saved_file.id}.csv")

        # vytvořit složku pro CSV pokud neexistuje
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        try:
            parse_pdf_to_csv(pdf_path, csv_path)
            success = True
        except Exception as e:
            success = False
            error_message = str(e)

        return render(request, "upload.html", {
            "success": success,
            "error": error_message if not success else None,
        })

    return render(request, "upload.html")
