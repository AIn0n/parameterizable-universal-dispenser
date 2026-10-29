from argparse import ArgumentParser
from pathlib import Path

from build123d.exporters3d import export_step, export_stl

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import generate_dispenser
from parameterizable_universal_dispenser.helpers import models_to_zip


def arguments_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="Parametizable universal dispenser generator")
    parser.add_argument(
        "--zip-path",
        "-z",
        type=str,
        required=False,
        default=None,
        help="Path to zipped file. If given, the files will be saved into the zip, in given directory.",
    )
    parser.add_argument(
        "--config-path",
        "-c",
        type=str,
        required=False,
        default="src/configs/default.conf.yaml",
    )
    return parser


def main() -> None:
    args = arguments_parser().parse_args()
    zip_path = args.zip_path
    conf = load_config(path=Path(args.config_path))
    dispenser, lid = generate_dispenser(conf)

    if zip_path is None:
        conf.output_dir.mkdir(exist_ok=True, parents=True)
        export_stl(dispenser, conf.output_dir / "dispenser.stl")
        export_step(dispenser, conf.output_dir / "dispenser.step")
        export_stl(lid, conf.output_dir / "lid.stl")
        export_step(lid, conf.output_dir / "lid.step")
        return None

    Path(zip_path).parent.mkdir(exist_ok=True, parents=True)
    models_to_zip(dispenser, lid, zip_path)


if __name__ == "__main__":
    main()
