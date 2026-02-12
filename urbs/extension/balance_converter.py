from abc import ABC, abstractmethod
import pyomo.core as pyomo


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, timesteps_ext, stf, location, tech):
        pass


class ConvertTotalCapacityToBalance(AbstractConstraint):
    def apply_rule(self, m, timesteps_ext, stf, location, tech):
        """
        Calculates the actual power generation based on installed capacity and solar profiles.
        """
        # CON: Solar Balance Conversion | Constrains generation profile based on capacity and solar load factor
        balance_value = (
                m.capacity_ext[stf, location, tech]
                * m.lf_solar[timesteps_ext, stf, location, tech]
                * m.hours[timesteps_ext]
        )
        # print(
        #    f"Debug: time = {timesteps_ext}, STF = {stf}, Location = {location}, Tech = {tech}"
        # )
        # print(f"Total Capacity to Balance (Solar) = {balance_value}")
        return m.balance_ext[timesteps_ext, stf, location, tech] == balance_value


def apply_balance_constraints(m):
    constraints = [
        ConvertTotalCapacityToBalance(),
    ]

    for i, constraint in enumerate(constraints):
        constraint_name = f"balance_constraint_{i + 1}"

        # We attach the constraint to the model dynamically
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.timesteps_ext,
                m.stf,
                m.location,
                m.tech,
                rule=lambda m, timesteps_ext, stf, loc, tech: constraint.apply_rule(
                    m, timesteps_ext, stf, loc, tech
                ),
            ),
        )