from django.shortcuts import render
from .models import FinancialAnalysis

def finance_list(request):
    data = FinancialAnalysis.objects.filter(user=request.user)
    return render(request, "finance_list.html", {"data": data})
