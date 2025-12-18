"""YAML parser for recipe files."""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from recipe_normalizer.exceptions import FileReadError, ParseError, ValidationError
from recipe_normalizer.models import Ingredient, Recipe
from recipe_normalizer.parsers.base import RecipeParser

logger = logging.getLogger(__name__)


class YamlRecipeParser(RecipeParser):
    """Parser for YAML recipe files."""

    SUPPORTED_EXTENSIONS = {".yaml", ".yml"}

    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension."""
        return extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> Recipe:
        """Parse a YAML recipe file."""
        logger.debug("Parsing YAML file: %s", file_path)

        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise FileReadError(str(file_path), "File not found") from e
        except PermissionError as e:
            raise FileReadError(str(file_path), "Permission denied") from e
        except yaml.YAMLError as e:
            raise ParseError(str(file_path), f"Invalid YAML: {e}") from e

        if not isinstance(data, dict):
            raise ParseError(str(file_path), "Invalid YAML structure: expected a dict")

        try:
            name = self._parse_name(data, file_path)
            ingredients = self._parse_ingredients(data, file_path)
            preparations = self._parse_preparations(data)

            return Recipe(name=name, ingredients=ingredients, preparations=preparations)
        except PydanticValidationError as e:
            raise ValidationError("recipe", str(e)) from e

    @staticmethod
    def _parse_name(data: dict[str, Any], file_path: Path) -> str:
        """Extract recipe name from YAML data."""
        name = data.get("name")
        if not name:
            raise ParseError(str(file_path), "Recipe name is required")
        return str(name).strip()

    def _parse_ingredients(
        self, data: dict[str, Any], file_path: Path
    ) -> list[Ingredient]:
        """Extract ingredients list from YAML data."""
        ingredients_data = data.get("ingredients", [])
        if not isinstance(ingredients_data, list):
            return []

        ingredients: list[Ingredient] = []
        for ing_data in ingredients_data:
            ingredient = self._parse_single_ingredient(ing_data, file_path)
            if ingredient:
                ingredients.append(ingredient)

        return ingredients

    def _parse_single_ingredient(
        self, data: dict[str, Any], file_path: Path
    ) -> Ingredient | None:
        """Parse a single ingredient from dictionary data."""
        if not isinstance(data, dict):
            logger.warning("Skipping non-dict ingredient in %s", file_path)
            return None

        item = data.get("item")
        if not item:
            logger.warning("Skipping ingredient without item in %s", file_path)
            return None

        return Ingredient(
            item=str(item).strip(),
            quantity=self._parse_quantity(data),
            unit=self._parse_unit(data),
            comment=self._parse_comment(data),
        )

    @staticmethod
    def _parse_quantity(data: dict[str, Any]) -> float | None:
        """Parse quantity from ingredient data."""
        quantity = data.get("quantity")
        if quantity is None:
            return None
        try:
            return float(quantity)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_unit(data: dict[str, Any]) -> str | None:
        """Parse unit from ingredient data."""
        unit = data.get("unit")
        if unit is None:
            return None
        unit_str = str(unit).strip()
        return unit_str if unit_str else None

    @staticmethod
    def _parse_comment(data: dict[str, Any]) -> str | None:
        """Parse comment from ingredient data."""
        comment = data.get("comment")
        if comment is None:
            return None
        return str(comment).strip()

    @staticmethod
    def _parse_preparations(data: dict[str, Any]) -> list[str]:
        """Extract preparation steps from YAML data."""
        preparations_data = data.get("preparations", [])
        if not isinstance(preparations_data, list):
            return []

        return [str(prep).strip() for prep in preparations_data if prep]
