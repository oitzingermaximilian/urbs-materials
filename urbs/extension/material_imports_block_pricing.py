import pyomo.core as pyomo
import pandas as pd

def apply_material_block_pricing(m, data):
    """
    Apply block-based allocation for imported materials.
    Financial valuation (multiplying by price and discounting)
    is handled centrally in the TradeCostRule.
    """

    # ==========================================
    # SETS
    # ==========================================
    m.price_blocks = pyomo.Set(
        initialize=list(data["mat_blocks"]),
        doc="Material pricing blocks (e.g., Tier1, Tier2, Tier3)"
    )

    # ==========================================
    # PARAMETERS
    # ==========================================
    m.mat_block_limits = pyomo.Param(
        m.stf, m.materials, m.price_blocks,
        initialize=lambda m, stf, mat, blk: data["mat_limits"].get((stf, mat, blk), 0.0),
        within=pyomo.NonNegativeReals,
        doc="Maximum import volume per block per year"
    )

    m.mat_block_prices = pyomo.Param(
        m.stf, m.materials, m.price_blocks,
        initialize=lambda m, stf, mat, blk: data["mat_prices"].get((stf, mat, blk), 0.0),
        within=pyomo.NonNegativeReals,
        doc="Price per unit for a specific block"
    )

    def export_block_params_to_excel(m, output_filename="pyomo_block_params_debug.xlsx"):
        """
        Extracts the initialized block limits and prices directly from
        the Pyomo model and saves them to an Excel file.
        """
        print("Extracting material block parameters from Pyomo...")

        rows = []

        # Iterate over the indices of the Parameter (stf, material, block)
        for (stf, mat, blk) in m.mat_block_limits:
            # Extract the numerical values
            limit_val = pyomo.value(m.mat_block_limits[stf, mat, blk])
            price_val = pyomo.value(m.mat_block_prices[stf, mat, blk])

            rows.append({
                "stf": stf,
                "material": mat,
                "block": blk,
                "mat_block_limit": limit_val,
                "mat_block_price": price_val
            })

        # Convert to DataFrame and export
        df = pd.DataFrame(rows)
        df.to_excel(output_filename, index=False)

        print(f"✅ Successfully exported {len(df)} parameter rows to {output_filename}")
        return df

    export_block_params_to_excel(m, "final_pyomo_params.xlsx")

    # ==========================================
    # VARIABLES
    # ==========================================
    m.material_imported_block = pyomo.Var(
        m.stf, m.materials, m.price_blocks,
        within=pyomo.NonNegativeReals,
        doc="Material imported allocated to specific pricing blocks"
    )

    # ==========================================
    # CONSTRAINTS
    # ==========================================

    # 1) Enforce Block Limits
    def mat_block_limit_rule(m, stf, mat, blk):
        # If the parameter limit is 0, enforce 0 immediately to reduce solver space
        if m.mat_block_limits[stf, mat, blk] == 0:
            return m.material_imported_block[stf, mat, blk] == 0

        return m.material_imported_block[stf, mat, blk] <= m.mat_block_limits[stf, mat, blk]

    m.mat_block_limit_constraint = pyomo.Constraint(
        m.stf, m.materials, m.price_blocks, rule=mat_block_limit_rule
    )

    # 2) Link: Total material_imported == Sum of blocks
    # This connects your new block logic to the rest of the model
    def link_mat_block_to_original_rule(m, stf, mat):
        return m.material_imported[stf, mat] == sum(
            m.material_imported_block[stf, mat, blk] for blk in m.price_blocks
        )

    m.link_mat_block_to_original_constraint = pyomo.Constraint(
        m.stf, m.materials, rule=link_mat_block_to_original_rule
    )