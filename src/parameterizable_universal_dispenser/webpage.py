import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path

import build123d as bt
import streamlit as st
import yaml
from streamlit_extras.three_viewer import three_viewer

from parameterizable_universal_dispenser.configuration import ConfigSchema, load_config
from parameterizable_universal_dispenser.generator import (
    PreviewOptions,
    generate_dispenser,
    get_stl_bytes,
    preview,
)

st.header("Parameterizable universal dispenser configurator")

conf = load_config(path=Path("src/configs/default.conf.yaml"))

config_col, preview_col = st.columns([0.3, 0.7])
st.set_page_config(layout="wide")

with config_col:
    with st.container(border=True):
        with st.expander("Base Dimensions"):
            conf.dispenser_dims.z_mm = st.number_input(
                "Total height", value=conf.dispenser_dims.z_mm
            )
            conf.dispenser_dims.x_mm = st.number_input(
                "Total width",
                value=conf.dispenser_dims.x_mm,
                help="Total Width of the whole object. It can be different than width of the object to put inside",
                min_value=conf.item_dims.x_mm,
            )
            conf.dispenser_dims.y_mm = st.number_input(
                "Total length",
                value=conf.dispenser_dims.y_mm,
                min_value=conf.item_dims.y_mm,
            )
            conf.dispenser_dims.corner_rounding_radius_mm = st.slider(
                "Rounding Radius",
                value=conf.dispenser_dims.corner_rounding_radius_mm,
                min_value=0.0,
                max_value=min(conf.dispenser_dims.y_mm, conf.dispenser_dims.x_mm) / 2,
            )
            conf.dispenser_dims.base_z_mm = st.number_input(
                "Base height",
                value=conf.dispenser_dims.base_z_mm,
                help="Base is the distance between ground and the first item in dispenser",
            )
        with st.expander("Item Dimensions"):
            # TODO: X and Y of item are wrong, fix it
            conf.item_dims.x_mm = st.number_input(
                "Width", value=conf.item_dims.x_mm, max_value=conf.dispenser_dims.x_mm
            )
            conf.item_dims.y_mm = st.number_input(
                "Length", value=conf.item_dims.y_mm, max_value=conf.dispenser_dims.y_mm
            )
            conf.item_dims.z_mm = st.number_input(
                "Height",
                value=conf.item_dims.z_mm,
                max_value=conf.dispenser_dims.z_mm,
                help="This value defines how large opening for item will be",
            )

        with st.expander("Lid Dimensions"):
            conf.lid_dims.z_mm = st.number_input(
                "Height", value=conf.lid_dims.z_mm, min_value=0.1
            )
            conf.lid_dims.margin_mm = st.slider(
                "Margin",
                value=conf.lid_dims.margin_mm,
                help="margin between lid and dispenser",
                min_value=0.0,
                max_value=1.0,
            )

        with st.expander("Exterior circles dimensions"):
            conf.circles_dims.r_mm = st.number_input(
                "Circles radius", value=conf.circles_dims.r_mm, min_value=0.1
            )
            conf.circles_dims.n = st.slider(
                "Number of circles around dispenser",
                value=conf.circles_dims.n,
                min_value=30,
                max_value=175,
            )

        with st.expander("finger hole opening dimensions"):
            conf.fingerhole_dims.fingerhole_x = st.number_input(
                "Width", value=conf.fingerhole_dims.fingerhole_x, min_value=0.1
            )
            conf.fingerhole_dims.fingerhole_z = st.number_input(
                "Height", value=conf.fingerhole_dims.fingerhole_z, min_value=0.1
            )


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


with preview_col:
    dispenser, lid = generate_dispenser(conf)
    download_bytes = prepare_zip_files(dispenser, lid, conf)

    option_col, download_col = st.columns(2)
    option_map = {
        PreviewOptions.BOTH: "Both",
        PreviewOptions.DISPENSER: "Dispenser only",
        PreviewOptions.LID: "Lid only",
    }

    preview_option = option_col.segmented_control(
        "View",
        options=option_map.keys(),
        format_func=lambda opt: option_map[opt],
        default=PreviewOptions.BOTH,
        label_visibility="collapsed",
    )
    download_col.download_button(
        "Download STL + STEP + .yaml confg",
        data=download_bytes,
        file_name="dispenser.zip",
        mime="model/stl",
        width="stretch",
        type="primary",
        icon=":material/download:",
    )

    part = preview(conf, dispenser, lid, preview_option)
    stl_bytes = get_stl_bytes(part)
    three_viewer(stl_bytes, file_format=".stl", height=600, key="my_model_viewer")
