from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from omegaconf import OmegaConf


@dataclass
class ItemDimensions:
    x_mm: float = 6
    y_mm: float = 8
    z_mm: float = 2
    count: int = 10


@dataclass
class CirclesDimensions:
    r_mm: float = 0.25
    n: int = 100


@dataclass
class DispenserDimensions:
    corner_rounding_radius_mm: float = 1.0
    x_mm: float = 10
    y_mm: float = 10
    base_z_mm: float = 1


@dataclass
class LidDimensions:
    z_mm: float = 2
    margin_mm: float = 0.2
    internal_z_mm: float = 0.5


@dataclass
class FingerHoleDimensions:
    fingerhole_z: float = 2.0
    fingerhole_x: float = 3.0


@dataclass
class ConfigSchema:
    item_dims: ItemDimensions = field(default_factory=ItemDimensions)
    circles_dims: CirclesDimensions = field(default_factory=CirclesDimensions)
    lid_dims: LidDimensions = field(default_factory=LidDimensions)
    fingerhole_dims: FingerHoleDimensions = field(default_factory=FingerHoleDimensions)
    dispenser_dims: DispenserDimensions = field(default_factory=DispenserDimensions)
    output_dir: Path = Path("./build/")


def load_config(path: Path) -> ConfigSchema:
    yaml_config = OmegaConf.load(path)

    schema = OmegaConf.structured(ConfigSchema)
    merged = OmegaConf.merge(schema, yaml_config)
    return cast(ConfigSchema, OmegaConf.to_object(merged))
