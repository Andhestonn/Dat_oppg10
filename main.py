import csv
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from les_data import les_stasjoner

MAPPE = Path(__file__).resolve().parent


def grupper_per_maaned(data):
    maaneder = {}

    for dag in data:
        dato = dag["dato"]
        nokkel = (dato.year, dato.month)

        if nokkel not in maaneder:
            maaneder[nokkel] = []

        maaneder[nokkel].append(dag)

    return maaneder


def grupper_vind_per_maaned(data):
    maaneder = {}

    for dag in data:
        maaned = dag["dato"].month

        if maaned not in maaneder:
            maaneder[maaned] = []

        if dag["vind"] is not None:
            maaneder[maaned].append(dag["vind"])
    return maaneder


def skifore(data, aar):
    antall = 0
    gyldige_dager = 0
    start = datetime(aar - 1, 11, 1)
    slutt = datetime(aar, 5, 31)
    for dag in data:
        if start <= dag["dato"] <= slutt:
            if dag["sno"] is not None:
                gyldige_dager += 1

                if dag["sno"] >= 20:
                    antall += 1
    totale_dager = (slutt - start).days + 1

    if gyldige_dager >= totale_dager / 2:
        return antall

    return None


def sommerdager(data, aar):
    sommer = 0
    hoysommer = 0
    trope = 0
    for dag in data:
        if dag['dato'].year == aar and dag['maks'] is not None:
            if dag['maks'] > 20:
                sommer += 1
            if dag['maks'] > 25:
                hoysommer += 1
            if dag['maks'] > 30:
                trope += 1
    return sommer, hoysommer, trope


def gjennomsnitt_temp(data, aar):
    temperaturer = []

    for dag in data:
        if dag["dato"].year == aar and dag["temp"] is not None:
            temperaturer.append(dag["temp"])

    if len(temperaturer) >= 300:
        return sum(temperaturer) / len(temperaturer)

    return None


def finn_median(verdier):
    sortert = sorted(verdier)
    antall = len(sortert)
    midten = antall // 2

    if antall % 2 == 1:
        return sortert[midten]
    else:
        return (sortert[midten - 1] + sortert[midten]) / 2


def main():
    stasjoner = les_stasjoner("stasjoner_mappe")

    data = stasjoner["oslo_blindern_1954_2025_med_makstemperatur"]

    grupper = grupper_per_maaned(data)
    statistikk = maanedsstatistikk(grupper)

    plott_maaneder(statistikk)
    plott_sommerdager(data)
    plott_gjennomsnitt(stasjoner)
    plott_vindstatistikk(data)
    plott_skisesonger(stasjoner)


def maanedsstatistikk(grupper):
    statistikk = {}

    for nokkel, dager in grupper.items():
        snoverdier = []
        vindverdier = []
        nedborverdier = []
        tempverdier = []

        for dag in dager:
            if dag["sno"] is not None:
                snoverdier.append(dag["sno"])

        for dag in dager:
            if dag["vind"] is not None:
                vindverdier.append(dag["vind"])

        for dag in dager:
            if dag["nedbor"] is not None:
                nedborverdier.append(dag["nedbor"])

        for dag in dager:
            if dag["temp"] is not None:
                tempverdier.append(dag["temp"])

        statistikk[nokkel] = {
            "sno_max": max(snoverdier) if snoverdier else None,
            "vind_max": max(vindverdier) if vindverdier else None,
            "nedbor_total": sum(nedborverdier) if len(nedborverdier) > 20 else None,
            "temp_min": min(tempverdier) if tempverdier else None,
            "temp_max": max(tempverdier) if tempverdier else None
        }

    return statistikk


def plott_maaneder(statistikk):
    datoer = []
    sno = []
    nedbor = []
    vind = []
    temp_min = []
    temp_max = []

    for nokkel, verdier in sorted(statistikk.items()):
        aar, maaned = nokkel

        datoer.append(datetime(aar, maaned, 1))
        sno.append(verdier["sno_max"])
        nedbor.append(verdier["nedbor_total"])
        vind.append(verdier["vind_max"])
        temp_min.append(verdier["temp_min"])
        temp_max.append(verdier["temp_max"])

    fig, akser = plt.subplots(4, 1, figsize=(12, 7), sharex=True)

    akser[0].plot(datoer, sno)
    akser[0].set_ylabel("Snødybde (cm)")

    akser[1].plot(datoer, nedbor)
    akser[1].set_ylabel("Nedbør (mm)")

    akser[2].plot(datoer, vind)
    akser[2].set_ylabel("Vind (m/s)")

    akser[3].plot(datoer, temp_min)
    akser[3].plot(datoer, temp_max)
    akser[3].set_ylabel("Temperatur (°C)")

    for akse in akser:
        akse.grid(True)

    plt.tight_layout()
    plt.show()


def plott_sommerdager(data):
    aarstall = []
    sommer = []
    hoysommer = []
    trope = []

    for aar in range(1954, 2026):
        s, h, t = sommerdager(data, aar)

        aarstall.append(aar)
        sommer.append(s)
        hoysommer.append(h)
        trope.append(t)

    plt.plot(aarstall, sommer, label="Sommerdager >20°C")
    plt.plot(aarstall, hoysommer, label="Høysommerdager >25°C")
    plt.plot(aarstall, trope, label="Tropedager >30°C")

    plt.xlabel("År")
    plt.ylabel("Antall dager")
    plt.title("Sommerdager per år – Oslo Blindern")
    plt.legend()
    plt.grid(True)
    plt.show()


def plott_gjennomsnitt(stasjoner):
    plt.figure(figsize=(12, 6))

    for navn, data in stasjoner.items():
        aarstall = sorted({dag["dato"].year for dag in data})
        gjennomsnitt = []

        for aar in aarstall:
            gjennomsnitt.append(gjennomsnitt_temp(data, aar))

        kort_navn = navn.split("_1954")[0].split("_2014")[0]
        plt.plot(aarstall, gjennomsnitt, label=kort_navn)

    plt.xlabel("År")
    plt.ylabel("Gjennomsnittstemperatur (°C)")
    plt.title("Årlig gjennomsnittstemperatur")
    plt.legend()
    plt.grid(True)
    plt.show()


def plott_vindstatistikk(data):
    grupper = grupper_vind_per_maaned(data)

    maaneder = []
    minimum = []
    medianer = []
    maksimum = []

    for maaned, vind in sorted(grupper.items()):
        if vind:
            maaneder.append(maaned)
            minimum.append(min(vind))
            medianer.append(finn_median(vind))
            maksimum.append(max(vind))

    plt.figure(figsize=(10, 5))

    plt.plot(maaneder, minimum, label="Minimum")
    plt.plot(maaneder, medianer, label="Median")
    plt.plot(maaneder, maksimum, label="Maksimum")

    plt.xlabel("Måned")
    plt.ylabel("Vindstyrke (m/s)")
    plt.xticks(range(1, 13))
    plt.title("Vindstatistikk per måned - Oslo Blindern")
    plt.legend()
    plt.grid(True)
    plt.show()


def plott_skisesonger(stasjoner):
    plt.figure(figsize=(12, 6))

    for navn, data in stasjoner.items():
        aarstall = []
        skidager = []

        for aar in sorted({dag["dato"].year for dag in data}):
            resultat = skifore(data, aar)
            aarstall.append(aar)
            skidager.append(resultat)

        kort_navn = navn.split("_1954")[0].split("_2014")[0]

        plt.plot(aarstall, skidager, label=kort_navn,
                 linewidth=1, alpha=0.75)

    plt.xlabel("Skisesong (sluttår)")
    plt.ylabel("Antall skidager")
    plt.title("Skisesonger - sammenligning av værstasjoner")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
