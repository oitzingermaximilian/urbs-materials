import pyomo.environ as pyomo
from abc import ABC, abstractmethod


def setup_split_scrap_learning(m):
    """
    Sets up two specific learning curves:
    1. Solar: Driven by capacity_scrap_rec for solarPV.
    2. Wind: Driven by sum of capacity_scrap_magnet_route for windon and windoff.
    Bulk recycling gets no learning curve.
    """
    m.tech_scrap_solar = pyomo.Set(initialize=["solarPV"])
    m.tech_scrap_wind = pyomo.Set(initialize=["windon", "windoff"])

    # ==============================================================================
    # 1. VARIABLE DEFINITIONS
    # ==============================================================================

    # --- SOLAR VARIABLES ---
    m.BD_scrap_solar = pyomo.Var(
        m.stf, m.location, m.nsteps_sec,
        domain=pyomo.Binary
    )
    
    m.aux_scrap_solar = pyomo.Var(
        m.stf, m.location, m.nsteps_sec,
        within=pyomo.NonNegativeReals
    )
    
    m.pricereduction_scrap_solar_unit = pyomo.Var(
        m.stf, m.location,
        domain=pyomo.NonNegativeReals
    )

    # --- WIND MAGNET VARIABLES ---
    # Shared binary for windon and windoff
    m.BD_scrap_wind = pyomo.Var(
        m.stf, m.location, m.nsteps_sec,
        domain=pyomo.Binary
    )
    
    # Split aux variables so savings can be properly assigned to each tech
    m.aux_scrap_windon = pyomo.Var(
        m.stf, m.location, m.nsteps_sec,
        within=pyomo.NonNegativeReals
    )
    
    m.aux_scrap_windoff = pyomo.Var(
        m.stf, m.location, m.nsteps_sec,
        within=pyomo.NonNegativeReals
    )
    
    m.pricereduction_scrap_wind_unit = pyomo.Var(
        m.stf, m.location,
        domain=pyomo.NonNegativeReals
    )
    
    # --- TOTAL CAPACITY-BASED SAVINGS ---
    # These represent sum(P_sec * aux). In scrap.py, they will be multiplied by the constant weight.
    m.PRICEREDUCTION_SCRAP_SOLAR_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_SOLAR_CAPEX_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_SOLAR_FOM_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_WINDON_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_WINDON_CAPEX_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_WINDON_FOM_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_WINDOFF_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_WINDOFF_CAPEX_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )
    
    m.PRICEREDUCTION_SCRAP_WINDOFF_FOM_CAP_BASED = pyomo.Var(
        m.stf, m.location,
        within=pyomo.NonNegativeReals
    )

    # ==============================================================================
    # 2. CONSTRAINTS FOR SOLAR
    # ==============================================================================
    
    def rule_solar_unit(m, stf, loc):
        val = sum(m.P_sec_recycling_solar[loc, n] * m.BD_scrap_solar[stf, loc, n] for n in m.nsteps_sec)
        return m.pricereduction_scrap_solar_unit[stf, loc] == val
    m.scrap_solar_constr_unit = pyomo.Constraint(m.stf, m.location, rule=rule_solar_unit)
    
    def rule_solar_total(m, stf, loc):
        val = sum(m.P_sec_recycling_solar[loc, n] * m.aux_scrap_solar[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_SOLAR_CAP_BASED[stf, loc] == val
    m.scrap_solar_constr_total = pyomo.Constraint(m.stf, m.location, rule=rule_solar_total)
    
    def rule_solar_total_capex(m, stf, loc):
        val = sum(m.P_sec_recycling_capex_solar[loc, n] * m.aux_scrap_solar[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_SOLAR_CAPEX_CAP_BASED[stf, loc] == val
    m.scrap_solar_constr_total_capex = pyomo.Constraint(m.stf, m.location, rule=rule_solar_total_capex)

    def rule_solar_total_fom(m, stf, loc):
        val = sum(m.P_sec_recycling_fom_solar[loc, n] * m.aux_scrap_solar[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_SOLAR_FOM_CAP_BASED[stf, loc] == val
    m.scrap_solar_constr_total_fom = pyomo.Constraint(m.stf, m.location, rule=rule_solar_total_fom)
    
    def rule_solar_limit(m, stf, loc):
        return sum(m.BD_scrap_solar[stf, loc, n] for n in m.nsteps_sec) == 1
    m.scrap_solar_constr_limit = pyomo.Constraint(m.stf, m.location, rule=rule_solar_limit)
    
    def rule_solar_mono(m, stf, loc):
        if stf == min(m.stf):
            return pyomo.Constraint.Skip
        return m.pricereduction_scrap_solar_unit[stf, loc] >= m.pricereduction_scrap_solar_unit[stf - 1, loc]
    m.scrap_solar_constr_mono = pyomo.Constraint(m.stf, m.location, rule=rule_solar_mono)
    
    def rule_solar_trigger(m, stf, loc):
        y0 = min(m.stf)
        cumulative_cap = m.total_recycling_cap_initial[loc, "solarPV"] + sum(
            m.capacity_scrap_rec[year, loc, "solarPV"] for year in m.stf if y0 <= year <= stf
        )
        active_threshold = sum(m.BD_scrap_solar[stf, loc, n] * m.tons_perstep_recycling[loc, "solarPV", n] for n in m.nsteps_sec)
        return cumulative_cap >= active_threshold
    m.scrap_solar_constr_trig = pyomo.Constraint(m.stf, m.location, rule=rule_solar_trigger)

    def rule_solar_aux_upper_M(m, stf, loc, n):
        return m.aux_scrap_solar[stf, loc, n] <= m.gamma_scrap * m.BD_scrap_solar[stf, loc, n]
    m.scrap_solar_aux_upper_M = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_solar_aux_upper_M)

    def rule_solar_aux_upper_cap(m, stf, loc, n):
        return m.aux_scrap_solar[stf, loc, n] <= m.capacity_scrap_rec[stf, loc, "solarPV"]
    m.scrap_solar_aux_upper_cap = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_solar_aux_upper_cap)

    def rule_solar_aux_lower(m, stf, loc, n):
        return m.aux_scrap_solar[stf, loc, n] >= m.capacity_scrap_rec[stf, loc, "solarPV"] - (1 - m.BD_scrap_solar[stf, loc, n]) * m.gamma_scrap
    m.scrap_solar_aux_lower = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_solar_aux_lower)


    # ==============================================================================
    # 3. CONSTRAINTS FOR WIND (MAGNET ROUTE)
    # ==============================================================================
    
    def rule_wind_unit(m, stf, loc):
        # We only need one unit price reduction value because it's the same chemical process for both
        val = sum(m.P_sec_recycling_wind[loc, n] * m.BD_scrap_wind[stf, loc, n] for n in m.nsteps_sec)
        return m.pricereduction_scrap_wind_unit[stf, loc] == val
    m.scrap_wind_constr_unit = pyomo.Constraint(m.stf, m.location, rule=rule_wind_unit)
    
    def rule_windon_total(m, stf, loc):
        val = sum(m.P_sec_recycling_wind[loc, n] * m.aux_scrap_windon[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_WINDON_CAP_BASED[stf, loc] == val
    m.scrap_windon_constr_total = pyomo.Constraint(m.stf, m.location, rule=rule_windon_total)
    
    def rule_windon_total_capex(m, stf, loc):
        val = sum(m.P_sec_recycling_capex_wind[loc, n] * m.aux_scrap_windon[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_WINDON_CAPEX_CAP_BASED[stf, loc] == val
    m.scrap_windon_constr_total_capex = pyomo.Constraint(m.stf, m.location, rule=rule_windon_total_capex)

    def rule_windon_total_fom(m, stf, loc):
        val = sum(m.P_sec_recycling_fom_wind[loc, n] * m.aux_scrap_windon[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_WINDON_FOM_CAP_BASED[stf, loc] == val
    m.scrap_windon_constr_total_fom = pyomo.Constraint(m.stf, m.location, rule=rule_windon_total_fom)
    
    def rule_windoff_total(m, stf, loc):
        val = sum(m.P_sec_recycling_wind[loc, n] * m.aux_scrap_windoff[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_WINDOFF_CAP_BASED[stf, loc] == val
    m.scrap_windoff_constr_total = pyomo.Constraint(m.stf, m.location, rule=rule_windoff_total)

    def rule_windoff_total_capex(m, stf, loc):
        val = sum(m.P_sec_recycling_capex_wind[loc, n] * m.aux_scrap_windoff[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_WINDOFF_CAPEX_CAP_BASED[stf, loc] == val
    m.scrap_windoff_constr_total_capex = pyomo.Constraint(m.stf, m.location, rule=rule_windoff_total_capex)

    def rule_windoff_total_fom(m, stf, loc):
        val = sum(m.P_sec_recycling_fom_wind[loc, n] * m.aux_scrap_windoff[stf, loc, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_SCRAP_WINDOFF_FOM_CAP_BASED[stf, loc] == val
    m.scrap_windoff_constr_total_fom = pyomo.Constraint(m.stf, m.location, rule=rule_windoff_total_fom)
    
    def rule_wind_limit(m, stf, loc):
        return sum(m.BD_scrap_wind[stf, loc, n] for n in m.nsteps_sec) == 1
    m.scrap_wind_constr_limit = pyomo.Constraint(m.stf, m.location, rule=rule_wind_limit)
    
    def rule_wind_mono(m, stf, loc):
        if stf == min(m.stf):
            return pyomo.Constraint.Skip
        return m.pricereduction_scrap_wind_unit[stf, loc] >= m.pricereduction_scrap_wind_unit[stf - 1, loc]
    m.scrap_wind_constr_mono = pyomo.Constraint(m.stf, m.location, rule=rule_wind_mono)
    
    def rule_wind_trigger(m, stf, loc):
        y0 = min(m.stf)
        # Combine windon and windoff for cumulative capacity, only counting magnet route!
        cumulative_cap = m.total_recycling_cap_initial[loc, "windon"] + m.total_recycling_cap_initial[loc, "windoff"] + sum(
            m.capacity_scrap_magnet_route[year, loc, "windon"] + m.capacity_scrap_magnet_route[year, loc, "windoff"]
            for year in m.stf if y0 <= year <= stf
        )
        
        # Use windon for the threshold tons_perstep, assuming they are identical in parameters
        active_threshold = sum(m.BD_scrap_wind[stf, loc, n] * m.tons_perstep_recycling[loc, "windon", n] for n in m.nsteps_sec)
        return cumulative_cap >= active_threshold
    m.scrap_wind_constr_trig = pyomo.Constraint(m.stf, m.location, rule=rule_wind_trigger)

    # --- WINDON AUX LINEARIZATIONS ---
    def rule_windon_aux_upper_M(m, stf, loc, n):
        return m.aux_scrap_windon[stf, loc, n] <= m.gamma_scrap * m.BD_scrap_wind[stf, loc, n]
    m.scrap_windon_aux_upper_M = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_windon_aux_upper_M)

    def rule_windon_aux_upper_cap(m, stf, loc, n):
        return m.aux_scrap_windon[stf, loc, n] <= m.capacity_scrap_magnet_route[stf, loc, "windon"]
    m.scrap_windon_aux_upper_cap = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_windon_aux_upper_cap)

    def rule_windon_aux_lower(m, stf, loc, n):
        return m.aux_scrap_windon[stf, loc, n] >= m.capacity_scrap_magnet_route[stf, loc, "windon"] - (1 - m.BD_scrap_wind[stf, loc, n]) * m.gamma_scrap
    m.scrap_windon_aux_lower = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_windon_aux_lower)

    # --- WINDOFF AUX LINEARIZATIONS ---
    def rule_windoff_aux_upper_M(m, stf, loc, n):
        return m.aux_scrap_windoff[stf, loc, n] <= m.gamma_scrap * m.BD_scrap_wind[stf, loc, n]
    m.scrap_windoff_aux_upper_M = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_windoff_aux_upper_M)

    def rule_windoff_aux_upper_cap(m, stf, loc, n):
        return m.aux_scrap_windoff[stf, loc, n] <= m.capacity_scrap_magnet_route[stf, loc, "windoff"]
    m.scrap_windoff_aux_upper_cap = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_windoff_aux_upper_cap)

    def rule_windoff_aux_lower(m, stf, loc, n):
        return m.aux_scrap_windoff[stf, loc, n] >= m.capacity_scrap_magnet_route[stf, loc, "windoff"] - (1 - m.BD_scrap_wind[stf, loc, n]) * m.gamma_scrap
    m.scrap_windoff_aux_lower = pyomo.Constraint(m.stf, m.location, m.nsteps_sec, rule=rule_windoff_aux_lower)
