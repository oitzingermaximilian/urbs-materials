import pandas as pd
import os
import numpy as np

def generate_vintages_from_data(input_file, output_file, vintage_years):
    """
    Reads the master Excel file and extracts true vintage data from the specified years,
    replicating them as separate technologies (e.g., gasplant_2030) across all years.
    """
    print(f"Reading {input_file}...")
    xls = pd.ExcelFile(input_file, engine='openpyxl')
    
    all_sheets = {}
    base_year = 2024
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Clean up string columns by replacing spaces with underscores
        # Skip the Global sheet to prevent breaking hardcoded property names like 'Discount rate'
        if sheet_name != 'Global':
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: x.replace(' ', '_') if isinstance(x, str) else x)
        
        if sheet_name == 'Process':
            print("Processing the 'Process' sheet for vintages based on true data...")
            df_new = []
            
            if 'Year' not in df.columns:
                print("Error: 'Year' column not found in Process sheet.")
                return
                
            unique_techs = df[df['Year'] == base_year]['Process'].unique()
            all_years = df['Year'].unique()
            
            for tech in unique_techs:
                # 1. Base vintage (e.g., tech_2024) - Uses the actual historical data from each year
                for year in all_years:
                    actual_year_data = df[(df['Year'] == year) & (df['Process'] == tech)]
                    if not actual_year_data.empty:
                        row = actual_year_data.iloc[0].copy()
                    else:
                        # Fallback if a year is missing
                        tech_2024_data = df[(df['Year'] == base_year) & (df['Process'] == tech)]
                        row = tech_2024_data.iloc[0].copy()
                        row['Year'] = year
                        row['inst-cap'] = 0 # Don't duplicate initial capacity
                        
                    row['Process'] = f"{tech}_{base_year}"
                    df_new.append(row)
                
                # 2. Future vintages - Extracted EXACTLY from the respective year's row
                for v_year in vintage_years:
                    tech_v_data = df[(df['Year'] == v_year) & (df['Process'] == tech)]
                    
                    if not tech_v_data.empty:
                        v_row = tech_v_data.iloc[0]
                        for year in all_years:
                            row = v_row.copy()
                            row['Year'] = year
                            row['Process'] = f"{tech}_{v_year}"
                            
                            # Only active in or after the vintage year
                            if year < v_year:
                                row['cap-up'] = 0
                                row['inst-cap'] = 0
                            else:
                                # Future tech doesn't have pre-existing installed capacity
                                row['inst-cap'] = 0
                                # If the original cap-up was 0 (to deactivate it previously), make it inf now
                                if 'cap-up' in row and row['cap-up'] == 0:
                                    row['cap-up'] = np.inf
                                    
                            df_new.append(row)
                            
            all_sheets[sheet_name] = pd.DataFrame(df_new)
            
        elif sheet_name in ['Process-Commodity', 'Process_Commodity']:
            print(f"Processing the '{sheet_name}' sheet for vintages based on true data...")
            df_new = []
            
            unique_techs = df[df['Year'] == base_year]['Process'].unique()
            all_years = df['Year'].unique()
            
            for tech in unique_techs:
                # 1. Base vintage
                for year in all_years:
                    actual_year_rows = df[(df['Year'] == year) & (df['Process'] == tech)]
                    if not actual_year_rows.empty:
                        rows = actual_year_rows.copy()
                    else:
                        tech_2024_rows = df[(df['Year'] == base_year) & (df['Process'] == tech)]
                        rows = tech_2024_rows.copy()
                        rows['Year'] = year
                    
                    rows['Process'] = f"{tech}_{base_year}"
                    df_new.append(rows)
                
                # 2. Future vintages
                for v_year in vintage_years:
                    tech_v_rows = df[(df['Year'] == v_year) & (df['Process'] == tech)]
                    if not tech_v_rows.empty:
                        for year in all_years:
                            rows = tech_v_rows.copy()
                            rows['Year'] = year
                            rows['Process'] = f"{tech}_{v_year}"
                            df_new.append(rows)
                            
            all_sheets[sheet_name] = pd.concat(df_new, ignore_index=True)
            
        elif sheet_name == 'TimeVarEff':
            print(f"Processing the '{sheet_name}' sheet, duplicating 2024 data across all years...")
            df_new = []
            
            if 'Year' in df.columns:
                base_year = 2024
                all_years = list(range(2024, 2051))
                
                # Get the 2024 data
                base_data = df[df['Year'] == base_year]
                
                if not base_data.empty:
                    for year in all_years:
                        rows = base_data.copy()
                        rows['Year'] = year
                        df_new.append(rows)
                    all_sheets[sheet_name] = pd.concat(df_new, ignore_index=True)
                else:
                    all_sheets[sheet_name] = df
            else:
                all_sheets[sheet_name] = df
                
        else:
            all_sheets[sheet_name] = df
            
    print(f"Saving updated data to {output_file}...")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, sheet_df in all_sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    print("Done! True data vintages extracted successfully.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(BASE_DIR, "Input", "urbs_intertemporal_master.xlsx")
    output_file = os.path.join(BASE_DIR, "Input", "urbs_intertemporal_master_vintages.xlsx")
    
    # Define the years from which to extract new technology definitions
    vintages_to_extract = [2030, 2040, 2050]
    
    if os.path.exists(input_file):
        generate_vintages_from_data(input_file, output_file, vintages_to_extract)
    else:
        print(f"Could not find {input_file}. Please run consolidate_data.py first.")
