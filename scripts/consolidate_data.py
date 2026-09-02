import pandas as pd
import os

def consolidate_excel_files(input_folder, output_file, start_year=2024, end_year=2050):
    all_sheets_data = {}
    
    for year in range(start_year, end_year + 1):
        file_path = os.path.join(input_folder, f'{year}.xlsx')
        if not os.path.exists(file_path):
            print(f'File not found: {file_path}')
            continue
            
        print(f'Loading data from {year}.xlsx...')
        try:
            # Read all sheets from the Excel file
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            for sheet_name, df in excel_data.items():
                if df.empty:
                    continue
                # Add Year column to the dataframe
                df['Year'] = year
                
                # Move 'Year' to the first column for better visibility
                cols = ['Year'] + [col for col in df.columns if col != 'Year']
                df = df[cols]
                
                if sheet_name not in all_sheets_data:
                    all_sheets_data[sheet_name] = []
                
                all_sheets_data[sheet_name].append(df)
                
        except Exception as e:
            print(f'Error reading {file_path}: {e}')
            
    print("\nApplying background data overrides...")
    
    # ---------------- CO2 prices ----------------
    if 'Commodity' in all_sheets_data:
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = (65 + (stf - 2024) * (75 - 65) / (2030 - 2024)) * 1e-3

        fixed_co2_prices_tyndp = {
            2031: 115.9 * 1e-3, 2032: 118.4 * 1e-3, 2033: 120.9 * 1e-3,
            2034: 123.4 * 1e-3, 2035: 125.9 * 1e-3, 2036: 128.4 * 1e-3,
            2037: 130.9 * 1e-3, 2038: 133.4 * 1e-3, 2039: 135.9 * 1e-3,
            2040: 147.0 * 1e-3, 2041: 149.1 * 1e-3, 2042: 151.2 * 1e-3,
            2043: 153.3 * 1e-3, 2044: 155.4 * 1e-3, 2045: 157.5 * 1e-3,
            2046: 159.6 * 1e-3, 2047: 161.7 * 1e-3, 2048: 163.8 * 1e-3,
            2049: 165.9 * 1e-3, 2050: 168.0 * 1e-3,
        }
        co2_prices.update(fixed_co2_prices_tyndp)
        
        for i, df in enumerate(all_sheets_data['Commodity']):
            year = df['Year'].iloc[0] if not df.empty else None
            if year in co2_prices:
                # Update the price for CO2 in EU27
                mask = (df['Site'] == 'EU27') & (df['Commodity'] == 'CO2')
                df.loc[mask, 'price'] = co2_prices[year]
                
    if 'Demand' in all_sheets_data:
        yearly_profile = [
            # User specifically requested spreading the yearly demand across 12 timesteps (v / 12)
            (v * 1e-3) / 12 for v in [
                207658333.3, 215588018.8, 223517704.2, 231447389.6, 239377075.1,
                247306760.5, 255236445.9, 260097649.0, 264958852.1, 269820055.3,
                274681258.3, 279542461.5, 284403664.6, 289264867.8, 294126070.8,
                298987274.0, 294534045.3, 298734647.4, 302935249.6, 307135851.7,
                311336453.8, 315537055.9, 319737658.1, 323938260.2, 328138862.3,
                332339464.4, 338580792.8,
            ]
        ]
        demand_dict = dict(zip(range(2024, 2051), yearly_profile))
        
        for df in all_sheets_data['Demand']:
            year = df['Year'].iloc[0] if not df.empty else None
            if year in demand_dict:
                # In urbs, Demand is usually formatted as 'Site.Commodity' (e.g. EU27.Elec)
                # Ensure we only overwrite values where t > 0
                if 'EU27.Elec' in df.columns and 't' in df.columns:
                    df.loc[df['t'] > 0, 'EU27.Elec'] = demand_dict[year]
                elif 'Elec' in df.columns and 't' in df.columns:
                    df.loc[df['t'] > 0, 'Elec'] = demand_dict[year]

    # ---------------- SUPIM ----------------
    if 'SupIm' in all_sheets_data:
        for df in all_sheets_data['SupIm']:
            # In urbs, SupIm is also formatted as 'Site.Commodity' (e.g. EU27.Hydro)
            # Ensure we only overwrite values where t > 0
            if 'EU27.Hydro' in df.columns and 't' in df.columns:
                df.loc[df['t'] > 0, 'EU27.Hydro'] = 0.3375
            elif 'Hydro' in df.columns and 't' in df.columns:
                df.loc[df['t'] > 0, 'Hydro'] = 0.3375
            
    print("\nConcatenating data and writing to output file...")
    
    # Write to a new Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, dfs in all_sheets_data.items():
            consolidated_df = pd.concat(dfs, ignore_index=True)
            consolidated_df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f'Written sheet: {sheet_name} with {len(consolidated_df)} rows')
            
    print(f"\nSuccessfully consolidated data into {output_file}")

if __name__ == "__main__":
    # Get the base directory (the project root) dynamically
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_folder = os.path.join(BASE_DIR, "Input", "urbs_intertemporal_2050")
    output_file = os.path.join(BASE_DIR, "Input", "urbs_intertemporal_master.xlsx")
    
    consolidate_excel_files(input_folder, output_file, 2024, 2050)
