"""Command-line interface for the recipe normalizer."""

import logging
import sys
from pathlib import Path

import click

from recipe_normalizer.converters.units import UnitConverter
from recipe_normalizer.exceptions import RecipeNormalizerError
from recipe_normalizer.parsers.registry import ParserRegistry
from recipe_normalizer.parsers.xml_parser import XmlRecipeParser
from recipe_normalizer.parsers.yaml_parser import YamlRecipeParser
from recipe_normalizer.services.normalizer import RecipeNormalizer


def setup_logging(verbose: bool, debug: bool) -> None:
    """Configure logging based on verbosity level."""
    if debug:
        level = logging.DEBUG
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif verbose:
        level = logging.INFO
        fmt = "%(levelname)s: %(message)s"
    else:
        level = logging.WARNING
        fmt = "%(levelname)s: %(message)s"

    logging.basicConfig(level=level, format=fmt, stream=sys.stderr)


def create_parser_registry() -> ParserRegistry:
    """Create and configure the parser registry with all available parsers."""
    registry = ParserRegistry()
    registry.register(XmlRecipeParser())
    registry.register(YamlRecipeParser())
    return registry


def create_normalizer() -> RecipeNormalizer:
    """Create a fully configured RecipeNormalizer instance."""
    registry = create_parser_registry()
    converter = UnitConverter()
    return RecipeNormalizer(registry, converter)


@click.command()
@click.argument(
    "input_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "output_file",
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", "-d", is_flag=True, help="Enable debug output")
@click.option(
    "--skip-errors",
    "-s",
    is_flag=True,
    help="Skip files that fail to parse instead of stopping",
)
def main(
    input_dir: Path,
    output_file: Path,
    verbose: bool,
    debug: bool,
    skip_errors: bool,
) -> None:
    """Normalize cooking recipes from various formats to JSON.

    INPUT_DIR: Directory containing recipe files (XML, YAML, etc.)

    OUTPUT_FILE: Path for the output JSON file
    """
    setup_logging(verbose, debug)
    logger = logging.getLogger(__name__)

    normalizer = create_normalizer()

    try:
        recipes = normalizer.normalize_directory(input_dir, skip_errors=skip_errors)
        normalizer.export_to_json(recipes, output_file)
        click.echo(f"Normalized {len(recipes)} recipes to {output_file}")

    except RecipeNormalizerError as e:
        logger.error(str(e))
        raise click.ClickException(str(e)) from e
    except ValueError as e:
        logger.error(str(e))
        raise click.ClickException(str(e)) from e


if __name__ == "__main__":
    main()

