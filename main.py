"""
project: micro wealth manager
by moonbak (c) 2024

Code License: MIT
"""
import json
from pprint import pprint
import sys

WPATH = 'wallet.json'


def gen_dummy_wallet():
    return {
        "revision": 1,
        "assets": [
            {"commodity": "gold", "volume": 3, "vol_info": "grams", "snap_valuation": 25, "year": 2024, "month": 4},
            {
                "commodity": "cash", "volume": 1533.5, "vol_info": "volatile_euros", "snap_valuation": 1533.5,
                "year": 2024, "month": 4
            }
        ],
        "commodities": [
            {"name": "cash", "positions": 1},
            {"name": "gold", "positions": 1}
        ]
    }


def serialize(given_obj):
    with open(WPATH, 'w') as fp:
        json.dump(given_obj, fp)


# - in case you need to dump the test wallet
# serialize(gen_dummy_wallet())
# sys.exit(1)

def calc_inflation():
    """
    calcul d'inflation mensuelle. Pour ca on compare la valeur actuelle IPC
    à la valeur de l'année précédente. Exemple mars 2024-> mars 2023
    """
    # tu peux vérifier que calcul est ok via:
    # https://www.insee.fr/fr/statistiques/serie/001761313
    print("feel free to check: https://www.insee.fr/fr/statistiques/serie/001761313")
    print()
    with open('ipc-timeseries.json', 'r') as my_fp:
        tmp = json.load(my_fp)
    trace = dict()
    for mm in (3, 2, 1):
        y = tmp['values'][f'2024-{mm:02d}']
        x = tmp['values'][f'2023-{mm:02d}']
        ratio = 100 * (y - x) / x
        trace[f'2024-{mm:02d}'] = ratio
        print(f'2024-{mm:02d} : {ratio:.2f}')
    for mm in (12, 11, 10, 9, 8, 7):
        y = tmp['values'][f'2023-{mm:02d}']
        x = tmp['values'][f'2022-{mm:02d}']
        ratio = 100 * (y - x) / x
        trace[f'2024-{mm:02d}'] = ratio
        print(f'2023-{mm:02d} : {ratio:.2f}')
    return tmp, trace


if __name__ == '__main__':
    ipc_table, infl = calc_inflation()
    print()
    print('And here is your wallet:')
    print()
    with open(WPATH, 'r') as fp:
        unpacked_obj = json.load(fp)
    pprint(unpacked_obj)

    print('curr value of euros:', unpacked_obj['assets'][1]['volume'])
    alpha_val = (unpacked_obj['assets'][1]['volume'] / ipc_table['values']['2024-03']) * 100
    print(f'true value of euros? {alpha_val:.2f}')
