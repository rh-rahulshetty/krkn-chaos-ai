from krkn_ai.models.scenario.base import Scenario
from krkn_ai.models.scenario.parameters import (
    DummyEndParameter,
    DummyExitStatusParameter,
)


class DummyScenario(Scenario):
    name: str = "dummy-scenario"
    krknctl_name: str = "dummy-scenario"
    krknhub_image: str = "containers.krkn-chaos.dev/krkn-chaos/krkn-hub:dummy-scenario"

    end: DummyEndParameter = DummyEndParameter()
    exit_status: DummyExitStatusParameter = DummyExitStatusParameter()

    def __init__(self, **data):
        super().__init__(**data)

    @property
    def parameters(self):
        return [
            self.end,
            self.exit_status,
        ]

    def mutate(self):
        pass
