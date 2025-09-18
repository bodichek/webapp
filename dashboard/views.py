from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from filesapp.models import FinancialAnalysis   # ✅ správně

@login_required(login_url="/login/")   # 👈 přesměruje nepřihlášeného na login
def dashboard(request):
    data = FinancialAnalysis.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"data": data})