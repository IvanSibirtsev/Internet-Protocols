# Трассировка автономных систем

## Запуск
    python tracert_ac.py -addr mit.edu
либо

    python tracert_ac.py -addr 104.98.238.167

## Результат
    Трассировка маршрута к mit.edu [104.98.238.167]
    №  IP                AS       Country/City         Provider
    1  192.168.1.1       --       --/--                --
    2  91.191.245.1      AS12668  RU/Yekaterinburg     LLC KomTehCentr
    3  92.242.29.226     AS12668  RU/Yekaterinburg     LLC KomTehCentr
    4  95.167.3.10       AS12389  RU/Magadan           PJSC Rostelecom
    5  95.167.3.9        AS12389  RU/Magadan           PJSC Rostelecom
    6  77.67.90.96       AS3257   US/Stockton          GTT Communications Inc.
    7  213.200.117.58    AS3257   NL/Amsterdam         GTT Communications Inc.
    8  154.14.69.154     AS3257   DE/Düsseldorf        GTT Communications Inc.
    9  23.210.55.40      AS20940  NL/Amsterdam         Akamai International B.V.
    10 95.100.192.124    AS20940  GB/Slough            Akamai International B.V.
    11 23.210.48.35      AS20940  GB/London            Akamai International B.V.
    12 23.210.48.133     AS20940  GB/London            Akamai International B.V.
    13 104.98.238.167    AS20940  GB/London            Akamai International B.V.
    Трассировка завершена.