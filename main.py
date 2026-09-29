"""
Bio-Velocity Equilibrium Framework (BVEF) Reference Engine.

A self-contained quantitative architecture coupling dynamic hospitality pricing,
carrying-capacity velocity bounds, ecosystem degradation liability penalties,
and enterprise asset valuation adjustments.

Author: Pathirannehelage Gayan Nugawela
Year: 2026
License: MIT
"""

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ==============================================================================
# Model Entities & Enums
# ==============================================================================

class EcologicalRegime(Enum):
    REGENERATIVE = "REGENERATIVE"           # Instantaneous load <= carrying capacity
    TRANSITIONAL = "TRANSITIONAL"           # Minor carrying capacity overshoot, absorbable
    CRITICAL_OVERBURDEN = "CRITICAL_OVERBURDEN"  # Structural degradation regime


@dataclass(frozen=True)
class EcosystemParameters:
    """Parameters governing natural asset carrying capacity, recovery, and valuation."""
    nominal_carrying_capacity: float        # Sustainable daily/cycle guest footprint (units)
    regeneration_rate_gamma: float          # Environmental restoration velocity (0 < gamma < 1)
    degradation_cost_coefficient_alpha: float  # Marginal cash restoration penalty ($/excess unit)
    degradation_exponent_theta: float       # Non-linear stress penalty scaling (theta >= 1.0)
    asset_base_valuation: float             # Baseline enterprise asset valuation ($)
    valuation_beta_sensitivity: float       # Cap-rate discount sensitivity to cumulative stress
    valuation_floor_omega: float            # Structural physical asset floor boundary ratio (0 < omega < 1)


@dataclass
class OperationalYieldState:
    """Operational cycle inputs for dynamic yield and displacement governance."""
    cycle_id: str
    available_units: int
    demanded_units: int
    base_unconstrained_rate: float
    marginal_cost_to_serve: float
    current_occupancy_ratio: float = 0.0

    def __post_init__(self):
        units_sold = min(self.available_units, self.demanded_units)
        self.current_occupancy_ratio = units_sold / self.available_units if self.available_units > 0 else 0.0


@dataclass
class BVEFExecutionResult:
    """Output metrics from the Bio-Velocity Equilibrium audit."""
    cycle_id: str
    occupied_units: int
    regime: EcologicalRegime
    bio_velocity_index: float
    cumulative_stress: float
    base_marginal_cost: float
    marginal_ecological_penalty: float
    adjusted_bvef_rate_floor: float
    recommended_bvef_rate: float
    gross_revenue: float
    direct_operating_costs: float
    ecosystem_degradation_penalty: float
    net_operating_cashflow: float
    adjusted_enterprise_valuation: float
    execution_time_us: float


# ==============================================================================
# BVEF Core Mathematical Engine
# ==============================================================================

class BioVelocityEquilibriumEngine:
    """
    Quantitative engine evaluating real-time dynamic pricing equilibrium against
    biophysical carrying capacity and long-term enterprise valuation constraints.
    """

    def __init__(self, params: EcosystemParameters):
        self.params = params

    def compute_bio_velocity_index(
        self, occupied_units: int, cumulative_stress: float
    ) -> Tuple[float, float, EcologicalRegime]:
        """
        Computes the instantaneous Bio-Velocity Index (B_t) and carries forward cumulative stress:
            Instantaneous Load L_t = U_t / K
            Stress Update S_t = max(0, S_{t-1} * (1 - gamma) + max(0, L_t - 1))
            Bio-Velocity Index B_t = L_t + S_t
        """
        instantaneous_load = occupied_units / self.params.nominal_carrying_capacity
        excess_ratio = max(0.0, instantaneous_load - 1.0)
        
        # Environmental recovery dynamics: stress decays by gamma, then absorbs new overshoot
        updated_stress = max(
            0.0,
            (cumulative_stress * (1.0 - self.params.regeneration_rate_gamma)) + excess_ratio
        )
        bio_velocity = instantaneous_load + updated_stress

        if bio_velocity <= 1.0:
            regime = EcologicalRegime.REGENERATIVE
        elif bio_velocity <= 1.35:
            regime = EcologicalRegime.TRANSITIONAL
        else:
            regime = EcologicalRegime.CRITICAL_OVERBURDEN

        return bio_velocity, updated_stress, regime

    def evaluate_cycle(
        self, state: OperationalYieldState, cumulative_stress: float
    ) -> BVEFExecutionResult:
        """
        Executes a deterministic cycle evaluation:
          1. Computes bio-velocity and stress states.
          2. Derives non-linear ecological degradation penalty.
          3. Establishes the BVEF dynamic marginal rate floor.
          4. Allocates market clearing rate using velocity rationing.
          5. Computes net adjusted operating cash flow and discounted asset valuation.
        """
        t0 = time.perf_counter_ns()

        units_sold = min(state.available_units, state.demanded_units)
        b_idx, updated_stress, regime = self.compute_bio_velocity_index(units_sold, cumulative_stress)

        # 1. Marginal Ecological Liability Penalty
        excess_units = max(0.0, units_sold - self.params.nominal_carrying_capacity)
        if excess_units > 0.0:
            degradation_penalty = self.params.degradation_cost_coefficient_alpha * (
                excess_units ** self.params.degradation_exponent_theta
            )
            marginal_ecological_cost = degradation_penalty / units_sold
        else:
            degradation_penalty = 0.0
            marginal_ecological_cost = 0.0

        # 2. Dynamic Marginal Rate Floor (BVEF Floor)
        # Guarantees rate covers both direct cost-to-serve and ecological restoration liabilities
        bvef_rate_floor = state.marginal_cost_to_serve + marginal_ecological_cost

        # 3. Dynamic Market Equilibrium Rate
        if b_idx > 1.0:
            # Shift pricing upward via log-velocity multiplier to ration demand away from overload
            velocity_multiplier = 1.0 + math.log(b_idx)
            recommended_rate = max(bvef_rate_floor, state.base_unconstrained_rate * velocity_multiplier)
        else:
            recommended_rate = max(bvef_rate_floor, state.base_unconstrained_rate)

        # 4. Cash Flow and Enterprise Valuation Mechanics
        gross_revenue = units_sold * recommended_rate
        direct_costs = units_sold * state.marginal_cost_to_serve
        net_cashflow = gross_revenue - direct_costs - degradation_penalty

        # Valuation discount due to cumulative carrying capacity degradation
        valuation_discount = self.params.valuation_beta_sensitivity * updated_stress
        adjusted_valuation = self.params.asset_base_valuation * max(
            self.params.valuation_floor_omega, (1.0 - valuation_discount)
        )

        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0

        return BVEFExecutionResult(
            cycle_id=state.cycle_id,
            occupied_units=units_sold,
            regime=regime,
            bio_velocity_index=round(b_idx, 4),
            cumulative_stress=round(updated_stress, 4),
            base_marginal_cost=round(state.marginal_cost_to_serve, 2),
            marginal_ecological_penalty=round(marginal_ecological_cost, 2),
            adjusted_bvef_rate_floor=round(bvef_rate_floor, 2),
            recommended_bvef_rate=round(recommended_rate, 2),
            gross_revenue=round(gross_revenue, 2),
            direct_operating_costs=round(direct_costs, 2),
            ecosystem_degradation_penalty=round(degradation_penalty, 2),
            net_operating_cashflow=round(net_cashflow, 2),
            adjusted_enterprise_valuation=round(adjusted_valuation, 2),
            execution_time_us=round(elapsed_us, 2)
        )


# ==============================================================================
# Benchmarking & Multi-Cycle Simulation Suite
# ==============================================================================

def run_bvef_comprehensive_suite():
    print("=" * 86)
    print("BIO-VELOCITY EQUILIBRIUM FRAMEWORK (BVEF) REFERENCE ENGINE")
    print("Ecosystem Carrying Capacity & Dynamic Yield Valuation Simulation")
    print("=" * 86)

    # Asset Baseline Configuration
    eco_params = EcosystemParameters(
        nominal_carrying_capacity=100.0,          # 100 rooms/guests sustainable threshold
        regeneration_rate_gamma=0.15,             # 15% natural regeneration velocity per operational cycle
        degradation_cost_coefficient_alpha=45.0,  # Baseline restoration cost ($45 per excess unit)
        degradation_exponent_theta=1.35,          # Non-linear degradation compounding
        asset_base_valuation=60_000_000.0,        # $60,000,000 baseline luxury eco-resort asset value
        valuation_beta_sensitivity=0.075,         # 7.5% cap-rate adjustment per stress index unit
        valuation_floor_omega=0.25                # 25% minimum structural liquidation floor
    )

    engine = BioVelocityEquilibriumEngine(eco_params)

    # Consecutive operational cycles: Nominal -> Capacity Ceiling -> Overburden -> Extreme Stress -> Recovery
    cycle_scenarios = [
        OperationalYieldState("Cycle-1-Nominal-Demand", 120, 75, 320.0, 120.0),
        OperationalYieldState("Cycle-2-Capacity-Threshold", 120, 100, 340.0, 120.0),
        OperationalYieldState("Cycle-3-High-Overshoot", 120, 118, 350.0, 120.0),
        OperationalYieldState("Cycle-4-Peak-Overburden", 120, 120, 360.0, 120.0),
        OperationalYieldState("Cycle-5-Post-Peak-Cooldown", 120, 60, 300.0, 120.0),
    ]

    cumulative_stress = 0.0

    for idx, cycle in enumerate(cycle_scenarios, start=1):
        res = engine.evaluate_cycle(cycle, cumulative_stress)
        cumulative_stress = res.cumulative_stress

        print(f"\n[{cycle.cycle_id}] | Regime: {res.regime.value}")
        print(f"  Physical Occupancy     : {res.occupied_units} / {cycle.available_units} units (Capacity: {eco_params.nominal_carrying_capacity:.0f})")
        print(f"  Bio-Velocity Index     : {res.bio_velocity_index:.4f} | Carryover Stress: {res.cumulative_stress:.4f}")
        print(f"  Base Unconstrained Rate: ${cycle.base_unconstrained_rate:.2f} --> Recommended BVEF Rate: ${res.recommended_bvef_rate:.2f}")
        print(f"  Dynamic Rate Floor     : ${res.adjusted_bvef_rate_floor:.2f} (Direct Cost: ${res.base_marginal_cost:.2f} + Eco Penalty: ${res.marginal_ecological_penalty:.2f})")
        print(f"  Gross Revenue          : ${res.gross_revenue:,.2f}")
        print(f"  Direct Operating Costs : ${res.direct_operating_costs:,.2f}")
        print(f"  Ecosystem Degradation  : -${res.ecosystem_degradation_penalty:,.2f}")
        print(f"  Net Operating Cash Flow: ${res.net_operating_cashflow:,.2f}")
        print(f"  Enterprise Valuation   : ${res.adjusted_enterprise_valuation:,.2f}")
        print(f"  Verification Latency   : {res.execution_time_us:.2f} µs")

    # High-frequency stress benchmark
    print("\n" + "-" * 86)
    print("Benchmarking 10,000 Consecutive BVEF Real-Time Audit Cycles...")
    
    benchmark_state = OperationalYieldState("Benchmark-Cycle", 120, 110, 330.0, 120.0)
    latencies = []
    bench_stress = 0.0

    for _ in range(10_000):
        t_start = time.perf_counter_ns()
        result = engine.evaluate_cycle(benchmark_state, bench_stress)
        elapsed_us = (time.perf_counter_ns() - t_start) / 1000.0
        latencies.append(elapsed_us)
        bench_stress = result.cumulative_stress

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"  P50 (Median Latency)   : {p50:.2f} µs")
    print(f"  P95 Latency            : {p95:.2f} µs")
    print(f"  P99 Latency            : {p99:.2f} µs")
    print("=" * 86)


if __name__ == "__main__":
    run_bvef_comprehensive_suite()
