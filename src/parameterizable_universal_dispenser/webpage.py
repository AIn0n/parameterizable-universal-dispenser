from pathlib import Path

import streamlit as st
from streamlit_extras.three_viewer import three_viewer

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import (
    generate_dispenser,
    get_min_circles_num,
)
from parameterizable_universal_dispenser.helpers import *

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
                min_value=get_min_circles_num(conf),
                max_value=175,
            )

        with st.expander("finger hole opening dimensions"):
            conf.fingerhole_dims.fingerhole_x = st.number_input(
                "Width", value=conf.fingerhole_dims.fingerhole_x, min_value=0.1
            )
            conf.fingerhole_dims.fingerhole_z = st.number_input(
                "Height", value=conf.fingerhole_dims.fingerhole_z, min_value=0.1
            )


with preview_col:
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
        width="stretch",
    )
    dispenser, lid = generate_dispenser(conf)
    download_col.download_button(
        "Download STL + STEP + .yaml confg",
        data=lambda: models_to_zipped_bytes(dispenser, lid, conf),
        file_name="dispenser.zip",
        mime="application/zip",
        width="stretch",
        type="primary",
        icon=":material/download:",
    )

    part = preview(conf, dispenser, lid, preview_option)
    stl_bytes = get_stl_bytes(part)
    three_viewer(stl_bytes, file_format=".stl", height=600, key="my_model_viewer")
