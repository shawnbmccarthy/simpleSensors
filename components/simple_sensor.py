from threading import Lock
from typing import ClassVar, Mapping, Sequence, Optional, Any
from typing_extensions import Self
from viam.components.component_base import ValueTypes
from viam.components.sensor import Sensor
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading
from .sensor_constants import MAPPING_STATUS, MAPPING_NAVIGATION, MAPPING_DEBUG

class SimpleSensor(Sensor, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily('acme', 'robodeck'), 'sensor')

    mapped_name: str
    board: str
    lock: Lock

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        mapped_name = config.attributes.fields['mapped_name'].string_value
        board = config.attributes.fields['board'].string_value

        if mapped_name is None or mapped_name == '':
            raise Exception('mapped_name is a required attribute')

        if board is None or board == '':
            raise Exception('board is a required attribute')

        return []

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.mapped_name = ''
        self.board = ''
        self.lock = Lock()

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> None:
        self.mapped_name = config.attributes.fields['mapped_name'].string_value
        self.board = config.attributes.fields['board'].string_value

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        if self.mapped_name == MAPPING_DEBUG:
            return {
                'BUMPER': 0,
                'GAP1': 0,
                'GAP2': 0,
                'GAP3': 0,
                'MISSED_SLOW_CYCLES': 0,
                'US_LEFT': 0,
                'US_RIGHT': 0
            }
        elif self.mapped_name == MAPPING_STATUS:
            return {
                'CONSUMED_CAP': 0,
                'CONSUMED_STAIN': 0,
                'FWD_STOP_REASON': 0,
                'ROBOT_HEALTH': 0,
                'ROBOT_MODE': 0,
                'SEARCH_STOP_ANGLE': 0,
                'SEARCH_STOP_REASON': 0,
                'STAINED_AREA': 0,
                'ST_TEMP': 0,
                'SUCC_SEARCH_RATIO': 0
            }
        elif self.mapped_name == MAPPING_NAVIGATION:
            return {
                'DEBUG_DATA_1': 0,
                'DEBUG_DATA_2': 0,
                'DEBUG_DATA_3': 0,
                'DEBUG_DATA_4': 0,
                'DEBUG_DATA_5': 0,
                'DEBUG_DATA_6': 0,
                'DEBUG_DATA_7': 0,
                'DEBUG_DATA_8': 0,
                'DEBUG_DATA_9': 0,
                'DEBUG_DATA_10': 0,
                'DEBUG_DATA_11': 0,
                'DEBUG_DATA_12': 0,
                'DEBUG_DATA_13': 0,
                'DEBUG_DATA_14': 0,
                'DEBUG_DATA_15': 0
            }
        pass

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        pass


Registry.register_resource_creator(
    Sensor.SUBTYPE,
    SimpleSensor.MODEL,
    ResourceCreatorRegistration(SimpleSensor.new, SimpleSensor.validate_config)
)