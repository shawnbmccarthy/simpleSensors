"""
debug_params.py

"""
from logging import Logger
from typing import Dict
from viam.logging import getLogger

from emulators.utilities import generate_random


class DebugParams(object):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    def get_debug_data(self) -> Dict[str, float]:
        self.logger.debug('returning debug data')
        ret_dict = {}
        for i in range(1, 16):
            ret_dict[f'DEBUG_{i}'] = generate_random(0, 20, 4)
        return ret_dict
