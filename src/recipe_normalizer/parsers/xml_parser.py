"""XML parser for recipe files."""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from recipe_normalizer.exceptions import FileReadError, ParseError, ValidationError
from recipe_normalizer.models import Ingredient, Recipe
from recipe_normalizer.parsers.base import RecipeParser

logger = logging.getLogger(__name__)


class XmlRecipeParser(RecipeParser):
    """Parser for XML recipe files."""

    SUPPORTED_EXTENSIONS = {".xml"}

    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension."""
        return extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> Recipe:
        """Parse an XML recipe file."""
        logger.debug("Parsing XML file: %s", file_path)

        try:
            tree = ET.parse(file_path)
        except FileNotFoundError as e:
            raise FileReadError(str(file_path), "File not found") from e
        except PermissionError as e:
            raise FileReadError(str(file_path), "Permission denied") from e
        except ET.ParseError as e:
            raise ParseError(str(file_path), f"Invalid XML: {e}") from e

        root = tree.getroot()

        try:
            name = self._parse_name(root, file_path)
            ingredients = self._parse_ingredients(root, file_path)
            preparations = self._parse_preparations(root)

            return Recipe(name=name, ingredients=ingredients, preparations=preparations)
        except PydanticValidationError as e:
            raise ValidationError("recipe", str(e)) from e

    @staticmethod
    def _parse_name(root: ET.Element, file_path: Path) -> str:
        """Extract recipe name from XML."""
        name_elem = root.find("name")
        if name_elem is None or name_elem.text is None:
            raise ParseError(str(file_path), "Recipe name is required")
        return name_elem.text.strip()

    def _parse_ingredients(self, root: ET.Element, file_path: Path) -> list[Ingredient]:
        """Extract ingredients list from XML."""
        ingredients: list[Ingredient] = []

        for ing_elem in root.findall("ingredients"):
            ingredient = self._parse_single_ingredient(ing_elem, file_path)
            if ingredient:
                ingredients.append(ingredient)

        return ingredients

    def _parse_single_ingredient(
        self, elem: ET.Element, file_path: Path
    ) -> Ingredient | None:
        """Parse a single ingredient element."""
        item_elem = elem.find("item")
        if item_elem is None or item_elem.text is None:
            logger.warning("Skipping ingredient without item in %s", file_path)
            return None

        item = item_elem.text.strip()
        quantity = self._parse_quantity(elem)
        unit = self._parse_unit(elem)
        comment = self._parse_comment(elem)

        return Ingredient(item=item, quantity=quantity, unit=unit, comment=comment)

    @staticmethod
    def _parse_quantity(elem: ET.Element) -> float | None:
        """Parse quantity from ingredient element."""
        qty_elem = elem.find("quantity")
        if qty_elem is None or qty_elem.text is None:
            return None
        try:
            return float(qty_elem.text.strip())
        except ValueError:
            return None

    @staticmethod
    def _parse_unit(elem: ET.Element) -> str | None:
        """Parse unit from ingredient element."""
        unit_elem = elem.find("unit")
        if unit_elem is None or unit_elem.text is None:
            return None
        unit_text = unit_elem.text.strip()
        return unit_text if unit_text else None

    @staticmethod
    def _parse_comment(elem: ET.Element) -> str | None:
        """Parse comment from ingredient element."""
        comment_elem = elem.find("comment")
        if comment_elem is None or comment_elem.text is None:
            return None
        return comment_elem.text.strip()

    @staticmethod
    def _parse_preparations(root: ET.Element) -> list[str]:
        """Extract preparation steps from XML."""
        preparations: list[str] = []

        for prep_elem in root.findall("preparations"):
            if prep_elem.text:
                preparations.append(prep_elem.text.strip())

        return preparations
