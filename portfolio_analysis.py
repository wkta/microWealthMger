import json
import datetime


# The following script is currently bugged and needs to be fixed!

# [Where does the problem comes from?]
# IPC timeseries are monthly (format: 2024-05 for example),
# whereas the rest of the program uses a model with updates that are weekly,
# format: 2024w09 for example, it denotes the 9th week of the wear... 

# To fix bugs in the current file, one would need to take that into account


# File paths
WALLET_PATH = 'wallet.json'
ASSET_VALUES_PATH = 'asset_values.json'
TMP_IPC_PATH = 'ipc-timeseries.json'


def load_json_data(filepath):
    """Load data from a JSON file."""
    with open(filepath, 'r') as file:
        return json.load(file)


def calculate_asset_contributions(wallet, asset_values, ipc_values, start_week, end_week):
    contributions = {}
    base_ipc = ipc_values[start_week]
    current_ipc = ipc_values[end_week]

    for asset in wallet['assets']:
        commodity = asset['commodity']
        volume = asset['volume']

        # Get initial and final valuations
        initial_valuation = asset_values[start_week][commodity]['valuation']
        final_valuation = asset_values[end_week][commodity]['valuation']
        print(f'{commodity}: init and final valuations are:', initial_valuation, final_valuation)

        # Adjust values for inflation
        initial_valuation_adjusted = adjust_for_inflation(initial_valuation, current_ipc, base_ipc)
        final_valuation_adjusted = adjust_for_inflation(final_valuation, current_ipc, base_ipc)

        # Calculate contribution
        initial_value = volume * initial_valuation_adjusted
        final_value = volume * final_valuation_adjusted
        contribution = final_value - initial_value

        contributions[commodity] = contributions.get(commodity, 0) + contribution

    return contributions

def main():
    wallet = load_json_data('wallet.json')
    asset_values = load_json_data('asset_values.json')
    ipc_values = load_json_data(TMP_IPC_PATH)
    start_week = '2023w06'
    end_week = '2024w18'

    contributions = calculate_asset_contributions(wallet, asset_values, ipc_values, start_week, end_week)
    print("Asset Contributions:", contributions)



def display_contributions(contributions):
    """Display the contributions of each asset."""
    total_contribution = sum(contributions.values())
    for commodity, contribution in contributions.items():
        print(f"{commodity} contributed: {contribution:.2f} euros")
        if total_contribution != 0:
            percentage = (contribution / total_contribution) * 100
            print(f"Percentage of total growth: {percentage:.2f}%")

"""
def main():
    # Load data
    wallet = load_json_data(WALLET_PATH)
    asset_values = load_json_data(ASSET_VALUES_PATH)

    # Define the period to analyze
    start_week = '2022w48'
    end_week = '2024w18'

    # Calculate contributions
    print('start and end weeks are, respectively:', start_week, end_week)

    contributions = calculate_asset_contributions(wallet, asset_values, start_week, end_week)

    # Display results
    display_contributions(contributions)
"""

if __name__ == '__main__':
    main()
