# Recipe Normalizer

A command-line application that normalizes cooking recipes from various input formats (XML, YAML) to a consistent JSON file format.

## Features

- Reads recipes from multiple formats (XML, YAML)
- Converts imperial units to metric units (pound → grams, fl. oz. → ml, etc.)
- Outputs a single normalized JSON file
- Extensible parser architecture

## Installation

```bash
uv sync
```

## Usage

```bash
uv run recipe-normalizer <input_directory> <output_file.json>
```

### Example

```bash
uv run recipe-normalizer ./recipes ./output.json
```

### Options

- `-v, --verbose`: Enable verbose output

## Testing the Examples

The `examples/` directory contains sample input files and expected output for verification.

Run the normalizer on the examples:

```bash
uv run recipe-normalizer ./examples ./output.json
```

Compare with expected output:

```bash
diff examples/expected_output.json output.json
```

Or verify programmatically:

```bash
uv run python -c "import json; e=json.load(open('examples/expected_output.json')); a=json.load(open('output.json')); print('OK' if e==a else 'MISMATCH')"
```

## Running Tests

```bash
uv run pytest
```

## Docker

Build the image:

```bash
docker build -t recipe-normalizer .
```

Run with mounted volumes:

```bash
docker run -v $(pwd)/examples:/data/input -v $(pwd):/data/output \
    recipe-normalizer /data/input /data/output/output.json
```

Compare with expected output:

```bash
diff examples/expected_output.json output.json
```

## Architecture

```
src/recipe_normalizer/
├── cli.py              # Entry point
├── models.py           # Pydantic models (Recipe, Ingredient)
├── exceptions.py       # Custom exceptions
├── converters/
│   └── units.py        # Unit conversion (pint)
├── parsers/
│   ├── base.py         # Abstract parser interface
│   ├── registry.py     # Parser registry
│   ├── xml_parser.py
│   └── yaml_parser.py
└── services/
    └── normalizer.py   # Main orchestration
```

### Design Principles

- **Registry Pattern**: `ParserRegistry` routes files to parsers by extension
- **Dependency Injection**: Services receive dependencies via constructor
- **Single Responsibility**: Each module has one clear purpose
- **Extensibility**: Add new formats by implementing `RecipeParser` interface

### Data Flow

```
Input Files → ParserRegistry → Recipe Models → UnitConverter → JSON Output
```

## Assumptions

- Cups are converted to ml using metric cup (240ml)
- Weight units (pound, oz) convert to grams
- Volume units (gallon, fl oz, cup) convert to ml or liter
- Uses US customary units with cooking-friendly definitions
- Recipes are sorted reverse alphabetically by name in the output