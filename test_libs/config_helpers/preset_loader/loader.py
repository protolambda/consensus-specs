from typing import Dict, Any

from ruamel.yaml import (
    YAML,
)
from pathlib import Path


def load_presets(presets_name) -> Dict[str, Any]:
    """
    Loads the given preset
    :param presets_name: The name of the generator. (lowercase snake_case)
    :return: Dictionary, mapping of constant-name -> constant-value
    """

    path = Path('configs/constants_presets/' + presets_name+'.yaml')
    yaml = YAML(typ='safe')
    return yaml.load(path)
