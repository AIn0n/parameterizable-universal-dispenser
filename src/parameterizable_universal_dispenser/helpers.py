import io
import shutil
import tempfile
from dataclasses import asdict
from enum import Enum, auto

import build123d as bt
import yaml

from parameterizable_universal_dispenser.configuration import ConfigSchema


def prepare_zip_files(dispenser: bt.Part, lid: bt.Part, conf: ConfigSchema) -> bytes:
    val = None
    with (
        tempfile.TemporaryDirectory() as tmp_models_dir,
        tempfile.TemporaryDirectory() as tmp_zip_dir,
    ):
        bt.export_step(dispenser, f"{tmp_models_dir}/dispenser.step")
        bt.export_step(lid, f"{tmp_models_dir}/lid.step")

        bt.export_stl(dispenser, f"{tmp_models_dir}/dispenser.stl")
        bt.export_stl(lid, f"{tmp_models_dir}/lid.stl")

        with open(f"{tmp_models_dir}/config.yaml", "w") as config_file:
            yaml.dump(asdict(conf), config_file, default_flow_style=False)

        filename = "dispenser"
        archive_fn = shutil.make_archive(
            f"{tmp_zip_dir}/{filename}", "zip", tmp_models_dir
        )
        with open(archive_fn, "rb") as f:
            val = f.read()

    assert val is not None
    return val


class PreviewOptions(Enum):
    BOTH = auto()
    DISPENSER = auto()
    LID = auto()


def preview(
    conf: ConfigSchema,
    dispenser: bt.Part,
    lid: bt.Part,
    previewOptions: PreviewOptions | None = None,
) -> bt.Part:
    if previewOptions is None:
        previewOptions = PreviewOptions.BOTH
    match previewOptions:
        case PreviewOptions.BOTH:
            distance = (
                conf.dispenser_dims.z_mm
                + conf.lid_dims.z_mm
                + conf.lid_dims.internal_z_mm
                + 10
            )
            part = dispenser + (bt.Pos(0, 0, distance) * bt.Rot(180, 0, 0) * lid)
        case PreviewOptions.DISPENSER:
            part = dispenser
        case PreviewOptions.LID:
            part = bt.Rot(180, 0, 0) * lid

    bb = part.bounding_box()
    center = bb.center()
    return part.moved(bt.Location((-center.X, -center.Y, -center.Z)))


def get_stl_bytes(part: bt.Part) -> bytes:
    mesher = bt.Mesher()
    mesher.add_shape(part, linear_deflection=0.001, angular_deflection=0.1)

    stl_stream = io.BytesIO()
    mesher.write_stream(stl_stream, "stl")
    return stl_stream.getvalue()
