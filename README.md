> **Warning**  
> This repo is work in progress.

# Parameterizable Universal Dispenser

This project is inspired by [this model](https://makerworld.com/pl/models/2613993-sanitary-pad-dispenser), 
found by my wife at printerest. I developed the  model to be easy to modify and accomodate with different items.
The default configuration I happily use as a dispenser for glass cleaning sheets.

# Models

For the default configs models are available packed in .zip file as a release. There are a few options to generate models
for modified config.

## Online

### (Recommended) Streamlit webpage

The easiest and recommended way to prepare your own version of the model. Visit the [webpage](https://parameterizable-universal-dispenser.streamlit.app/), insert the desired values in GUI configurator,
and click **download** and you ready to go!

### Github actions

This repo already accomodate the github action to generate and release files, based on the default config.
Step by step:
- Clone the repo
- Modify the default config file
- commit and add tag starting with `v` letter
  - Github Actions should run automatically
- Download release file

## Locally

### Docker

You can generate models using `Dockerfile.generate`. Modify the default config and run the commands:
```bash
docker build -f Dockerfile.generate -t generate:latest .
docker run --rm -v "$(pwd)/build":"/app/build" generate:latest
```

You will find all the STL files at `build/` directory.

### Python

System requirements: install `uv` python library.

UV [installation guide](https://docs.astral.sh/uv/getting-started/installation/).


Next clone the repo and move to the directory:
```bash
git clone https://github.com/AIn0n/2Mkb && cd 2Mkb
```


Create UV virtual environment:
```bash
uv venv
```


Activate the environment:
```bash
source .venv/bin/activate
```


Install project requirements:
```bash
uv sync
```


Run the script:
```bash
uv run generate
```

All STLs can be found at `build/` directory.


# LICENSE

License found at [this repo](https://github.com/non-ai-licenses/non-ai-licenses/blob/main/NON-AI-APACHE2).
It's just a Apache 2.0 license, with small disclaimer to not use it as a training data in any form of AI
models.