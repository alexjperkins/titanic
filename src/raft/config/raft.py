import json
import logging
import yaml
from types import MappingProxyType
from typing import Any, Dict, Tuple

from .. interfaces import IConfig
from .. messaging.network import Address
from .. patterns import Singleton
from .. config.exceptions import (
    MarshallJSONError,
    MarshallYAMLError,
)


logger = logging.getLogger(__file__)


def _marshall_yaml(data: Dict) -> Dict:
    marshalled_data = data
    marshalled_servers: Dict[int, Address] = {}

    for identification, address in data['servers'].items():
        try:
            host, port = address.split(':')
        except ValueError:
            logger.error('could not parse address %s ', address)
            raise MarshallYAMLError

        marshalled_servers.update(
            {
                identification: Address(
                    host=host, port=int(port), identification=identification
                )
            }
        )

    marshalled_data.update({'servers': marshalled_servers})
    return marshalled_data


def _marshall_json(data: Dict) -> Dict:
    marshalled_data = data
    marshalled_servers: Dict[int, Address] = {}

    for identification, address in data['servers'].items():
        marshalled_servers.update(
            {
                identification: Address(
                    host=address['host'], port=int(address['port']),
                    identification=identification
                )
            }
        )

    marshalled_data.update({'servers': marshalled_servers})
    return marshalled_data


def build_config_from_yaml(filepath: str) -> "RaftConfig":
    with open(filepath, 'r') as s:
        try:
            marshalled_data = _marshall_yaml(data=yaml.safe_load(s))
            cfg = RaftConfig(**marshalled_data)

        except TypeError:
            logger.error('failed to marshall yaml', exc_info=True)
            raise

        except yaml.YAMLError:
            logger.error(
                'failed to load %s as a JSON file', filepath, exc_info=True
            )
            raise

        return cfg


def build_config_from_json(filepath: str) -> "RaftConfig":
    with open(filepath, 'r') as f:
        try:
            marshalled_data = _marshall_json(data=json.load(f))
            cfg = RaftConfig(**marshalled_data)

        except TypeError:
            logger.error('failed to marshall json', exc_info=True)

        except json.JSONDecodeError:
            logger.error(
                'failed to load %s as a JSON file', filepath, exc_info=True
            )

        return cfg


class MetaRaftConfig(IConfig, Singleton):
    pass


class RaftConfig(metaclass=MetaRaftConfig):

    def __init__(self, servers: Dict[int, Address]):
        self._servers = servers  # pass from yaml instead

    def __iter__(self):
        yield from self.__dict__.items()

    def to_dict(self) -> Dict[Any, Any]:
        return {k: v for k, v in self}

    @property
    def servers(self):
        return MappingProxyType(self._servers)
