from webapplication.models import Invest
from django.http import JsonResponse

def getInvestAktiv(request):
    jahr = request.GET.get('jahr')
    #jahr = Invest.objects.values('jahr').filter(jahr=jahr)
    bereich = list(Invest.objects.values('bereich').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    team = list(Invest.objects.values('team').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    ou = list(Invest.objects.values('ou_id__ou').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_übrig = list(Invest.objects.values('investmittel_übrig').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_gesamt = list(Invest.objects.values('investmittel_gesamt').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_verausgabt = list(Invest.objects.values('investmittel_verausgabt').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_geplant = list(Invest.objects.values('investmittel_gesamt').filter(typ="Planung").filter(jahr=jahr).order_by("ou_id__ou"))
    response_data = {
        "ou":ou,
        "bereich":bereich,
        "team": team,
        "inv_gesamt":inv_gesamt,
        "inv_übrig":inv_übrig,
        "inv_geplant":inv_geplant,
        "inv_verausgabt":inv_verausgabt,
        "jahr": jahr
    }
    return JsonResponse(response_data)

def getInvestmittelplanung(request):
    jahr = request.GET.get('jahr')
    bereich = list(Invest.objects.values('bereich').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    team = list(Invest.objects.values('team').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    ou = list(Invest.objects.values('ou_id__ou').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    inv_gesamt = list(Invest.objects.values('investmittel_gesamt').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    inv_geplant = list(Invest.objects.values('investmittel_gesamt').filter(typ="Planung").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    summe_geplant_invest = 0.00
    percent = []
    inv_geplant_str = Invest.objects.values_list('investmittel_gesamt').filter(typ="Planung").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou")
    for inv in inv_geplant_str:
        summe_geplant_invest = summe_geplant_invest + float(str(inv).replace("(Decimal('", "").replace("'),)", ""))
    for inv in inv_geplant_str:
        try:
            percent.append(round((float(str(inv).replace("(Decimal('", "").replace("'),)", "")) / float(summe_geplant_invest)) * 100, 2))
        except ZeroDivisionError:
            percent.append(0.00)
    response_data = {
        "ou":ou,
        "bereich":bereich,
        "team": team,
        "inv_gesamt":inv_gesamt,
        "inv_geplant":inv_geplant,
        "percent": percent,
        "jahr": jahr
    }
    return JsonResponse(response_data)

def getInvestSoll(request):
    jahr = request.GET.get('jahr')
    bereich = list(Invest.objects.values('bereich').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    team = list(Invest.objects.values('team').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    ou = list(Invest.objects.values('ou_id__ou').filter(typ="Aktiv").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    inv_geplant = list(Invest.objects.values('investmittel_gesamt').filter(typ="Planung").filter(jahr=jahr).exclude(ou_id__ou=1).order_by("ou_id__ou"))
    response_data = {
        "ou":ou,
        "bereich":bereich,
        "team": team,
        "inv_geplant":inv_geplant,
        "jahr": jahr
    }
    return JsonResponse(response_data)

def getModifyInvest(request):
    jahr = request.GET.get('jahr')
    #jahr = Invest.objects.values('jahr').filter(jahr=jahr)
    bereich = list(Invest.objects.values('bereich').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    team = list(Invest.objects.values('team').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    ou = list(Invest.objects.values('ou_id__ou').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_übrig = list(Invest.objects.values('investmittel_übrig').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_gesamt = list(Invest.objects.values('investmittel_gesamt').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_verausgabt = list(Invest.objects.values('investmittel_verausgabt').filter(typ="Aktiv").filter(jahr=jahr).order_by("ou_id__ou"))
    inv_geplant = list(Invest.objects.values('investmittel_gesamt').filter(typ="Planung").filter(jahr=jahr).order_by("ou_id__ou"))
    response_data = {
        "ou":ou,
        "bereich":bereich,
        "team": team,
        "inv_gesamt":inv_gesamt,
        "inv_übrig":inv_übrig,
        "inv_geplant":inv_geplant,
        "inv_verausgabt":inv_verausgabt,
        "jahr": jahr
    }
    return JsonResponse(response_data)