from pathlib import Path

from build123d.exporters3d import export_step, export_stl

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import generate_dispenser


def main():
    conf = load_config(path=Path("src/configs/default.conf.yaml"))
    dispenser, lid = generate_dispenser(conf)

    conf.output_dir.mkdir(exist_ok=True, parents=True)
    export_stl(dispenser, conf.output_dir / "dispenser.stl")
    export_step(dispenser, conf.output_dir / "dispenser.step")
    export_stl(lid, conf.output_dir / "lid.stl")
    export_step(lid, conf.output_dir / "lid.step")


if __name__ == "__main__":
    main()
