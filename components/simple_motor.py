from threading import Lock
from typing import ClassVar, Dict, Mapping, Sequence, Optional, Any, Tuple
from typing_extensions import Self
from viam.components.component_base import ValueTypes
from viam.components.motor import Motor
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily


class SimpleMotor(Motor, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily('acme', 'robodeck'), 'motor')

    mapped_name: str
    board: str
    is_moving: bool
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
        self.is_moving = False
        self.lock = Lock()

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> None:
        self.mapped_name = config.attributes.fields['mapped_name'].string_value
        self.board = config.attributes.fields['board'].string_value

    async def set_power(
        self,
        power: float,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        with self.lock.acquire():
            if power == 0.0:
                self.is_moving = False
            else:
                self.is_moving = True

    async def go_for(
        self,
        rpm: float,
        revolutions: float,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        with self.lock.acquire():
            self.is_moving = True
            for _ in range(int(revolutions)):
                pass
            self.is_moving = False

    async def go_to(
        self,
        rpm: float,
        position_revolutions: float,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        with self.lock.acquire():
            self.is_moving = True
            for _ in range(int(position_revolutions)):
                pass
            self.is_moving = False

    async def reset_zero_position(
        self,
        offset: float,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ):
        pass

    async def get_position(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> float:
        return 0.0

    async def get_properties(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Motor.Properties:
        raise NotImplementedError()

    async def stop(self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs):
        with self.lock.acquire():
            self.is_moving = False

    async def is_powered(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
    ) -> Tuple[bool, float]:
        return self.is_moving, 0

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        pass


Registry.register_resource_creator(
    Motor.SUBTYPE,
    SimpleMotor.MODEL,
    ResourceCreatorRegistration(SimpleMotor.new, SimpleMotor.validate_config)
)