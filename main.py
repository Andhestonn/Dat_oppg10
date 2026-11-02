import csv
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt


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
    return data


def les_stasjoner(stasjoner_mappe):
    stasjoner = {}
    for fil in Path(stasjoner_mappe).glob("*.csv"):
        stasjonsnavn = fil.stem
        stasjoner[stasjonsnavn] = les_fil(fil)

    return stasjoner


stasjoner = {
    "oslo_blindern": [{"dato", "temperatur", "nedbor"}],
    "roeros": [{"dato", "temperatur", "nedbor"}],
    "sinnes": [{"dato", "temperatur", "nedbor"}],
    "tromsoe": [{"dato", "temperatur", "nedbor"}],
    "vaernes": [{"dato", "temperatur", "nedbor"}],
    "vanabu": [{"dato", "temperatur", "nedbor"}],
}


def plotting(data, aar, stasjonsnavn):
    dager = [dag for dag in data if dag['dato'].year == aar]
    datoer = [dag['dato'] for dag in dager]
    felter = ['sno', 'nedbor', 'temp', 'vind']
    titler = ['Snødybde (cm)', 'Nedbør (mm)',
              'Middeltemperatur (°C)', 'Høyeste middelvind (m/s)']
    fig, akser = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
    for i in range(4):
        verdier = [dag[felter[i]] for dag in dager]
        akser[i].plot(datoer, verdier)
        akser[i].set_ylabel(titler[i])
        akser[i].grid(True)
        fig.suptitle(f'Værdata fra {stasjonsnavn} i {aar}')
        plt.tight_layout()
        plt.show()


def skifore(data, aar):
    antall = 0
    start = datetime(aar - 1, 11, 1)
    slutt = datetime(aar, 5, 31)
    for dag in data:
        if start <= dag['dato'] <= slutt:
            if dag['sno'] is not None and dag['sno'] >= 20:
                antall += 1
        return antall


def plantevekst(data, aar):
    vekst = 0
    for dag in data:
        if dag['dato'].year == aar:
            if dag['temp'] is not None and dag['temp'] > 5:
                vekst += dag['temp'] - 5
                return vekst


def lengste_torrperiode(data, aar):
    dager = [dag for dag in data if dag['dato'].year == aar]
    lengst = 0
    antall = 0
    start = None
    beste_start = None
    beste_slutt = None
    for dag in dager:
        if dag['nedbor'] == 0 and (antall == 0 or dag['dato'] - forrige_dato == timedelta(days=1)):
            if antall == 0:
                start = dag['dato']
            antall += 1
        elif dag['nedbor'] == 0:
            start = dag['dato']
            antall = 1
        else:
            antall = 0
        if antall > lengst:
            lengst = antall
            beste_start = start
            beste_slutt = dag['dato']
            forrige_dato = dag['dato']
            return lengst, beste_start, beste_slutt


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
    stasjoner = les_stasjoner('stasjoner')   # folder containing the CSV files
    print('Tilgjengelige stasjoner:', ', '.join(stasjoner))
    navn = input('Velg stasjon: ')
    if navn not in stasjoner:
        print('Ukjent stasjon.')
        return
    data = stasjoner[navn]

    aar = int(input('Skriv inn et år (2014-2025): '))
    if aar < 2014 or aar > 2025:
        print('Velg et år mellom 2014 og 2025.')
        return

    plotting(data, aar, navn)

    if aar == 2014:
        print('Merk: Skisesongen 2014 mangler data fra november og desember 2013.')

    print('Dager med skiføre:', skifore(data, aar))
    print('Total plantevekst:', round(plantevekst(data, aar), 1))
    lengde, start, slutt = lengste_torrperiode(data, aar)

    print('Lengste periode uten nedbør:', lengde, 'dager')

    if start is not None:
        print('Fra', start.strftime('%d.%m.%Y'),
              'til', slutt.strftime('%d.%m.%Y'))

    sommer, hoysommer, trope = sommerdager(data, aar)

    print('Sommerdager:', sommer)
    print('Høysommerdager:', hoysommer)
    print('Tropedager:', trope)
    print('Merk: Dager med manglende målinger er ikke telt med.')


if __name__ == '__main__':
    main()
