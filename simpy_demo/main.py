import json
import os
import time
from typing import Dict

import dotenv
from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface,
    SimulatorState,
    SimulatorSessionResponse,
)

import hospital_sim


DEFAULT_CONFIG = {"initial_beds": 200, "initial_patients": 0}


class TemplateSimulatorSession:
    def __init__(self) -> None:
        self.sim = hospital_sim.HospitalSim(**DEFAULT_CONFIG)

    def episode_start(self, config: Dict = None) -> None:
        if config is None:
            config = DEFAULT_CONFIG

        self.sim.reset(**config)

    def episode_step(self, action: Dict) -> None:
        self.sim.step(Δnum_beds=action["change_beds"])

    def get_state(self) -> Dict:
        return self.sim.get_current_state()

    def halted(self) -> bool:
        return False


def get_workspace_config() -> BonsaiClientConfig:
    dotenv.load_dotenv(override=True)

    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    if workspace is None:
        raise ValueError("The Bonsai workspace ID is not set.")
    if access_key is None:
        raise ValueError("The access key for the Bonsai workspace is not set.")

    return BonsaiClientConfig(workspace=workspace, access_key=access_key)


def get_sim_interface(simulator_context) -> SimulatorInterface:
    """Register sim interface."""

    with open("interface.json", mode="r", encoding="ascii") as infile:
        interface = json.load(infile)

    return SimulatorInterface(
        name=interface["name"],
        timeout=interface["timeout"],
        simulator_context=simulator_context,
        description=interface["description"],
    )


def get_session_id(client_config, client) -> str:
    registration_info = get_sim_interface(
        simulator_context=client_config.simulator_context
    )

    registered_session: SimulatorSessionResponse = client.session.create(
        workspace_name=client_config.workspace, body=registration_info
    )

    session_id = registered_session.session_id

    print(f"Registered simulator. {session_id}")
    return session_id


def main():

    client_config = get_workspace_config()
    client = BonsaiClient(client_config)
    session_id = get_session_id(client_config=client_config, client=client)

    sequence_id = 1

    sim = TemplateSimulatorSession()

    try:
        while True:

            bonsai_state = SimulatorState(
                sequence_id=sequence_id, state=sim.get_state(), halted=False,
            )

            event = client.session.advance(
                workspace_name=client_config.workspace,
                session_id=session_id,
                body=bonsai_state,
            )

            sequence_id = event.sequence_id

            print(f'[{time.strftime("%H:%M:%S")}] Last Event: {event.type}')

            if event.type == "Idle":
                time.sleep(event.idle.callback_time)
            elif event.type == "EpisodeStart":
                sim.episode_start(config=event.episode_start.config)
            elif event.type == "EpisodeStep":
                sim.episode_step(action=event.episode_step.action)
            elif event.type == "Unregister":
                print(f"Unregistered simulator because {event.unregister.details}")
                return
    except BaseException as err:
        client.session.delete(
            workspace_name=client_config.workspace, session_id=session_id,
        )
        print(f"Unregistered simulator because {type(err).__name__}: {err}")


if __name__ == "__main__":
    main()
