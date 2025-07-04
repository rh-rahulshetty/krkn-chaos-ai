from pydantic import BaseModel
import datetime
from enum import Enum

from chaos_ai.models.base_scenario import BaseScenario


class CommandRunResult(BaseModel):
    generation_id: int      # Which generation was scenario referred
    scenario: BaseScenario  # scenario details
    cmd: str                # Krkn-Hub command 
    log: str                # Log details or path to log file
    returncode: int         # Return code of Krkn-Hub scenario execution
    start_time: datetime.datetime   # Start date timestamp of the test 
    end_time: datetime.datetime     # End date timestamp of the test
    fitness_score: float            # Overall fitness score measured for scenario.


class KrknRunnerType(str, Enum):
    HUB_RUNNER = "HUB_RUNNER"
    CLI_RUNNER = "CLI_RUNNER"
