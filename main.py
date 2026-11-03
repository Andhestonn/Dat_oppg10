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


def skifore(data, aar):
    antall = 0
    start = datetime(aar - 1, 11, 1)
    slutt = datetime(aar, 5, 31)
    for dag in data:
        if start <= dag['dato'] <= slutt:
            if dag['sno'] is not None and dag['sno'] >= 20:
                antall += 1
        return antall


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


def main():
    stasjoner = les_stasjoner("stasjoner_mappe")

    data = stasjoner["oslo_blindern_1954_2025_med_makstemperatur"]

    grupper = grupper_per_maaned(data)

    print(grupper[(2020, 1)][:2])


if __name__ == "__main__":
    main()
