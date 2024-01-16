"""
main entry point
"""
import asyncio
import sys

from viam.components.base import Base
from viam.components.motor import Motor
from viam.components.power_sensor import PowerSensor
from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.module.module import Module

from components import SimpleSensor, SimplePowerSensor, SimpleBase, SimpleMotor

logger = getLogger(__name__)

OK = 0
SOCKET_NEEDED_ERR = 1
MODULE_START_ERR = 2


async def main(addr: str) -> None:
    failed = OK
    logger.info('starting module')

    try:
        m = Module(addr)
        # technically not needed but here for completeness
        m.add_model_from_registry(Sensor.SUBTYPE, SimpleSensor.MODEL)
        m.add_model_from_registry(PowerSensor.SUBTYPE, SimplePowerSensor.MODEL)
        m.add_model_from_registry(Motor.SUBTYPE, SimpleMotor.MODEL)
        m.add_model_from_registry(Base.SUBTYPE, SimpleBase.MODEL)
        await m.start()
    except Exception as e:
        logger.fatal(f'error occurred starting module: {e}, exiting ({MODULE_START_ERR})')
        failed = MODULE_START_ERR
    finally:
        sys.exit(failed)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.fatal(f'need socket path as cmd line arg, exiting ({SOCKET_NEEDED_ERR})')
        sys.exit(SOCKET_NEEDED_ERR)
    asyncio.run(main(sys.argv[1]))
    sys.exit(OK)
