from typing import Dict

from matplotlib import pyplot as plt
import numpy as np

import hospital_sim as hs


def run_sim(runtime_days: int) -> Dict:

    sim = hs.HospitalSim(initial_patients=0, initial_beds=200)

    states = []

    for _ in range(runtime_days):

        state = sim.get_current_state()
        states.append(state)

        utilization = state["utilization"]

        if utilization >= 0.9:
            Δnum_beds = +25
        elif utilization < 0.7:
            Δnum_beds = -10
        else:
            Δnum_beds = 0

        # NOTE: it takes 1 day to change the number of beds
        sim.step(Δnum_beds=Δnum_beds)

    return states


def plot_sim_results(runtime_days: int):

    states = run_sim(runtime_days=runtime_days)

    times = [state["simulation_time"] for state in states]
    num_beds_over_time = [state["num_beds"] for state in states]
    num_patients_over_time = [state["num_patients"] for state in states]
    num_overflow_over_time = [state["num_patients_overflow"] for state in states]
    utilization_over_time = [state["utilization"] for state in states]

    _, (ax0, ax1) = plt.subplots(
        nrows=2, ncols=1, sharex=True, figsize=(12, 6), dpi=160
    )

    # plot the number of patients and beds over time
    ax0.scatter(times, num_beds_over_time, s=16, label="# of beds")
    ax0.scatter(times, num_patients_over_time, s=16, label="# of patients")
    ax0.scatter(times, num_overflow_over_time, s=16, label="# of overflow patients")
    ax0.legend(loc=(0.7718, 0.12))
    ax0.grid(linewidth=0.2)

    # color utilization by whether it falls in the target range
    colors = ["C2" if 0.7 <= point <= 0.9 else "C3" for point in utilization_over_time]

    # plot utilization over time
    ax1.scatter(
        times, utilization_over_time, s=16, c=colors, label="utilization (actual)"
    )

    # plot target utilization range
    N = 100
    ax1.fill_between(
        x=np.linspace(0, runtime_days, N),
        y1=0.7 * np.ones(N),
        y2=0.9 * np.ones(N),
        color="gray",
        alpha=0.25,
        label="utilization (target)",
    )

    ax1.set_xlabel("Simulation Time (days)")
    ax1.legend(loc="lower right")
    ax1.grid(linewidth=0.2)

    plt.savefig("demo.png")


if __name__ == "__main__":

    plot_sim_results(runtime_days=2 * 30)
