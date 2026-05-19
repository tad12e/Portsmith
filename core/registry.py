
"""Service registry for Portsmith.

This module loads service definitions from YAML, validates the config,
and keeps the parsed services available for the rest of the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("configs") / "services.yaml"


@dataclass(frozen=True, slots=True)
class ServiceDefinition:
	"""A single service entry loaded from the registry config."""

	command: str
	port: int
	domain: str


class ServiceRegistry:
	"""Load and validate service definitions from a YAML config file."""

	def __init__(self, services: dict[str, ServiceDefinition], source_path: Path | None = None) -> None:
		self._services = services
		self.source_path = source_path

	def __repr__(self) -> str:
		return f"ServiceRegistry(services={list(self._services.keys())}, source={self.source_path})"

	@classmethod
	def load(cls, path: str | Path = DEFAULT_CONFIG_PATH) -> "ServiceRegistry":
		"""Load service definitions from a YAML file."""

		config_path = Path(path)
		with config_path.open("r", encoding="utf-8") as handle:
			raw_config = yaml.safe_load(handle) or {}

		services = cls._parse_services(raw_config)
		return cls(services=services, source_path=config_path)

	@staticmethod
	def _parse_services(raw_config: Any) -> dict[str, ServiceDefinition]:
		if not isinstance(raw_config, dict):
			raise ValueError("Services config must be a mapping at the top level.")

		raw_services = raw_config.get("services")
		if not isinstance(raw_services, dict) or not raw_services:
			raise ValueError("Services config must contain a non-empty 'services' mapping.")

		services: dict[str, ServiceDefinition] = {}
		for name, service_config in raw_services.items():
			if not isinstance(name, str) or not name.strip():
				raise ValueError("Service names must be non-empty strings.")
			if not isinstance(service_config, dict):
				raise ValueError(f"Service '{name}' must be defined as a mapping.")

			command = service_config.get("command")
			domain = service_config.get("domain")
			port = service_config.get("port")

			if not isinstance(command, str) or not command.strip():
				raise ValueError(f"Service '{name}' must define a non-empty command.")
			if not isinstance(domain, str) or not domain.strip():
				raise ValueError(f"Service '{name}' must define a non-empty domain.")

			parsed_port = ServiceRegistry._coerce_port(port, name)
			services[name] = ServiceDefinition(command=command.strip(), port=parsed_port, domain=domain.strip())

		return services

	@staticmethod
	def _coerce_port(value: Any, service_name: str) -> int:
		if isinstance(value, bool) or value is None:
			raise ValueError(f"Service '{service_name}' must define a valid port.")

		if isinstance(value, int):
			port = value
		elif isinstance(value, str) and value.strip().isdigit():
			port = int(value.strip())
		else:
			raise ValueError(f"Service '{service_name}' must define a valid port.")

		if not 1 <= port <= 65535:
			raise ValueError(f"Service '{service_name}' port must be between 1 and 65535.")

		return port

	def get(self, name: str) -> ServiceDefinition:
		"""Return a single service definition by name."""

		return self._services[name]

	def __getitem__(self, name: str) -> ServiceDefinition:
		"""Allow dictionary-style access: registry['auth']."""
		return self.get(name)

	def __contains__(self, name: object) -> bool:
		"""Allow existence checks: 'auth' in registry."""
		return name in self._services

	def names(self) -> list[str]:
		"""Return the configured service names in insertion order."""

		return list(self._services)

	def as_dict(self) -> dict[str, dict[str, Any]]:
		"""Return the public service registry shape used by the rest of the app."""

		return {
			name: {"port": service.port, "domain": service.domain}
			for name, service in self._services.items()
		}

	def raw_services(self) -> dict[str, ServiceDefinition]:
		"""Expose the parsed service definitions for internal use."""

		return dict(self._services)
