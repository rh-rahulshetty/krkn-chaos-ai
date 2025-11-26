import re

from krkn_ai.models.app import CommandRunResult

_INVALID_FILENAME_CHARS = re.compile(r'[^A-Za-z0-9._-]')


def _sanitize_filename_component(value: str) -> str:
    """Replace characters that are unsafe for filenames."""
    return _INVALID_FILENAME_CHARS.sub('_', value)


def format_result_filename(fmt: str, command_result: CommandRunResult) -> str:
    """
    Format output filename using placeholders from a CommandRunResult.

    Supported placeholders:
    - %g: Generation ID
    - %s: Scenario ID
    - %c: Scenario Name
    """
    scenario_name = getattr(command_result.scenario, "name", "") or ""
    safe_name = _sanitize_filename_component(str(scenario_name))
    return (
        fmt.replace('%g', str(command_result.generation_id))
           .replace('%s', str(command_result.scenario_id))
           .replace('%c', safe_name)
    )

