from threading import Lock
from typing import ClassVar, Dict, Mapping, Sequence, Tuple, Optional, Any
from typing_extensions import Self
from viam.components.component_base import ValueTypes
from viam.components.power_sensor import PowerSensor
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, Vector3


class SimplePowerSensor(PowerSensor, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily('acme', 'robodeck'), 'powersensor')

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
        return {
            'a': {'amps': 0, 'ampsIsAc': False},
            'v': {'volts': 0, 'voltsIsAc': False},
            'watts': 0
        }

    async def get_voltage(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[float, bool]:
        return 0, False

    async def get_current(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[float, bool]:
        return 0, False

    async def get_power(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> float:
        return 0

    async def set_power(
        self,
        linear: Vector3,
        angular: Vector3,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        pass

    async def set_velocity(
        self,
        linear: Vector3,
        angular: Vector3,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
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
    PowerSensor.SUBTYPE,
    SimplePowerSensor.MODEL,
    ResourceCreatorRegistration(SimplePowerSensor.new, SimplePowerSensor.validate_config)
)