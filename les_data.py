import csv
from datetime import datetime, timedelta
from pathlib import Path

MAPPE = Path(__file__).resolve().parent


def til_tall(tekst):
    if tekst == '' or tekst == '-':
        return None
    return float(tekst.replace(',', '.'))


def les_fil(filsti):
    data = []
    with open(filsti, encoding='utf-8-sig') as fil:
        leser = csv.DictReader(fil, delimiter=';')
        for rad in leser:
            dato_tekst = rad.get('Tid(norsk normaltid)')
            if not dato_tekst:
                continue
            dag = {
                'dato': datetime.strptime(dato_tekst, '%d.%m.%Y'),
                'maks': til_tall(rad.get('Maksimumstemperatur (døgn)', '')),
                'temp': til_tall(rad.get('Middeltemperatur (døgn)', '')),
                'nedbor': til_tall(rad.get('Nedbør (døgn)', '')),
                'vind': til_tall(rad.get('Høyeste middelvind (døgn)', '')),
                'sno': til_tall(rad.get('Snødybde', ''))
            }
            data.append(dag)
    data.sort(key=lambda dag: dag["dato"])
    return data


def les_stasjoner(stasjoner_mappe):
    stasjoner = {}

    print("Looking in:", (MAPPE / stasjoner_mappe).resolve())

    for fil in (MAPPE / stasjoner_mappe).glob("*.csv"):
        print("Found:", fil.name)
        stasjonsnavn = fil.stem
        stasjoner[stasjonsnavn] = les_fil(fil)

    return stasjoner
