import pandas as pd

xls_path = "Input_urbsextensionv1.xlsx"
xls = pd.ExcelFile(xls_path)

if "Recycling_Costs" in xls.sheet_names:
    df = pd.read_excel(xls, "Recycling_Costs")
    print(df.to_string())
