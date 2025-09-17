import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from .forms import CompanyForm, ContactPersonForm
from .models import Company, ContactPerson


# ------------------------------------------------
# CREATE / UPDATE company for current user
# ------------------------------------------------
@login_required
def company_create(request):
    """Umožní uživateli vytvořit nebo editovat vlastní firmu a kontaktní osobu."""
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        company = None

    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        contact_form = ContactPersonForm(request.POST)

        if form.is_valid() and contact_form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()

            contact = contact_form.save(commit=False)
            contact.company = company
            contact.save()

            return redirect("company_detail")
    else:
        form = CompanyForm(instance=company)
        contact_form = ContactPersonForm()

    return render(request, "company/company_form.html", {
        "form": form,
        "contact_form": contact_form
    })


# ------------------------------------------------
# DETAIL – pro přihlášeného uživatele
# ------------------------------------------------
@login_required
def company_detail(request):
    """Detail firmy přihlášeného uživatele."""
    company = Company.objects.filter(user=request.user).first()
    if not company:
        return redirect("company_create")   # 👈 správně, ne company_new

    contact_persons = ContactPerson.objects.filter(company=company)
    return render(request, "company/detail.html", {
        "company": company,
        "contacts": contact_persons
    })


# ------------------------------------------------
# DETAIL – podle ID (např. pro admina)
# ------------------------------------------------
@login_required
def company_detail_by_id(request, pk):
    """Detail firmy podle ID (pro admina / kouče)."""
    company = get_object_or_404(Company, pk=pk)
    contact_persons = ContactPerson.objects.filter(company=company)
    return render(request, "company/detail.html", {
        "company": company,
        "contacts": contact_persons
    })


# ------------------------------------------------
# LIST všech firem (pro admina)
# ------------------------------------------------
class CompanyListView(ListView):
    model = Company
    template_name = "company/company_list.html"
    context_object_name = "companies"


# ------------------------------------------------
# FETCH ARES data
# ------------------------------------------------
def fetch_company_data(request):
    """Načte data o firmě z ARES (MFČR) podle IČO."""
    ico = request.GET.get("ico")
    if not ico:
        return JsonResponse({"error": "IČO is required"}, status=400)

    url = f"https://wwwinfo.mfcr.cz/cgi-bin/ares/darv_bas.cgi?ico={ico}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
    except requests.RequestException:
        return JsonResponse({"error": "Nepodařilo se kontaktovat ARES API"}, status=500)

    try:
        root = ET.fromstring(r.content)
        ns = {"are": "http://wwwinfo.mfcr.cz/ares/xml_doc/schemas/ares/ares_answer_basic/v_1.0.0"}

        # název firmy
        name = root.find(".//are:OF", ns)
        # adresa – ulice + číslo
        street = root.find(".//are:NU", ns)
        house_number = root.find(".//are:CO", ns)
        # město
        city = root.find(".//are:N", ns)
        # PSČ
        postal_code = root.find(".//are:PSC", ns)

        data = {
            "ico": ico,
            "name": name.text if name is not None else "",
            "address": f"{street.text} {house_number.text}" if street is not None and house_number is not None else "",
            "city": city.text if city is not None else "",
            "postal_code": postal_code.text if postal_code is not None else "",
        }
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": f"Chyba při parsování XML: {str(e)}"}, status=500)
