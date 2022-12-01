from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from beamCalculations.app.app import calcZL


def BeamCalc(request):
    data = {
        'result': 0,
        'category': 0
    }
    if request.is_ajax():
        value_zl = int(request.POST.get('valueZL'))
        value_h = float(request.POST.get('valueH'))
        value_count = int(request.POST.get('valueCount'))
        value_first = float(request.POST.get('valueFirst'))

        data = calcZL(value_zl, value_h, value_count, value_first)
        return JsonResponse(data)
    return render(request, 'calc/kategoria_obiektu.html', data)
