from abc import ABC, abstractmethod
import pyomo.core as pyomo
from pyomo.environ import value


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, stf, location, tech):
        pass


DEBUG = False  # Set to False to disable all debug prints


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class CapacityExtGrowthRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Capacity Growth Balance | Tracks installed capacity evolution (New - Decommissioned)
        if stf == value(m.y0):
            debug_print(
                f"Running constraint CapacityExtGrowthRule for stf={stf} (start year)"
            )
            return (
                m.capacity_ext[stf, location, tech]
                == m.Installed_Capacity_Q_s[location, tech]
                + m.capacity_ext_new[stf, location, tech]
                - m.capacity_dec[stf, location, tech]
            )
        else:
            debug_print(
                f"Running constraint CapacityExtGrowthRule for stf={stf} (inside intervall)"
            )
            return (
                m.capacity_ext[stf, location, tech]
                == m.capacity_ext[stf - 1, location, tech]
                + m.capacity_ext_new[stf, location, tech]
                - m.capacity_dec[stf, location, tech]
            )


class CapacityExtNewLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: New Capacity Limit | Restricts annual new capacity to defined installable limits
        cap_val = m.capacity_ext_new[stf, location, tech]
        if stf == 2024:
            ext_val = m.Q_ext_new[stf, location, tech]
            return cap_val <= ext_val
        else:
            ext_val = m.Q_ext_new[stf, location, tech]
            return cap_val <= ext_val


class ConstraintBatteryDemandRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: BESS Demand Calculation | Calculates required BESS capacity based on other tech installations
        lhs = m.demand_bess[stf, location]
        rhs = sum(
            m.factor_bess[location, t] * m.capacity_ext_new[stf, location, t]
            for t in m.tech
            if t != "Batteries"
        )
        debug_print(f"Caluclating battery demand for {stf}: demand = {rhs}")
        return lhs == rhs


class ConstraintBatteryCapRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: BESS Capacity Requirement | Ensures BESS installations meet the calculated demand
        lhs = m.demand_bess[stf, location]
        rhs = m.capacity_ext_new[stf, location, "Batteries"]

        debug_print(
            f"Battery cap constraint for {stf}, {location}: lhs demand = {lhs}, rhs battery cap = {rhs}"
        )
        return lhs <= rhs


def apply_stockpiling_constraints(m):
    """
    Applies the cleaned list of stockpile and capacity constraints.
    """
    constraints = [
        CapacityExtGrowthRule(),
        CapacityExtNewLimitRule(),
        ConstraintBatteryDemandRule(),
        ConstraintBatteryCapRule(),
    ]

    for constraint_obj in constraints:
        # Use class name for clearer constraint naming in Pyomo
        name = constraint_obj.__class__.__name__
        setattr(
            m,
            name,
            pyomo.Constraint(
                m.stf,
                m.location,
                m.tech,
                rule=lambda m, stf, loc, tech: constraint_obj.apply_rule(m, stf, loc, tech),
            ),
        )

    print("Stockpiling constraints applied successfully.")