def calcZL(valueZL: int, valueH: float, valueCount: int, valueFirst: float):
    zl = int(valueZL)
    building_height = float(valueH)
    storey = int(valueCount)
    first_storey = float(valueFirst)
    grupa_wysokosciowa = str
    ostatnia = str

    if building_height <= 12.0 and storey <= 4:
        grupa_wysokosciowa = "Niski (N)"
        bu = 0
    elif building_height <= 25.0 and storey <= 9:
        grupa_wysokosciowa = "Średniowysokie (SW)"
        bu = 1
    elif building_height <= 55.0 and storey <= 18:
        grupa_wysokosciowa = "Wysokie (W)"
        bu = 2
    else:
        grupa_wysokosciowa = "Wysokościowe (WW)"
        bu = 3

    a = [["B", "B", "C", "D", "C"],
         ["B", "B", "B", "C", "B"],
         ["B", "B", "B", "B", "B"],
         ["A", "A", "A", "B", "A"]]

    if storey <= 2 and building_height < 12.0 and (zl == 1 or zl == 2 or zl == 3):
        if storey == 1 and first_storey <= 9.0:
            if zl == 1:
                ostatnia = "D"
            elif zl == 2:
                ostatnia = "D"
            elif zl == 3:
                ostatnia = "D"
            else:
                print("Nie moża obniżyć klasy.")
        elif storey == 2 and first_storey <= 9.0:
            if zl == 1:
                ostatnia = "C"
            elif zl == 2:
                ostatnia = "C"
            elif zl == 3:
                ostatnia = "D"
            else:
                print("Nie moża obniżyć klasy.")
        else:
            print("Coś poszło nie tak.")
    else:
        ostatnia = "-"

    spr = a[bu][zl - 1]

    result = f"Ketegoria obiektu: {spr}<br>Można obniżyć do klasy: {ostatnia}<br>Grupa wysokościowa: {grupa_wysokosciowa}"

    # if spr == "A":
    #     zmiana_tablicy = 1
    # elif spr == "B":
    #     zmiana_tablicy = 2
    # elif spr == "C":
    #     zmiana_tablicy = 3
    # elif spr == "D":
    #     zmiana_tablicy = 4
    # elif spr == "E":
    #     zmiana_tablicy = 5
    # else:
    #     zmiana_tablicy = 0
    category = spr if ostatnia == '-' else ostatnia
    data = {
        'result': result,
        'category': category
    }
    return data

# def calcPM(self):
#     e2 = self.PM_gestosc_obciazenia_ogniowego.text()
#     pm_gestosc_obciazenia_ogniowego=float(e2.replace(",","."))
#     f2 = self.PM_ilosc_kondygnacji.text()
#     pm_ilosc_kondygnacji=float(f2.replace(",","."))
#     g2 = self.PM_wysokosc_budynku.text()
#     pm_wysokosc_budynku=float(g2.replace(",","."))
#
#     if pm_ilosc_kondygnacji<2:
#         grupa_wysokosciowa_pm="Budynek o jednej kondygnacji(bez ograniczeń wysokośći)"
#         bu = 0
#     elif pm_wysokosc_budynku<12.0 and pm_ilosc_kondygnacji<5:
#         grupa_wysokosciowa_pm="Niski (N)"
#         bu = 1
#     elif pm_wysokosc_budynku<25.0 and pm_ilosc_kondygnacji<10:
#         grupa_wysokosciowa_pm="Średniowysokie (SW)"
#         bu = 2
#     elif pm_wysokosc_budynku<55.0 and pm_ilosc_kondygnacji<19:
#         grupa_wysokosciowa_pm="Wysokie (W)"
#         bu = 3
#     else:
#         grupa_wysokosciowa_pm="Wysokościowe (WW)"
#         bu = 4
#
#     a= [["E", "D", "C", "B", "B"],["D", "D", "C", "B", "B"],["C", "C", "C", "B", "B"],["B", "B", "B", "*", "*"],["A", "A", "A", "*", "*"]]
#     to=[["R 240", "R 30", "REI 120", "EI 120 (O<->I)", "EI 60", "RE 30"],["R 120", "R 30", "REI 60", "EI 60 (O<->I)", "EI 30 (4.)", "RE 30"],["R 60", "R 15", "REI 60", "EI 30 (O<->I)", "EI 15 (4.)", "RE 15"],["R 30", "(-)", "REI 30", "EI 30 (O<->I)", "(-)", "(-)"],["(-)", "(-)", "(-)", "(-)", "(-)", "(-)", ]]
#
#     if pm_gestosc_obciazenia_ogniowego<=500.0:
#         wgo=0
#     elif pm_gestosc_obciazenia_ogniowego<=1000.0:
#         wgo=1
#     elif pm_gestosc_obciazenia_ogniowego<=2000.0:
#         wgo=2
#     elif pm_gestosc_obciazenia_ogniowego<=4000.0:
#         wgo=3
#     else:
#         wgo=4
#     spr_pm=a[wgo][bu]
#
#     self.Wynik.setHtml(
#     '<p style="text-align:center;font-size:30px;color:green;">Kategoria obiektu: ' + spr_pm + '<p style="text-align:center;font-size:15px;color:black;">Grupa wysokościowa: ' + grupa_wysokosciowa_pm)
#     if spr_pm == "A":
#         zmiana_tablicy_pm = 1
#     elif spr_pm == "B":
#         zmiana_tablicy_pm = 2
#     elif spr_pm == "C":
#         zmiana_tablicy_pm = 3
#     elif spr_pm == "D":
#         zmiana_tablicy_pm = 4
#     elif spr_pm == "E":
#         zmiana_tablicy_pm = 5
#     else:
#         zmiana_tablic_pm = 0
#
#     self.Tablica.setCurrentIndex(zmiana_tablicy_pm)
