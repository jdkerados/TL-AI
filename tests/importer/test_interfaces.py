"""Architecture tests: every stage is an abstract interface with no implementation."""

import inspect
from abc import ABC
from typing import Any

import pytest

from tl_importer.importers import EntityImporter
from tl_importer.mapping import EntityMapper
from tl_importer.normalizers import Normalizer
from tl_importer.parsers import Parser
from tl_importer.providers import (
    ManualProvider,
    MaxrollProvider,
    Provider,
    QuestlogProvider,
    WikiProvider,
    YoutubeProvider,
)
from tl_importer.validators import ImportValidator

ALL_INTERFACES: tuple[type, ...] = (
    Provider,
    WikiProvider,
    QuestlogProvider,
    MaxrollProvider,
    YoutubeProvider,
    ManualProvider,
    Parser,
    Normalizer,
    ImportValidator,
    EntityMapper,
    EntityImporter,
)


@pytest.mark.parametrize("interface", ALL_INTERFACES, ids=lambda cls: cls.__name__)
def test_interface_is_abstract(interface: type) -> None:
    assert issubclass(interface, ABC)
    assert inspect.isabstract(interface)


@pytest.mark.parametrize("interface", ALL_INTERFACES, ids=lambda cls: cls.__name__)
def test_interface_cannot_be_instantiated(interface: Any) -> None:
    with pytest.raises(TypeError):
        interface()


@pytest.mark.parametrize(
    "provider_interface",
    [WikiProvider, QuestlogProvider, MaxrollProvider, YoutubeProvider, ManualProvider],
    ids=lambda cls: cls.__name__,
)
def test_named_providers_extend_provider(provider_interface: type) -> None:
    assert issubclass(provider_interface, Provider)


def test_interfaces_declare_required_methods() -> None:
    assert set(Provider.__abstractmethods__) == {"name", "supports", "fetch"}
    assert set(Parser.__abstractmethods__) == {"can_parse", "parse"}
    assert set(Normalizer.__abstractmethods__) == {"entity_type", "normalize"}
    assert set(ImportValidator.__abstractmethods__) == {"validate"}
    assert set(EntityMapper.__abstractmethods__) == {"entity_type", "rules", "apply"}
    assert set(EntityImporter.__abstractmethods__) == {"persist"}
