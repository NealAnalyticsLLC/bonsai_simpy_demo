inkling "2.0"

using Goal


type SimState {
    simulation_time: number,
    num_beds: number,
    num_patients: number,
    num_patients_overflow: number,
    utilization: number,
}


type SimAction {
    change_beds: number<-20, -10, 0, 10, 20>,
}


type SimConfig {
    initial_beds: number<200 .. 300>,
    initial_patients: number<0 .. 100>,
}


simulator HospitalSim (Action: SimAction, Config: SimConfig): SimState {
    # Automatically launch the simulator with this registered package name.
    package "Hospital"
}


graph (input: SimState): SimAction {

    concept ControlBeds(input): SimAction {
        curriculum {

            source HospitalSim

            training {
                EpisodeIterationLimit: 2 * 365, # default is 1,000
            }

            goal (State: SimState) {

                drive OptimalUtilization:
                    State.utilization
                    in Goal.Range(0.7, 0.9)
                    within 14

            }

            lesson StaticStart {
                scenario {
                    initial_beds: 200,
                    initial_patients: 0
                }
            }

            lesson RandomizeStart {
                scenario {
                    initial_beds: number<200, 240, 260, 280, 300>,
                    initial_patients: 0
                }
            }

        }
    }
}
