from pathlib import Path

from build123d.exporters3d import export_step, export_stl

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import universal_item_dispenser


def main():
    conf = load_config(path=Path("src/configs/default.conf.yaml"))
    part = universal_item_dispenser(conf)

    conf.output_dir.mkdir(exist_ok=True, parents=True)
    export_stl(part, conf.output_dir / "dispenser.stl")
    export_step(part, conf.output_dir / "dispenser.step")


if __name__ == "__main__":
    main()
