from pathlib import Path

import streamlit as st
from streamlit_extras.three_viewer import three_viewer

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import (
    center_for_preview,
    get_stl_bytes,
    universal_item_dispenser,
)

st.header("Hello world! hehe")

conf = load_config(path=Path("src/configs/default.conf.yaml"))

config_col, preview_col = st.columns(2)
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
            conf.dispenser_dims.corner_rounding_radius_mm = st.number_input(
                "Rounding Radius",
                value=conf.dispenser_dims.corner_rounding_radius_mm,
                max_value=min(conf.dispenser_dims.y_mm, conf.dispenser_dims.x_mm) / 2,
            )
            conf.dispenser_dims.base_z_mm = st.number_input(
                "Base height",
                value=conf.dispenser_dims.base_z_mm,
                help="Base is the distance between ground and the first item in dispenser",
            )


with preview_col:
    part = center_for_preview(universal_item_dispenser(conf))

    three_viewer(
        get_stl_bytes(part), file_format=".stl", height=600, key="my_model_viewer"
    )
