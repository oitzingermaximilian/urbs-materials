import pyomo.environ as pyomo


def apply_variables(m):
    """
    These Variables are used for the stockpile.py script constraints
    """

    # NOM: \hat{\pi}_{y,\ell,k} | Installed capacity | MW
    m.capacity_ext = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{new}_{y,\ell,k} | Newly installed capacity | MW
    m.capacity_ext_new = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{imp}_{y,\ell,k} | Imported capacity | MW
    m.capacity_ext_imported = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{sto-out}_{y,\ell,k} | Stockpile withdrawals | MW
    m.capacity_ext_stockout = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{eu-prim}_{y,\ell,k} | Primary capacity additions | MW
    m.capacity_ext_euprimary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{eu-sec}_{y,\ell,k} | Remanufactured capacity additions | MW
    m.capacity_ext_eusecondary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{facility}_{y,\ell,k} | Remanufacturing facility capacity | MW
    m.capacity_facility_eusecondary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{facility-inactive}_{y,\ell,k} | Unused capacity of facility | MW
    m.capacity_inactive_eusecondary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{sto}_{y,\ell,k} | Stockpile level | MW
    m.capacity_ext_stock = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{sto-imp}_{y,\ell,k} | Stockpile imports | MW
    m.capacity_ext_stock_imported = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{sto-short}_{y,\ell,k} | Stockpile Shortfall/Stockout Sum | MW
    m.sum_outofstock = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{sto-sum}_{y,\ell,k} | Total Stockpile Sum | MW
    m.sum_stock = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    # NOM: ADM_{y,\ell,k} | Anti-dumping measures | -
    m.anti_dumping_measures = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    """
    These Variables are used for the balance_converter.py script constraints
    """
    # NOM: Bal^{ext}_{t,y,\ell,k} | Balance extension (res_vertex_rule) | MW
    m.balance_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: Bal^{imp}_{t,y,\ell,k} | Balance import extension | MW
    m.balance_import_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: Bal^{out}_{t,y,\ell,k} | Balance out-of-stock extension | MW
    m.balance_outofstock_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: Bal^{prim}_{t,y,\ell,k} | Balance EU Primary extension | MW
    m.balance_EU_primary_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: Bal^{sec}_{t,y,\ell,k} | Balance EU Secondary extension | MW
    m.balance_EU_secondary_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    """
    These Variables are used for the costs.py script constraints
    """
    # NOM: C^{new}_{type} | New cost components | EUR
    m.costs_new = pyomo.Var(m.cost_type_new, domain=pyomo.NonNegativeReals)

    # NOM: \xi^{imp}_{y,\ell,k} | Yearly import cost | EUR
    m.costs_ext_import = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: \xi^{stor}_{y,\ell,k} | Yearly storage cost | EUR
    m.costs_ext_storage = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: \xi^{eu-prim}_{y,\ell,k} | Yearly EU primary production cost | EUR
    m.costs_EU_primary = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: \xi^{eu-sec}_{y,\ell,k} | Yearly EU secondary production cost | EUR
    m.costs_EU_secondary = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    """
    These Variables are used for the economiesofscale_base.py script constraints.
    """
    # NOM: \delta_{y,\ell,k,n} | Binary decision variable for learning stage | {0/1}
    m.BD_sec = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        domain=pyomo.Binary,
        doc="Binary variable: 1 if stage is in learning step n, 0 otherwise"
    )

    # NOM: \hat{z}_{y,\ell,k,n} | Auxiliary variable for linearization | MW
    m.auxiliary_product_BD_q = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        within=pyomo.NonNegativeReals,
        doc="Auxiliary variable for linearizing BD_sec * capacity_produced_output",
    )

    # NOM: \Delta P_{y,\ell,k,n} | Unit Price Reduction | EUR/MW
    m.pricereduction_sec_investment = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,
        domain=pyomo.NonNegativeReals,
        doc="Current value of cost reduction (EUR/MW) based on active step"
    )

    # NOM: \Delta C_{y,\ell,k,n} | Total operational cost savings | EUR
    m.PRICEREDUCTION_CAP_DEP_INV = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,
        domain=pyomo.NonNegativeReals,
        doc="Total operational cost savings (EUR) due to learning effects"
    )

    """
    These Variables are used for the scrap.py script constraints.
    """
    # NOM: \hat{\pi}^{dec}_{y,\ell,k} | Decommissioned capacity | MW
    m.capacity_dec = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{scrap,dec}_{y,\ell,k} | Scrap generated from decommissioning | t
    m.capacity_scrap_dec = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{scrap,rec}_{y,\ell,k} | Scrap used for remanufacturing | t
    m.capacity_scrap_rec = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{scrap}_{y,\ell,k} | Total Scrap amount | t
    m.capacity_scrap_total = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \xi^{scrap}_{y,\ell,k} | Yearly scrap processing cost | EUR
    m.cost_scrap = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    """
    BESS variables
    """
    # NOM: D^{BESS}_{y,\ell} | Battery energy storage system proxy demand | MWh
    m.demand_bess = pyomo.Var(m.stf, m.location, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{sec,cum}_{y,\ell,k} | Cumulative Secondary Capacity | MW
    m.capacity_secondary_cumulative = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \hat{\pi}^{fac,cum}_{y,\ell,k} | Cumulative Facility Capacity | MW
    m.capacity_facility_cumulative = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    # NOM: \xi^{o\&m}_{y,\ell,k} | Yearly O&M cost | EUR
    m.costs_O_and_M = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    """
    Materials.py variables
    """
    # NOM: \hat{\pi}^{proc}_{y,\ell,k,s} | Total Processing Capacity | t/yr
    m.capacity_processing_total = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{proc,new}_{y,\ell,k,s} | New Processing Capacity | t/yr
    m.processing_cap_new = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{scrap,hand}_{y,\ell,k} | Scrap Handling Capacity Total | t/yr
    m.capacity_scrap_handling_total = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{scrap,hand,new}_{y,\ell,k} | New Scrap Handling Capacity | t/yr
    m.scraphandling_cap_new = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    # --- 2. PRODUCTION & FLOWS ---
    # NOM: \hat{\pi}^{prod}_{y,\ell,k,s} | Produced Output Capacity | MW
    m.capacity_produced_output = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{flow}_{y,\ell,k,s} | Produced Flow Capacity | MW
    m.capacity_produced_flow = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{prod,sto}_{y,\ell,k,s} | Produced Storage Capacity | MW
    m.capacity_produced_storage = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{prod,out}_{y,\ell,k,s} | Produced Stockout | MW
    m.capacity_produced_stockout = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # Import Splits
    # NOM: \hat{\pi}^{imp,total}_{y,\ell,k,s} | Total Imported Capacity | MW
    m.capacity_imported = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{imp,flow}_{y,\ell,k,s} | Imported Flow Capacity | MW
    m.capacity_imported_flow = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{imp,sto}_{y,\ell,k,s} | Imported Storage Capacity | MW
    m.capacity_imported_storage = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: \hat{\pi}^{imp,out}_{y,\ell,k,s} | Imported Stockout | MW
    m.capacity_imported_stockout = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: S_{y,\ell,k,s} | Supply Available for Next Stage | MW
    m.Supply = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # --- 3. STOCKPILES ---
    # NOM: Sto^{dom}_{y,\ell,k,s} | Domestic Stockpile | MW
    m.stock_domestic = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: Sto^{imp}_{y,\ell,k,s} | Imported Stockpile | MW
    m.stock_imported = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: R_{y,m} | Remaining Reserves | t
    m.remaining_reserves = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # NOM: Cap^{prim}_{y,m} | Primary Material Annual Capacity | t/yr
    m.primary_material_capacity_annual = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # NOM: Comp^{sto}_{y,\ell,k,s} | Components Stockpile | Units
    m.components_stockpile = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # --- 4. MATERIAL FLOWS ---
    # NOM: D^{mat}_{y,m} | Total Material Demand | t
    m.demand_material_total = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # NOM: M^{mined}_{y,m} | Material Mined | t
    m.material_mined = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # NOM: M^{imp}_{y,m} | Material Imported | t
    m.material_imported = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # NOM: M^{rec}_{y,m} | Material Recycled | t
    m.material_recycled = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # NOM: D^{prod}_{t,y,\ell,k} | Electricity demand for manufacturing | MWh
    m.demand_production = pyomo.Var(
        m.timesteps_ext,
        m.stf,
        m.location,
        m.tech,
        within=pyomo.NonNegativeReals,
        doc="Electricity demand for manufacturing per stage (MWh)"
    )

    # --- 5. COSTS ---
    # NOM: C^{capex}_{y} | Total CAPEX Extension | EUR
    m.cost_capex_total_extension = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)

    # NOM: C^{opex}_{y} | Total OPEX Extension | EUR
    m.cost_opex_total_extension = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)

    # NOM: C^{trade}_{y} | Total Trade Cost Extension | EUR
    m.cost_trade_total_extension = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)

    # NOM: C^{hold}_{y} | Stockpile Holding Cost | EUR
    m.cost_stockpile_holding = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)

    # NOM: NZIA^{short}_{y,\ell,k,s} | NZIA Shortfall | Units
    m.nzia_shortfall = pyomo.Var(
        m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # NOM: E^{fac}_{y,\ell,k} | Factory Energy Annual | MWh
    m.FACTORY_ENERGY_ANNUAL = pyomo.Var(
        m.stf, m.location, m.tech,
        domain=pyomo.NonNegativeReals
    )

    # NOM: Bal^{new}_{y,\ell,k} | Balance Yearly New Capacity | MW
    m.balance_yearly_new_capacity = pyomo.Var(m.stf, m.location, m.tech, within=pyomo.NonNegativeReals)

    #########################
    # Scrap Economies of Scale Variables
    #########################
    # NOM: \hat{z}^{scrap}_{y,\ell,k,n} | Aux Variable Scrap | -
    m.ap_BDV_scrap = pyomo.Var(
        m.stf, m.location, m.tech, m.nsteps_sec, within=pyomo.NonNegativeReals
    )

    # NOM: \Delta P^{scrap}_{y,\ell,k} | Price Reduction Scrap | EUR
    m.pricereduction_scrap = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    # NOM: \delta^{scrap}_{y,\ell,k,n} | Binary Variable Scrap | {0/1}
    m.BDV_scrap = pyomo.Var(
        m.stf, m.location, m.tech, m.nsteps_sec, domain=pyomo.Binary
    )

    # NOM: \Delta P^{stage}_{y,\ell,k} | Price Reduction Stage | EUR
    m.pricereduction_stage = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )