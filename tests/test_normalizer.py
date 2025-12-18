"""Tests for the recipe normalizer service."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from recipe_normalizer.converters.units import UnitConverter
from recipe_normalizer.models import Ingredient, Recipe
from recipe_normalizer.parsers.registry import ParserRegistry
from recipe_normalizer.parsers.xml_parser import XmlRecipeParser
from recipe_normalizer.parsers.yaml_parser import YamlRecipeParser
from recipe_normalizer.services.normalizer import RecipeNormalizer


class TestRecipeNormalizer(unittest.TestCase):
    """Tests for the RecipeNormalizer service."""

    def setUp(self) -> None:
        """Create a normalizer instance for testing."""
        registry = ParserRegistry()
        registry.register(XmlRecipeParser())
        registry.register(YamlRecipeParser())
        converter = UnitConverter()
        self.normalizer = RecipeNormalizer(registry, converter)

    def test_normalize_directory_with_mixed_formats(self) -> None:
        """Test normalizing a directory with XML and YAML files."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            xml_content = """<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <name>pudding</name>
                <ingredients>
                    <item>milk</item>
                    <quantity>1</quantity>
                    <unit>gallon</unit>
                </ingredients>
                <preparations>Mix</preparations>
            </root>
            """
            (tmppath / "pudding.xml").write_text(xml_content)

            yaml_content = """
name: rice
ingredients:
  - item: rice
    quantity: 0.44
    unit: pound
preparations:
  - Cook
"""
            (tmppath / "rice.yaml").write_text(yaml_content)

            recipes = self.normalizer.normalize_directory(tmppath)

        self.assertEqual(len(recipes), 2)
        self.assertEqual(recipes[0].name, "rice")
        self.assertEqual(recipes[1].name, "pudding")

    def test_normalize_converts_units(self) -> None:
        """Test that unit conversion is applied during normalization."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            yaml_content = """
name: test
ingredients:
  - item: butter
    quantity: 1
    unit: pound
"""
            (tmppath / "test.yaml").write_text(yaml_content)

            recipes = self.normalizer.normalize_directory(tmppath)

        self.assertEqual(recipes[0].ingredients[0].unit, "gr")
        quantity = recipes[0].ingredients[0].quantity
        self.assertIsNotNone(quantity)
        self.assertGreaterEqual(quantity, 453)  # type: ignore[arg-type]
        self.assertLessEqual(quantity, 454)  # type: ignore[arg-type]

    def test_normalize_preserves_comments(self) -> None:
        """Test that ingredient comments are preserved."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            yaml_content = """
name: test
ingredients:
  - item: onion
    quantity: 1
    comment: diced
"""
            (tmppath / "test.yaml").write_text(yaml_content)

            recipes = self.normalizer.normalize_directory(tmppath)

        self.assertEqual(recipes[0].ingredients[0].comment, "diced")

    def test_export_to_json(self) -> None:
        """Test exporting recipes to JSON file."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            output_path = tmppath / "output.json"

            recipes = [
                Recipe(
                    name="test",
                    ingredients=[Ingredient(item="water", quantity=500, unit="ml")],
                    preparations=["Boil"],
                )
            ]

            self.normalizer.export_to_json(recipes, output_path)

            with open(output_path) as f:
                data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "test")
        self.assertEqual(data[0]["ingredients"][0]["item"], "water")

    def test_recipes_sorted_reverse_alphabetically(self) -> None:
        """Test that recipes are sorted reverse alphabetically by name."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "zebra.yaml").write_text("name: zebra\n")
            (tmppath / "apple.yaml").write_text("name: apple\n")
            (tmppath / "mango.yaml").write_text("name: mango\n")

            recipes = self.normalizer.normalize_directory(tmppath)

        names = [r.name for r in recipes]
        self.assertEqual(names, ["zebra", "mango", "apple"])

    def test_invalid_directory_raises_error(self) -> None:
        """Test that non-directory path raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.normalizer.normalize_directory(Path("/nonexistent/path"))
        self.assertIn("not a directory", str(context.exception))

    def test_ignores_unsupported_files(self) -> None:
        """Test that unsupported file types are ignored."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "valid.yaml").write_text("name: valid\n")
            (tmppath / "ignored.txt").write_text("some text")
            (tmppath / "ignored.json").write_text("{}")

            recipes = self.normalizer.normalize_directory(tmppath)

        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, "valid")


if __name__ == "__main__":
    unittest.main()
