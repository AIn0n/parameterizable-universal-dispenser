# %%
from pathlib import Path

import build123d as bt
from ocp_vscode import show

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import generate_dispenser, preview

# %%

conf = load_config(path=Path("../configs/default.conf.yaml"))
dispenser, lid = generate_dispenser(conf)
show(preview(conf, dispenser, lid))

# %%
