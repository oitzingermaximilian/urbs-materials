import pandas as pd
import os
import re

# ==========================================
# 1. CONFIGURATION & MAPPING
# ==========================================
file_path = 'Input_urbsextensionv1.xlsx'  # Make sure this matches your actual file name
output_file = 'URBS_consolidated_input.csv'

# We define specific processing rules for each sheet "Archetype"
sheet_configs = {
    # ARCHETYPE 1: Simple Key-Value (Global Params)
    'Base': {
        'type': 'KeyValue',
        'key_col': 'Param',
        'val_col': 'Value'
    },

    # ARCHETYPE 2: Static Tech Parameters (Entity in Rows, Params in Cols)
    'Technologies': {
        'type': 'StaticMatrix',
        'id_vars': ['Technologies'],  # This becomes 'entity'
        'map_cols': {'Technologies': 'entity'},
        'default_year': '2025-2050'
    },

    # ARCHETYPE 3: Time Series Matrix (Year in Rows, Entity in Cols, Sheet Name = Param)
    'dcr': {
        'type': 'TimeSeries_EntityCols',
        'id_vars': ['Stf'],
        'param_name': 'dcr'  # Hardcode parameter name
    },
    'installable_capacity': {
        'type': 'TimeSeries_EntityCols',
        'id_vars': ['Stf'],
        'param_name': 'installable_capacity'
    },

    # ARCHETYPE 4: Complex Cost Sheet (Year in Rows, Params+Entity in Cols)
    # Header format: "parameter_entity" (e.g. import_EU27_solarPV)
    'cost_sheet': {
        'type': 'TimeSeries_ComplexHeader',
        'id_vars': ['Stf']
    },

    # ARCHETYPE 5: Multi-Index Time Series (Year + Entity in Rows, Params in Cols)
    'gas_block': {
        'type': 'TimeSeries_MultiRow',
        'id_vars': ['stf', 'block'],
        'map_cols': {'block': 'entity', 'stf': 'year'}
    },

    # ARCHETYPE 6: Time Steps (Year + Timestep in Rows, Entity in Cols)
    'loadfactors': {
        'type': 'TimeSeries_WithStep',
        'id_vars': ['timestep', 'Stf'],
        'param_name': 'load_factor'
    }
}

# ==========================================
# 2. PROCESSING LOGIC
# ==========================================
all_data = []
xls = pd.ExcelFile(file_path)

for sheet_name in xls.sheet_names:
    if sheet_name not in sheet_configs:
        print(f"Skipping sheet: {sheet_name} (No config found)")
        continue

    print(f"Processing sheet: {sheet_name}...")
    df = pd.read_excel(xls, sheet_name=sheet_name)
    config = sheet_configs[sheet_name]

    # Pre-processing: Fill forward years if they are merged in Excel (common in 'gas_block')
    if 'stf' in df.columns:
        df['stf'] = df['stf'].ffill()
    if 'Stf' in df.columns:
        df['Stf'] = df['Stf'].ffill()

    # --- LOGIC BRANCHES ---

    if config['type'] == 'KeyValue':
        # Simple rename
        df_processed = df.rename(columns={config['key_col']: 'parameter', config['val_col']: 'value'})
        df_processed['entity'] = 'Global'
        df_processed['year'] = None

    elif config['type'] == 'StaticMatrix':
        # Melt columns into parameters
        df_processed = df.melt(id_vars=config['id_vars'], var_name='parameter', value_name='value')
        df_processed = df_processed.rename(columns=config['map_cols'])
        df_processed['year'] = None
        df_processed['year_condition'] = config['default_year']

    elif config['type'] == 'TimeSeries_EntityCols':
        # Melt columns into entities
        df_processed = df.melt(id_vars=config['id_vars'], var_name='entity', value_name='value')
        df_processed = df_processed.rename(columns={'Stf': 'year'})
        df_processed['parameter'] = config['param_name']

    elif config['type'] == 'TimeSeries_MultiRow':
        # Melt columns (price, limit, emissions) into parameters
        df_processed = df.melt(id_vars=config['id_vars'], var_name='parameter', value_name='value')
        df_processed = df_processed.rename(columns=config['map_cols'])

    elif config['type'] == 'TimeSeries_WithStep':
        # Handle loadfactors (timestep needs to be preserved)
        df_processed = df.melt(id_vars=config['id_vars'], var_name='entity', value_name='value')
        df_processed = df_processed.rename(columns={'Stf': 'year'})
        df_processed['parameter'] = config['param_name']
        # We append timestep to year_condition or keep it separate?
        # For now, let's create a 'timestep' column and keep year_condition standard
        # If your model needs it in one column, we can combine them later.

    elif config['type'] == 'TimeSeries_ComplexHeader':
        # 1. Melt everything first
        df_long = df.melt(id_vars=config['id_vars'], var_name='raw_header', value_name='value')
        df_long = df_long.rename(columns={'Stf': 'year'})

        # 2. Parse the header (e.g., "import_EU27_solarPV" -> param="import", entity="EU27_solarPV")
        # We split by the FIRST underscore only.
        # Limitation: If your parameter has an underscore (e.g. "fixed_cost"), this logic needs tweaking.
        split_data = df_long['raw_header'].str.split('_', n=1, expand=True)
        df_long['parameter'] = split_data[0]
        df_long['entity'] = split_data[1]

        df_processed = df_long.drop(columns=['raw_header'])

    # --- COMMON CLEANUP ---

    # Add sheet origin
    df_processed['sheet_type'] = sheet_name

    # Add standardized Year Condition if not present
    if 'year_condition' not in df_processed.columns:
        # If we have a valid year, use it; otherwise default
        if 'year' in df_processed.columns:
            df_processed['year_condition'] = df_processed['year'].astype(str)
            # Handle NaN years (Global params)
            df_processed.loc[df_processed['year'].isna(), 'year_condition'] = '2025-2050'
        else:
            df_processed['year_condition'] = '2025-2050'

    # Ensure Site column exists (extract from entity if possible, else Default)
    if 'site' not in df_processed.columns:
        # Simple heuristic: If entity starts with "EU27", site is "EU27"
        # You can expand this logic later
        if 'entity' in df_processed.columns:
            df_processed['site'] = df_processed['entity'].astype(str).apply(
                lambda x: x.split('.')[0] if '.' in x else (x.split('_')[0] if '_' in x else 'Global')
            )
        else:
            df_processed['site'] = 'Global'

    # Standardize columns
    target_cols = ['sheet_type', 'site', 'year', 'entity', 'parameter', 'value', 'year_condition']

    # If we have 'timestep' (from loadfactors), we can keep it or merge it.
    # For now, I'll add it as an extra column if it exists, but you can drop it if you want strictly the format you asked for.
    if 'timestep' in df_processed.columns:
        target_cols.append('timestep')

    # Fill missing cols with None
    for col in target_cols:
        if col not in df_processed.columns:
            df_processed[col] = None

    all_data.append(df_processed[target_cols])

# ==========================================
# 3. SAVE
# ==========================================
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    # Optional: Filter out empty values (Excel often reads empty rows)
    final_df = final_df.dropna(subset=['value'])

    final_df.to_csv(output_file, index=False)
    print(f"Done! Saved {len(final_df)} rows to {output_file}")
    print(final_df.head())
else:
    print("No data extracted.")