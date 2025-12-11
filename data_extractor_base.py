import pandas as pd
import os

# --- CONFIGURATION ---
INPUT_DIR = "Input/urbs_intertemporal_2050"

# 1. TIMELINE SETTINGS
MODEL_START_YEAR = 2024
MODEL_END_YEAR = 2050

# A. YEARS TO SCAN
ALL_YEARS = list(range(MODEL_START_YEAR, MODEL_END_YEAR + 1))

# B. VINTAGE YEARS
VINTAGE_YEARS = [2024, 2030, 2040, 2050]

# 2. SHEET CLASSIFICATION
SHEETS_VINTAGE_ONLY = [
    'Process',
    'Process-Commodity',
    'Site',
    'Global'
]

SHEETS_EVERY_YEAR = [
    'Demand',
    'SupIm',
    'Commodity'
]

TARGET_COLS = ['sheet_type', 'site', 'year', 'entity', 'parameter', 'value', 'year_condition', 'timestep']


# --- HELPER FUNCTIONS ---

def process_vintage_sheet(df, sheet_type, year):
    """
    Handles Process/Storage Vintages.
    - NEW LOGIC: All costs/efficiency are defined in 2024 (valid 2024-2050).
    - ONLY cap-up changes over time to 'activate' the tech.
    """
    if df is None or df.empty: return pd.DataFrame()

    entity_col = 'Process' if 'Process' in df.columns else 'Storage'
    # Name example: Lignite_2050
    df['entity'] = df[entity_col].astype(str) + f"_{year}"

    if 'Site' not in df.columns: df['Site'] = 'Global'
    df['site'] = df['Site']

    list_of_dfs = []

    # 1. PARAMETER GROUPS
    init_params = ['lifetime', 'inst-cap']  # Defined in 2024 (Value 0 if future)
    lock_params = ['cap-up', 'min-fraction']  # Dynamic: 0 before vintage, Value after

    ignore = [entity_col, 'Site', 'entity', 'site', 'sheet_type']
    available_cols = [c for c in df.columns if c not in ignore]

    # -------------------------------------------------------------------
    # A. INITIALIZATION (inst-cap, lifetime)
    # -------------------------------------------------------------------
    # Always Year 2024. If future vintage, force value to 0.

    if year == MODEL_START_YEAR:
        # If vintage is 2024, take real values
        cols_init = [c for c in available_cols if c in init_params]
        if cols_init:
            melted = df.melt(id_vars=['entity', 'site'], value_vars=cols_init,
                             var_name='parameter', value_name='__temp_value__')
            melted = melted.rename(columns={'__temp_value__': 'value'})
            melted['year_condition'] = str(MODEL_START_YEAR)
            melted['year'] = MODEL_START_YEAR
            melted['sheet_type'] = sheet_type
            melted['timestep'] = None
            melted['value'] = melted['value'].fillna(0)
            list_of_dfs.append(melted)
    else:
        # If vintage is Future (2050), force 0 at 2024
        base_df = df[['entity', 'site']].copy()
        for param in init_params:
            temp = base_df.copy()
            temp['parameter'] = param
            temp['value'] = 0
            temp['year_condition'] = str(MODEL_START_YEAR)
            temp['year'] = MODEL_START_YEAR
            temp['sheet_type'] = sheet_type
            temp['timestep'] = None
            list_of_dfs.append(temp)

    # -------------------------------------------------------------------
    # B. DYNAMIC ACTIVATION (cap-up, min-fraction)
    # -------------------------------------------------------------------
    # This is the ONLY place where we have time-dependent split

    # 1. Dormant Phase (2024 -> Vintage-1)
    if year > MODEL_START_YEAR:
        locked_df = df[['entity', 'site']].copy()
        for param in lock_params:
            temp = locked_df.copy()
            temp['parameter'] = param
            temp['value'] = 0  # <--- FORCE 0 (Cannot build yet)
            temp['year_condition'] = f"{MODEL_START_YEAR}-{year - 1}"
            temp['year'] = MODEL_START_YEAR  # Defined at start
            temp['sheet_type'] = sheet_type
            temp['timestep'] = None
            list_of_dfs.append(temp)

    # 2. Active Phase (Vintage -> 2050)
    # Uses the actual value from Excel (e.g., 9999 or whatever is in the sheet)
    cols_lock = [c for c in available_cols if c in lock_params]
    if cols_lock:
        melted = df.melt(id_vars=['entity', 'site'], value_vars=cols_lock,
                         var_name='parameter', value_name='__temp_value__')
        melted = melted.rename(columns={'__temp_value__': 'value'})

        melted['value'] = melted['value'].fillna(0)
        melted['year_condition'] = f"{year}-{MODEL_END_YEAR}"
        # We assign it to the vintage year so we know when it starts
        melted['year'] = year
        melted['sheet_type'] = sheet_type
        melted['timestep'] = None
        list_of_dfs.append(melted)

    # -------------------------------------------------------------------
    # C. STATIC PARAMETERS (inv-cost, fix-cost, eff, etc.)
    # -------------------------------------------------------------------
    # CRITICAL CHANGE: These are now ALWAYS defined in 2024, valid 2024-2050.

    # Get all columns that are NOT init or lock params
    cols_static = [c for c in available_cols if c not in init_params and c not in lock_params]

    if cols_static:
        melted = df.melt(id_vars=['entity', 'site'], value_vars=cols_static,
                         var_name='parameter', value_name='__temp_value__')
        melted = melted.rename(columns={'__temp_value__': 'value'})

        melted['value'] = melted['value'].fillna(0)

        # ALWAYS start at 2024
        melted['year_condition'] = f"{MODEL_START_YEAR}-{MODEL_END_YEAR}"
        melted['year'] = MODEL_START_YEAR

        melted['sheet_type'] = sheet_type
        melted['timestep'] = None
        list_of_dfs.append(melted)

    return pd.concat(list_of_dfs, ignore_index=True)


def process_process_commodity(df, sheet_type, year):
    # Same logic: Defined in 2024, valid until 2050
    if df is None or df.empty: return pd.DataFrame()

    df['entity'] = df['Process'].astype(str) + f"_{year}"
    df['parameter'] = df['Commodity'] + "_" + df['Direction']
    df['value'] = df['ratio']

    # Always 2024-2050
    df['year_condition'] = f"{MODEL_START_YEAR}-{MODEL_END_YEAR}"
    df['year'] = MODEL_START_YEAR

    df['site'] = 'Global'
    df['sheet_type'] = sheet_type
    df['timestep'] = None
    df['value'] = df['value'].fillna(0)

    return df[['sheet_type', 'site', 'year', 'entity', 'parameter', 'value', 'year_condition', 'timestep']]


def process_commodity_sheet(df, sheet_type, year):
    # Prices still vary annually
    if df is None or df.empty: return pd.DataFrame()
    col = 'Name' if 'Name' in df.columns else (df.columns[0] if 'Commodity' not in df.columns else 'Commodity')
    df['entity'] = df[col]
    if 'Site' not in df.columns: df['Site'] = 'Global'
    df['site'] = df['Site']
    ignore = [col, 'Site', 'entity', 'site']
    value_vars = [c for c in df.columns if c not in ignore]

    melted = df.melt(id_vars=['entity', 'site'], value_vars=value_vars,
                     var_name='parameter', value_name='__temp_value__')
    melted = melted.rename(columns={'__temp_value__': 'value'})

    melted['value'] = melted['value'].fillna(0)
    melted['year_condition'] = str(year)
    melted['year'] = year
    melted['sheet_type'] = sheet_type
    melted['timestep'] = None
    return melted


def process_timeseries_sheet(df, sheet_type, year):
    if df is None or df.empty: return pd.DataFrame()
    timestep_col = df.columns[0]
    df = df.rename(columns={timestep_col: 'timestep'})
    value_vars = [c for c in df.columns if c != 'timestep']

    melted = df.melt(id_vars=['timestep'], value_vars=value_vars,
                     var_name='raw_header', value_name='__temp_value__')
    melted = melted.rename(columns={'__temp_value__': 'value'})

    melted['value'] = melted['value'].fillna(0)

    def parse_header(header):
        parts = str(header).split('.')
        return (parts[0], parts[1]) if len(parts) >= 2 else ('Global', parts[0])

    melted[['site', 'entity']] = melted['raw_header'].apply(lambda x: pd.Series(parse_header(x)))
    melted['year_condition'] = str(year)
    melted['year'] = year
    melted['sheet_type'] = sheet_type
    melted['parameter'] = 'fix' if sheet_type == 'Demand' else 'sup-im'
    return melted[['sheet_type', 'site', 'year', 'entity', 'parameter', 'value', 'year_condition', 'timestep']]


# --- MAIN CONVERTER ---
def main_converter():
    print(f"Reading EXCEL files from: {os.path.abspath(INPUT_DIR)}")
    all_data = []

    for year in ALL_YEARS:
        file_path = os.path.join(INPUT_DIR, f"{year}.xlsx")

        if not os.path.exists(file_path):
            if year in VINTAGE_YEARS:
                print(f"❌ Warning: Vintage File not found {file_path}")
            continue

        print(f"--- Processing {year}.xlsx ---")

        if year in VINTAGE_YEARS:
            current_sheets = SHEETS_VINTAGE_ONLY + SHEETS_EVERY_YEAR
        else:
            current_sheets = SHEETS_EVERY_YEAR

        for sheet_name in current_sheets:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            except ValueError:
                continue
            except Exception as e:
                print(f"   [Error] reading {sheet_name}: {e}")
                continue

            if sheet_name in ['Process', 'Storage']:
                processed = process_vintage_sheet(df, sheet_name, year)
            elif sheet_name == 'Process-Commodity':
                processed = process_process_commodity(df, sheet_name, year)
            elif sheet_name in ['Demand', 'SupIm']:
                processed = process_timeseries_sheet(df, sheet_name, year)
            else:
                processed = process_commodity_sheet(df, sheet_name, year)

            if not processed.empty:
                all_data.append(processed[TARGET_COLS])

    if not all_data:
        print("❌ ERROR: No data loaded.")
        return

    final_df = pd.concat(all_data, ignore_index=True)
    final_df['value'] = final_df['value'].fillna(0)

    output_file = "Universal_Model_Data.csv"
    final_df.to_csv(output_file, index=False)
    print(f"✅ Success! Generated '{output_file}' with {len(final_df)} rows.")

    # --- FINAL CHECKS ---
    print("\n[CHECK 1] Costs Validity (Must be 2024-2050 for 2050 Vintage):")
    # Looking for inv-cost of a 2050 vintage
    mask_cost = (final_df['sheet_type'] == 'Process') & \
                (final_df['entity'].str.contains("_2050")) & \
                (final_df['parameter'] == 'inv-cost')
    print(final_df[mask_cost].head(1))

    print("\n[CHECK 2] Cap-Up Dynamic (0 before 2050):")
    # Looking for cap-up of a 2050 vintage (should see 2024-2049 = 0)
    mask_cap = (final_df['sheet_type'] == 'Process') & \
               (final_df['entity'].str.contains("_2050")) & \
               (final_df['parameter'] == 'cap-up')
    print(final_df[mask_cap].sort_values('year_condition').head(2))


if __name__ == "__main__":
    main_converter()