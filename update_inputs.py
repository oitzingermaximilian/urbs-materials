import pandas as pd
import os

file_path = r"c:\Users\maxoi\OneDrive\Desktop\Repositories\urbs-materials\Input_urbsextensionv1.xlsx"
out_path = r"c:\Users\maxoi\OneDrive\Desktop\Repositories\urbs-materials\Input_urbsextensionv1.xlsx"

# Backup first
import shutil
shutil.copy(file_path, file_path + ".bak")

# Load Excel file and read all sheets
sheets = pd.read_excel(file_path, sheet_name=None)

# 1. Update Material_Intensity sheet
if "Material_Intensity" in sheets:
    mat_df = sheets["Material_Intensity"]
    
    magnet_mats = ["dysprosium", "neodymium", "praseodymium", "terbium"]
    bulk_mats = ["blade_bulk_on", "tower_bulk_on", "blade_bulk_off", "tower_bulk_off", "aluminum", "cobalt", "copper", "gallium", "graphite", "lithium", "manganese", "nickel", "niobium", "titanium", "vanadium"]
    
    for idx, row in mat_df.iterrows():
        tech = row["Technology"]
        mat = row["Material"]
        if tech in ["windon", "windoff"]:
            if mat in magnet_mats:
                mat_df.at[idx, "rec_efficiency"] = 0.94
            elif mat in bulk_mats:
                mat_df.at[idx, "rec_efficiency"] = 0.56
                
    sheets["Material_Intensity"] = mat_df

# 2. Update Cost_Data sheet
if "Cost_Data" in sheets:
    cost_df = sheets["Cost_Data"]
    
    # Values in k€/kton
    cost_magnet_opex = 18032.0   # $19,600/t -> ~18,032 EUR/t -> 18032 k€/kton
    cost_bulk_opex = 161.0       # $175/t -> ~161 EUR/t -> 161 k€/kton
    
    cost_magnet_capex = 83904.0  # $142M for 1557t/yr -> ~83,904 EUR/t/yr -> 83904 k€/kton/yr
    cost_bulk_capex = 100.0      # 6M€ for 60,000t/yr -> 100 EUR/t/yr -> 100 k€/kton/yr
    
    cols_to_add = {
        "recyclingcostmagnet_EU27_windon": cost_magnet_opex,
        "recyclingcostmagnet_EU27_windoff": cost_magnet_opex,
        "recyclingcostbulk_EU27_windon": cost_bulk_opex,
        "recyclingcostbulk_EU27_windoff": cost_bulk_opex,
        "recyclingcapexmagnet_EU27_windon": cost_magnet_capex,
        "recyclingcapexmagnet_EU27_windoff": cost_magnet_capex,
        "recyclingcapexbulk_EU27_windon": cost_bulk_capex,
        "recyclingcapexbulk_EU27_windoff": cost_bulk_capex
    }
    
    for col, val in cols_to_add.items():
        if col not in cost_df.columns:
            cost_df[col] = val
        else:
            cost_df[col] = val
            
    sheets["Cost_Data"] = cost_df

# Save back to Excel
with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
    for sheet_name, df in sheets.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Excel file successfully updated with new pathways!")
