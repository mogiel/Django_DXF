import os
from datetime import datetime
import ezdxf
import ezdxf.math
from math import pi
import math
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

def home(request):
    return render(request, 'home.html')


def beam(request):
    return render(request, 'beam.html')


def author(request):
    return render(request, 'author.html')


def download_dxf_beam(request):
    nazwaBelki = request.POST['namePosition']
    # rozpietoscBelki
    rB = float(request.POST['DB'])
    # wysokoscBelki
    wB = float(request.POST['WB'])
    # szerokoscBelki
    sB = float(request.POST['SB'])
    # szerokoscPodporyLewej
    sPL = float(request.POST['SPL'])
    # szerokoscPodporyPrawej
    sPP = float(request.POST['SPP'])
    # srednicaPretaGlownegoGornego
    sPGG = float(request.POST['SPG'])
    # srednicaPretaGlownegoDolnego
    sPGD = float(request.POST['SPD'])
    # średnicaStrzemienia
    sS = float(request.POST['SPS'])
    # otulinaGorna
    oG = float(request.POST['oG'])
    # otulinaDolna
    oD = float(request.POST['oD'])
    # otulinaBocznaLewa
    oBL = float(request.POST['oBL'])
    # otulinaBocznaPrawa
    oBP = float(request.POST['oBP'])
    # otulinaBocznaLewaPrzekroj
    oBLP = float(request.POST['oBLP'])
    # otulinaBocznaPrawaPrzekroj
    oBPP = float(request.POST['oBPP'])
    # zasięgStrzemionPIerszegorzęduLewa
    zSPL = float(request.POST['zSPL'])
    # zasięgStrzemionPIerszegorzęduPrawa
    zSPP = float(request.POST['zSPP'])
    # rozstawStrzemionPIerszegorzęduLewa
    rSPL = float(request.POST['rSPL'])
    # rozstawStrzemionPIerszegorzęduPrawa
    rSPP = float(request.POST['rSPP'])

    drawing = ezdxf.new(dxfversion='R2018', setup=["linetypes"])
    drawing.header['$LTSCALE'] = 50
    drawing.header['$INSUNITS'] = 4
    drawing.header['$MEASUREMENT'] = 1

    msp = drawing.modelspace()

    drawing.layers.new('KONEC-Obrys', dxfattribs={'color': 3})
    drawing.layers.new('KONEC-Prety', dxfattribs={'color': 1})
    drawing.layers.new('KONEC-Strzemiona', dxfattribs={'color': 6})
    drawing.layers.new('KONEC-Kreskowanie', dxfattribs={'color': 7})
    drawing.layers.new('KONEC-Wymiary', dxfattribs={'color': 4})
    drawing.layers.new('KONEC-Przerywana', dxfattribs={'color': 8, 'linetype': 'DASHED'})

    drawing.styles.new('KONEC-TEKST', dxfattribs={'font': 'Arial.ttf'})

    drawing.dimstyles.new('KONEC_1_20',
                          dxfattribs={'dimjust': 0, 'dimscale': 20, 'dimblk': 'OBLIQUE', 'dimtxsty': 'KONEC-TEKST'})

    # wyokragleniePretagornego
    if sPGG <= 16:
        wPG = sPGG * 2.5
    else:
        wPG = sPGG * 4.0
    # strzalkaWyoblenia
    sW1 = ezdxf.math.arc_to_bulge((wPG, 0), pi, pi / 2, wPG)
    sW = -1 / sW1[2]
    # Obrys belki
    pointsObrys = [(0, 0), (sPL, 0), ((sPL + rB), 0), ((sPL + rB + sPP), 0), ((sPL + rB + sPP), wB), (0, wB)]
    msp.add_lwpolyline(pointsObrys, dxfattribs={'closed': True, 'layer': 'KONEC-Obrys'})

    # Geometria pręta górnego
    pointsPretG = [((oBL + 0.5 * sPGG), oD, sPGG, sPGG),
                   ((oBL + 0.5 * sPGG), (wB - oG - sS - 0.5 * sPGG - wPG), sPGG, sPGG, sW),
                   ((oBL + 0.5 * sPGG + wPG), (wB - oG - sS - 0.5 * sPGG), sPGG, sPGG),
                   ((sPL + rB + sPP - oBP - 0.5 * sPGG - wPG), (wB - oG - sS - 0.5 * sPGG), sPGG, sPGG, sW),
                   ((sPL + rB + sPP - oBP - 0.5 * sPGG), (wB - oG - sS - 0.5 * sPGG - wPG), sPGG, sPGG),
                   ((sPL + rB + sPP - oBP - 0.5 * sPGG), oD)]
    msp.add_lwpolyline(pointsPretG, dxfattribs={'layer': 'KONEC-Prety'})
    # Geometria pręta dolnego
    pointsPretD = [(oBL, (oD + sS + 0.5 * sPGD), sPGD, sPGD), (sPL + rB + sPP - oBP, (oD + sS + 0.5 * sPGD))]
    msp.add_lwpolyline(pointsPretD, dxfattribs={'layer': 'KONEC-Prety'})

    # strzemiona
    # punktyStrzemion
    pS = []

    rDS = math.floor(min(0.75 * wB * 0.9, 400) / 5) * 5

    oOP = rB - (math.ceil(zSPL / rSPL) * rSPL + math.ceil(zSPP / rSPP) * rSPP + math.floor(
        (rB - (math.ceil(zSPL / rSPL) * rSPL + math.ceil(zSPP / rSPP) * rSPP)) / rDS) * rDS)

    # print(oOP, 'start')
    while oOP > 60:
        rDS -= 5
        oOP = rB - (math.ceil(zSPL / rSPL) * rSPL + math.ceil(zSPP / rSPP) * rSPP + math.floor(
            (rB - (math.ceil(zSPL / rSPL) * rSPL + math.ceil(zSPP / rSPP) * rSPP)) / rDS) * rDS)
    if oOP > 60:
        while oOP > 60:
            rDS -= 5
            oOP = rB - (math.ceil(zSPL / rSPL) * rSPL + math.ceil(zSPP / rSPP) * rSPP + math.floor(
                (rB - (math.ceil(zSPL / rSPL) * rSPL + math.ceil(zSPP / rSPP) * rSPP)) / rDS) * rDS)

    for i in range(int(math.ceil(zSPL / rSPL) + 1)):
        pS.append(oOP / 2 + i * rSPL)

    ostatnieStrzemieLewa = pS[-1]

    for i in range(int(math.ceil(zSPP / rSPP) + 1)):
        pS.append(rB - oOP / 2 - i * rSPP)

    ostatnieStrzemiePrawa = pS[-1]

    for i in range(1, int((rB - ostatnieStrzemieLewa - (rB - ostatnieStrzemiePrawa)) / rDS)):
        pS.append(ostatnieStrzemieLewa + i * rDS)

    # ilośćRozstawuDrugiego Rzędu
    iRDR = math.ceil((ostatnieStrzemiePrawa - ostatnieStrzemieLewa) / rDS)

    for a in pS:
        pointsStrzemie = [((sPL + a), oD, sS, sS), ((sPL + a), (wB - oG))]
        msp.add_lwpolyline(pointsStrzemie, dxfattribs={'layer': 'KONEC-Strzemiona'})

    # podpory
    wysokosc_podpory = 200
    hatch1 = msp.add_hatch(dxfattribs={'layer': 'KONEC-Kreskowanie'})
    hatch1.set_pattern_fill('ANSI33', scale=20, color=-1)
    hatch1.paths.add_polyline_path(
        [(0, 0), (0, -wysokosc_podpory), (sPL, -wysokosc_podpory), (sPL, 0)]
    )

    hatch2 = msp.add_hatch(dxfattribs={'layer': 'KONEC-Kreskowanie'})
    hatch2.set_pattern_fill('ANSI31', scale=20, color=-1)
    hatch2.paths.add_polyline_path(
        [(sPL + rB, 0), (sPL + rB, -wysokosc_podpory), (sPL + rB + sPP, -wysokosc_podpory), (sPL + rB + sPP, 0)]
    )

    punkty_podpor = (0, sPL, sPL + rB, sPL + rB + sPP)
    for a in punkty_podpor:
        punkty = [(a, 0), (a, -wysokosc_podpory)]
        msp.add_lwpolyline(punkty, dxfattribs={'layer': 'KONEC-Obrys'})

    linia_1 = [(0 - 200, -wysokosc_podpory), (sPL + 200, -wysokosc_podpory)]
    msp.add_lwpolyline(linia_1, dxfattribs={'layer': 'KONEC-Przerywana'})
    linia_2 = [(sPL + rB - 200, -wysokosc_podpory), (sPL + rB + sPP + 200, -wysokosc_podpory)]
    msp.add_lwpolyline(linia_2, dxfattribs={'layer': 'KONEC-Przerywana'})

    # wymiarowanie
    dim1 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 200), p1=(0, -wysokosc_podpory), p2=(sPL, -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})
    dim2 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 200), p1=(sPL, -wysokosc_podpory),
                              p2=(sPL + rB, -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})
    dim3 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 200), p1=(sPL + rB, -wysokosc_podpory),
                              p2=(sPL + rB + sPP, -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})

    dim4 = msp.add_linear_dim(base=(-100, 0), p1=(0, 0), p2=(0, wB), angle=90,
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})

    # wymiarowanie strzemion
    dim5 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 100), p1=(sPL, -wysokosc_podpory),
                              p2=(sPL + pS[0], -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})

    pS.sort()

    dim6 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 100), p1=(sPL + pS[0], -wysokosc_podpory),
                              p2=(sPL + ostatnieStrzemieLewa, -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'},
                              text=f'{math.ceil(zSPL / rSPL)} x {rSPL} = <>')

    dim7 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 100), p1=(sPL + ostatnieStrzemieLewa, -wysokosc_podpory),
                              p2=(sPL + ostatnieStrzemiePrawa, -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'},
                              text=f'{iRDR} x {rDS} = <>')

    dim8 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 100), p1=(sPL + ostatnieStrzemiePrawa, -wysokosc_podpory),
                              p2=(sPL + pS[-1], -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'},
                              text=f'{math.ceil(zSPP / rSPP)} x {rSPP} = <>')

    dim9 = msp.add_linear_dim(base=(0, -wysokosc_podpory - 100), p1=(sPL + pS[-1], -wysokosc_podpory),
                              p2=(sPL + rB, -wysokosc_podpory),
                              dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})

    # przekrój
    startPrzekroj = sPL + rB + sPP + 500

    pointsPrzekroj = [(startPrzekroj, 0), (startPrzekroj + sB, 0), (startPrzekroj + sB, wB), (startPrzekroj, wB)]
    msp.add_lwpolyline(pointsPrzekroj, dxfattribs={'closed': True, 'layer': 'KONEC-Obrys'})

    # przekrój strzemie
    # wyokragleniePretagornego
    wPS = 0
    if sS <= 16:
        wPS = sS * 2.5
    else:
        wPS = sS * 4.0

    zakotwieniePretaStrzemienia = 80
    # strzalkaWyoblenia
    sW1 = ezdxf.math.arc_to_bulge((wPG, 0), pi, pi / 2, wPG)
    sW = -1 / sW1[2]

    # Geometria strzemienia
    pointsStrzemiePrzekroj = [
        (startPrzekroj + oBLP + 0.5 * sS, wB - oG - 0.5 * sS - wPS - zakotwieniePretaStrzemienia, sS, sS),
        (startPrzekroj + oBLP + 0.5 * sS, wB - oG - 0.5 * sS - wPS, sS, sS, sW),
        (startPrzekroj + oBLP + 0.5 * sS + wPS, wB - oG - 0.5 * sS, sS, sS),
        (startPrzekroj + sB - oBPP - 0.5 * sS - wPS, wB - oG - 0.5 * sS, sS, sS, sW),
        (startPrzekroj + sB - oBPP - 0.5 * sS, wB - oG - 0.5 * sS - wPS, sS, sS),
        (startPrzekroj + sB - oBPP - 0.5 * sS, oD + 0.5 * sS + wPS, sS, sS, sW),
        (startPrzekroj + sB - oBPP - 0.5 * sS - wPS, oD + 0.5 * sS, sS, sS),
        (startPrzekroj + oBLP + 0.5 * sS + wPS, oD + 0.5 * sS, sS, sS, sW),
        (startPrzekroj + oBLP + 0.5 * sS, oD + 0.5 * sS + wPS, sS, sS),
        (startPrzekroj + oBLP + 0.5 * sS, wB - oG - 0.5 * sS - wPS, sS, sS, sW),
        (startPrzekroj + oBLP + 0.5 * sS + wPS, wB - oG - 0.5 * sS, sS, sS),
        (startPrzekroj + oBLP + 0.5 * sS + wPS + zakotwieniePretaStrzemienia, wB - oG - 0.5 * sS, sS, sS)
    ]

    # print(msp.add_lwpolyline(pointsStrzemiePrzekroj).get_app_data('Length'))
    # print(sprawdzenie_dlugosci.get_contro)

    msp.add_lwpolyline(pointsStrzemiePrzekroj, dxfattribs={'layer': 'KONEC-Prety'})

    msp.add_circle([startPrzekroj + oBLP + 0.5 * sS + wPS, wB - oG - sS - 0.5 * sPGG], 0.5 * sPGG)
    # msp.add_hatch()

    hatch3 = msp.add_hatch(dxfattribs={'layer': 'KONEC-Kreskowanie'})
    path_hatch3 = hatch3.paths.add_edge_path()
    hatch3.set_solid_fill(color=-1)
    path_hatch3.add_arc(center=(startPrzekroj + oBLP + 0.5 * sS + wPS, wB - oG - sS - 0.5 * sPGG), radius=0.5 * sPGG)

    msp.add_circle([startPrzekroj + sB - oBPP - 0.5 * sS - wPS, wB - oG - sS - 0.5 * sPGG], 0.5 * sPGG)
    # msp.add_hatch()

    hatch3 = msp.add_hatch(dxfattribs={'layer': 'KONEC-Kreskowanie'})
    path_hatch3 = hatch3.paths.add_edge_path()
    hatch3.set_solid_fill(color=-1)
    path_hatch3.add_arc(center=(startPrzekroj + sB - oBPP - 0.5 * sS - wPS, wB - oG - sS - 0.5 * sPGG),
                        radius=0.5 * sPGG)

    msp.add_circle([startPrzekroj + oBLP + 0.5 * sS + wPS, oD + sS + 0.5 * sPGD], 0.5 * sPGD)

    hatch3 = msp.add_hatch(dxfattribs={'layer': 'KONEC-Kreskowanie'})
    path_hatch3 = hatch3.paths.add_edge_path()
    hatch3.set_solid_fill(color=-1)
    path_hatch3.add_arc(center=(startPrzekroj + oBLP + 0.5 * sS + wPS, oD + sS + 0.5 * sPGD), radius=0.5 * sPGD)

    msp.add_circle([startPrzekroj + sB - oBPP - 0.5 * sS - wPS, oD + sS + 0.5 * sPGD], 0.5 * sPGD)

    hatch3 = msp.add_hatch(dxfattribs={'layer': 'KONEC-Kreskowanie'})
    path_hatch3 = hatch3.paths.add_edge_path()
    hatch3.set_solid_fill(color=-1)
    path_hatch3.add_arc(center=(startPrzekroj + sB - oBPP - 0.5 * sS - wPS, oD + sS + 0.5 * sPGD), radius=0.5 * sPGD)

    dim10 = msp.add_linear_dim(base=(startPrzekroj, -wysokosc_podpory - 100), p1=(startPrzekroj, 0),
                               p2=(startPrzekroj + sB, 0),
                               dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})

    dim11 = msp.add_linear_dim(base=(startPrzekroj + sB + 200, 0), p1=(startPrzekroj + sB, 0),
                               p2=(startPrzekroj + sB, wB), angle=90,
                               dimstyle='KONEC_1_20', dxfattribs={'layer': 'KONEC-Wymiary'})

    czas = datetime.now().strftime("%y%m%d%H%M%S%f")
    filepath = f'download/Files/temp/{czas}.dxf'

    drawing.saveas(filepath)

    print(os.path.basename(filepath))

    Belka = f'{nazwaBelki}.dxf'

    with open(filepath, 'rt') as dxf_file:
        response = HttpResponse(dxf_file.read())
        response['Content-Disposition'] = 'attachment; filename=' + Belka
        return response
