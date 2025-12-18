"""Recipe normalization service."""

import json
import logging
from pathlib import Path
from typing import Any

from recipe_normalizer.converters.units import UnitConverter
from recipe_normalizer.exceptions import (
    EmptyDirectoryError,
    FileWriteError,
    RecipeNormalizerError,
)
from recipe_normalizer.models import Ingredient, Recipe
from recipe_normalizer.parsers.registry import ParserRegistry

logger = logging.getLogger(__name__)


class RecipeNormalizer:
    """Service for normalizing recipes from various formats."""

    def __init__(
        self, parser_registry: ParserRegistry, unit_converter: UnitConverter
    ) -> None:
        """Initialize the normalizer.

        Args:
            parser_registry: Registry of available parsers
            unit_converter: Converter for unit normalization
        """
        self._parser_registry = parser_registry
        self._unit_converter = unit_converter

    def normalize_directory(
        self, input_dir: Path, skip_errors: bool = False
    ) -> list[Recipe]:
        """Normalize all recipe files in a directory.

        Args:
            input_dir: Directory containing recipe files
            skip_errors: If True, skip files that fail to parse

        Returns:
            List of normalized Recipe objects
        """
        if not input_dir.is_dir():
            raise ValueError(f"Input path is not a directory: {input_dir}")

        logger.info("Processing recipes from: %s", input_dir)

        recipes: list[Recipe] = []
        supported_extensions = self._parser_registry.get_supported_extensions()
        errors: list[tuple[Path, Exception]] = []

        for file_path in input_dir.iterdir():
            if file_path.is_file() and file_path.suffix in supported_extensions:
                try:
                    recipe = self._normalize_file(file_path)
                    recipes.append(recipe)
                    logger.debug("Successfully processed: %s", file_path)
                except RecipeNormalizerError as e:
                    if skip_errors:
                        logger.warning("Skipping file: %s - %s", file_path, e)
                        errors.append((file_path, e))
                    else:
                        raise

        if not recipes:
            raise EmptyDirectoryError(str(input_dir))

        if errors:
            logger.warning("Completed with %d errors", len(errors))

        logger.info("Successfully processed %d recipes", len(recipes))
        return self._sort_recipes(recipes)

    def _normalize_file(self, file_path: Path) -> Recipe:
        """Parse and normalize a single recipe file."""
        logger.debug("Normalizing file: %s", file_path)
        recipe = self._parser_registry.parse(file_path)
        return self._normalize_recipe(recipe)

    def _normalize_recipe(self, recipe: Recipe) -> Recipe:
        """Apply normalization to a recipe."""
        normalized_ingredients = [
            self._normalize_ingredient(ing) for ing in recipe.ingredients
        ]
        return Recipe(
            name=recipe.name,
            ingredients=normalized_ingredients,
            preparations=recipe.preparations,
        )

    def _normalize_ingredient(self, ingredient: Ingredient) -> Ingredient:
        """Normalize an ingredient's units."""
        if ingredient.quantity is None:
            return ingredient

        result = self._unit_converter.convert(ingredient.quantity, ingredient.unit)
        rounded_quantity = self._unit_converter.round_quantity(result.quantity)

        return Ingredient(
            item=ingredient.item,
            quantity=rounded_quantity,
            unit=result.unit if result.unit else None,
            comment=ingredient.comment,
        )

    @staticmethod
    def _sort_recipes(recipes: list[Recipe]) -> list[Recipe]:
        """Sort recipes reverse alphabetically by name."""
        return sorted(recipes, key=lambda r: r.name.lower(), reverse=True)

    def export_to_json(self, recipes: list[Recipe], output_path: Path) -> None:
        """Export normalized recipes to a JSON file.

        Args:
            recipes: List of normalized recipes
            output_path: Path for the output JSON file
        """
        data = self._recipes_to_dict(recipes)
        self._write_json(data, output_path)

    @staticmethod
    def _recipes_to_dict(recipes: list[Recipe]) -> list[dict[str, Any]]:
        """Convert recipes to dictionary format."""
        return [recipe.model_dump_clean() for recipe in recipes]

    @staticmethod
    def _write_json(data: list[dict[str, Any]], output_path: Path) -> None:
        """Write data to JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent="\t", ensure_ascii=False)
            logger.info("Output written to: %s", output_path)
        except PermissionError as e:
            raise FileWriteError(str(output_path), "Permission denied") from e
        except OSError as e:
            raise FileWriteError(str(output_path), str(e)) from e
