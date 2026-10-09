import streamlit as st

from parameterizable_universal_dispenser.generator import universal_item_dispenser
from parameterizable_universal_dispenser.configuration import load_config
from build123d import Mesher
from streamlit_extras.three_viewer import three_viewer
import io
from pathlib import Path


st.header("Hello world! hehe")

conf = load_config(path=Path("src/configs/default.conf.yaml"))

part = universal_item_dispenser(conf)

# 1. Generate the STL bytes entirely in memory
mesher = Mesher()
mesher.add_shape(part, linear_deflection=0.001, angular_deflection=0.1)

stl_stream = io.BytesIO()
mesher.write_stream(stl_stream, "stl")
stl_bytes = stl_stream.getvalue()

# 2. Display the bytes directly
three_viewer(
    stl_bytes,
    file_format=".stl",   # <-- Required for bytes
    height=600,
    key="my_model_viewer"
)
