import json
import logging
import yaml
from types import MappingProxyType
from typing import Any, Dict, Tuple

from .. interfaces import IConfig
from .. patterns import Singleton
from .. config.exceptions import (
    MarshallJSONError,
    MarshallYAMLError,
)


Address = Tuple[str, int]


logger = logging.getLogger(__file__)


def _marshall_yaml(data: Dict) -> Dict:
    marshalled_data = data
    marshalled_servers: Dict[int, Address] = {}

    for key, address in data['servers'].items():
        try:
            host, port = address.split(':')
        except ValueError:
            logger.error('could not parse address %s ', address)
            raise MarshallYAMLError

        marshalled_servers.update(
            {key: (host, int(port))}
        )

    marshalled_data.update({'servers': marshalled_servers})
    return marshalled_data


def _marshall_json(data: Dict) -> Dict:
    marshalled_data = data
    marshalled_servers: Dict[int, Address] = {}

    for key, address in data['servers'].items():
        marshalled_servers.update(
            {key: (address['host'], int(address['port']))}
        )

    marshalled_data.update({'servers': marshalled_servers})
    return marshalled_data


def build_config_from_yaml(filepath: str) -> "RaftConfig":
    with open(filepath, 'r') as s:
        try:
            marshalled_data = _marshall_yaml(**yaml.safe_load(s))
            cfg = RaftConfig(**marshalled_data)

        except TypeError:
            logger.error('failed to marshall yaml', exc_info=True)

        except yaml.YAMLError:
            logger.error(
                'failed to load %s as a JSON file', filepath, exc_info=True
            )

        return cfg


def build_config_from_json(filepath: str) -> "RaftConfig":
    with open(filepath, 'r') as f:
        try:
            cfg = RaftConfig(**json.load(f))

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
