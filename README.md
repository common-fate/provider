# commonfate-provider-core

Commonfate Provider Core Python Package

## Getting started

```
poetry install
```

Open a virtual environment:

```
poetry shell
```

## Testing

Run tests:

```
pytest
```

This repo uses snapshot testing to verify that the output schema is as expected.

You can update these snapshot tests by running:

```
pytest --snapshot-update
```

## Building a development version

When working on the Common Fate Provider framework it can be useful to use a development build of this package in an Access Provider. To do so run:

```
poetry build
```

which will create a `dist` folder containing the package:

```
dist
├── commonfate_provider-0.1.5-py3-none-any.whl
└── commonfate_provider-0.1.5.tar.gz
```

You can then install this package locally via `pip` in the Access Provider you'd like to use it with:

```bash
# from the Access Provider repository
source .venv/bin/activate
pip install ../commonfate-provider-core/dist/commonfate_provider-0.1.5.tar.gz
```
