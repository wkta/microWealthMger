import json
import datetime
from pprint import pprint
import sys

# Chemins des fichiers
WPATH = 'wallet.json'
IPC_PATH = 'ipc-timeseries.json'
ASSET_VALUES_PATH = 'asset_values.json'

def load_wallet():
    with open(WPATH, 'r') as fp:
        return json.load(fp)

def save_wallet(wallet):
    with open(WPATH, 'w') as fp:
        json.dump(wallet, fp)

def load_asset_values():
    try:
        with open(ASSET_VALUES_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_asset_values(asset_values):
    with open(ASSET_VALUES_PATH, 'w') as file:
        json.dump(asset_values, file)

def calc_inflation():
    # Supposons que cette fonction utilise les données IPC pour des calculs réels d'inflation
    with open(IPC_PATH, 'r') as my_fp:
        ipc_data = json.load(my_fp)
    return ipc_data


def rebalance_portfolio(wallet):
    print("Mise à jour du portefeuille.")
    changes_made = False  # Variable pour suivre les modifications

    while True:
        print("Choisissez une action :")
        print("a) Ajouter un actif")
        print("b) Retirer un actif")
        print("c) Terminer la mise à jour")
        action = input("Votre choix (a, b, c) : ").lower()

        if action == 'a':
            add_asset(wallet)
            changes_made = True
        elif action == 'b':
            remove_asset(wallet)
            changes_made = True
        elif action == 'c':
            if changes_made:
                # Mise à jour de la révision et de la date de dernière modification uniquement si des changements ont été faits
                wallet['revision'] += 1
                wallet['last_change'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Portefeuille mis à jour avec succès.")
                print(f"Révision actuelle : {wallet['revision']}")
                print(f"Dernière modification : {wallet['last_change']}")
                # Sauvegarder les changements dans le fichier wallet.json
                save_wallet(wallet)
            else:
                print("Aucune modification effectuée.")
            break
        else:
            print("Choix non valide, veuillez réessayer.")


def add_asset(wallet, asset_values):
    commodity = input("Entrez le type d'actif à ajouter (ex: gold, cryptoETF) : ")
    volume = float(input(f"Entrez la quantité de {commodity} à ajouter : "))
    vol_info = input(f"Entrez l'unité de mesure pour {commodity} (ex: grams, account unit) : ")
    current_week = datetime.datetime.now().strftime("%Yw%W")

    # Calcul du nouvel identifiant
    new_id = max((asset['id'] for asset in wallet['assets']), default=0) + 1
    new_asset = {
        "id": new_id,
        "commodity": commodity,
        "volume": volume,
        "vol_info": vol_info,
        "enter_date_info": current_week
    }
    wallet['assets'].append(new_asset)

    # Mise à jour des commodities_stats
    commodity_entry = next((item for item in wallet['commodities_stats'] if item['name'] == commodity), None)
    if commodity_entry:
        commodity_entry['positions'] += 1
        commodity_entry['total_volume'] += volume
    else:
        wallet['commodities_stats'].append({"name": commodity, "positions": 1, "total_volume": volume})

    # Demander et enregistrer le cours actuel si l'actif n'est pas du cash
    if commodity != 'cash':
        valuation = float(input(f"Entrez le cours actuel pour {commodity} : "))
        if current_week not in asset_values:
            asset_values[current_week] = {}
        asset_values[current_week][commodity] = {
            'valuation': valuation,
            'used_vol_unit': vol_info
        }

    # Sauvegarder les modifications dans asset_values.json
    save_asset_values(asset_values)

    print(f"Actif {commodity} ajouté avec succès.")


def remove_asset(wallet):
    asset_id = int(input("Entrez l'identifiant de l'actif à retirer : "))
    asset_to_remove = next((asset for asset in wallet['assets'] if asset['id'] == asset_id), None)
    if asset_to_remove:
        wallet['assets'].remove(asset_to_remove)
        # Mise à jour de commodities_stats
        commodity_entry = next((item for item in wallet['commodities_stats'] if item['name'] == asset_to_remove['commodity']), None)
        if commodity_entry:
            commodity_entry['positions'] -= 1
            commodity_entry['total_volume'] -= asset_to_remove['volume']
            if commodity_entry['positions'] == 0:
                wallet['commodities_stats'].remove(commodity_entry)
        print(f"Actif {asset_to_remove['commodity']} retiré.")
    else:
        print("Aucun actif trouvé avec cet identifiant.")


def update_asset_values(wallet):
    print("Mise à jour des valeurs des actifs.")
    print('-'*32)

    asset_values = load_asset_values()  # Charger les valeurs précédentes
    current_week = datetime.datetime.now().strftime("%Yw%W")

    for asset in wallet['assets']:
        if asset['commodity'] == 'cash':
            # Assigner la valeur de 1.0 au cash systématiquement
            if current_week not in asset_values:
                asset_values[current_week] = {}
            asset_values[current_week][asset['commodity']] = {
                'valuation': 1.0,
                'used_vol_unit': asset['vol_info']  # "euros" pour cash
            }
        else:
            print(f"{asset['commodity']} valeur actuelle: {asset['snap_valuation']} euros")
            new_valuation = input(f"Entrez la nouvelle évaluation pour {asset['commodity']} (en euros, laissez vide pour ne pas changer): ")
            if new_valuation:
                asset['snap_valuation'] = float(new_valuation)
                if current_week not in asset_values:
                    asset_values[current_week] = {}
                asset_values[current_week][asset['commodity']] = {
                    'valuation': asset['snap_valuation'],
                    'used_vol_unit': asset['vol_info']
                }
                print(f"Nouvelle évaluation pour {asset['commodity']}: {asset['snap_valuation']} euros")
    
    save_asset_values(asset_values)
    print("Valeurs des actifs mises à jour.")


def estimate_portfolio_val(wallet, asset_values, ipc_data):
    print("Estimation de la valeur actuelle du portefeuille en euros constants.")
    current_week = datetime.datetime.now().strftime("%Yw%W")
    pprint(asset_values)

    # Chercher les valeurs d'actifs les plus récentes
    if current_week in asset_values:
        latest_values = asset_values[current_week]
    else:
        # Si aucune valeur n'est enregistrée pour la semaine courante, utiliser la dernière disponible
        latest_available_week = max(asset_values.keys())
        print('last data available:', latest_available_week)
        latest_values = asset_values[latest_available_week]

    total_nominal_value = 0
    total_real_value = 0

    current_date = datetime.datetime.now()
    current_month = current_date.strftime("%Y-%m")  # Ex: '2024-04'

    # Calculer la valeur totale basée sur les dernières évaluations disponibles
    for asset in wallet['assets']:
        asset_type = asset['commodity']
        if asset_type in latest_values:
            current_valuation = latest_values[asset_type]['valuation']
            volume = asset['volume']
            valuation = current_valuation * volume
            total_nominal_value += valuation

            # Recherche de l'IPC le plus récent disponible si l'IPC du mois en cours n'est pas disponible
            if current_month in ipc_data['values']:
                current_ipc = ipc_data['values'][current_month]
            else:
                # Trouver le dernier mois disponible dans les données
                available_months = sorted(ipc_data['values'].keys(), reverse=True)
                last_available_month = available_months[0] if available_months else current_month
                # risky:
                # Utiliser 1 comme valeur par défaut si aucune donnée n'est disponible
                # safer:
                current_ipc = ipc_data['values'][last_available_month]

            real_valuation = valuation / current_ipc * 100
            total_real_value += real_valuation
            print(f"{asset_type}: {volume} {asset['vol_info']} à {current_valuation} par unité. Valeur totale: {valuation} euros, Valeur réelle ajustée: {real_valuation:.2f} euros constants")
        else:
            print(f"Aucune donnée de valeur trouvée pour {asset_type} à la semaine {current_week}")

    print(f"Valeur nominale totale du portefeuille: {total_nominal_value} euros")
    print(f"Valeur réelle totale du portefeuille ajustée pour l'inflation: {total_real_value:.2f} euros constants")
    return total_real_value




def main():
    wallet = load_wallet()
    ipc_data = calc_inflation()
    asset_values = load_asset_values()

    while True:
        print("1. Rééquilibrer le portefeuille")
        print("2. Mettre à jour les valeurs des actifs")
        print("3. Info sur la valeur du portefeuille et son évolution")
        print("4. Quitter")
        choice = input("Choisissez une option: ")

        if choice == '1':
            rebalance_portfolio(wallet)
            save_wallet(wallet)
        elif choice == '2':
            update_asset_values(wallet)
        elif choice == '3':
            estimate_portfolio_val(wallet, asset_values, ipc_data)
        elif choice == '4':
            print("Fin du programme.")
            break
        else:
            print("Option invalide. Veuillez réessayer.")

if __name__ == '__main__':
    main()
