# %%
from pathlib import Path

from ocp_vscode import show

from parameterizable_universal_dispenser.configuration import load_config
from parameterizable_universal_dispenser.generator import universal_item_dispenser

# %%

conf = load_config(path=Path("../configs/default.conf.yaml"))
show(universal_item_dispenser(conf))

# %%
