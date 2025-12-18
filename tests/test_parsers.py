"""Tests for recipe parsers."""

import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from recipe_normalizer.exceptions import (
    FileReadError,
    ParseError,
    UnsupportedFormatError,
)
from recipe_normalizer.parsers.registry import ParserRegistry
from recipe_normalizer.parsers.xml_parser import XmlRecipeParser
from recipe_normalizer.parsers.yaml_parser import YamlRecipeParser


class TestXmlRecipeParser(unittest.TestCase):
    """Tests for the XML recipe parser."""

    def setUp(self) -> None:
        """Create a parser instance for testing."""
        self.parser = XmlRecipeParser()

    def test_supports_xml_extension(self) -> None:
        """Test that parser supports .xml extension."""
        self.assertTrue(self.parser.supports_extension(".xml"))
        self.assertTrue(self.parser.supports_extension(".XML"))
        self.assertFalse(self.parser.supports_extension(".yaml"))

    def test_parse_simple_recipe(self) -> None:
        """Test parsing a simple XML recipe."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <name>Test Recipe</name>
            <ingredients>
                <item>flour</item>
                <quantity>200</quantity>
                <unit>gr</unit>
            </ingredients>
            <preparations>Mix well</preparations>
        </root>
        """
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            recipe = self.parser.parse(Path(f.name))

        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(len(recipe.ingredients), 1)
        self.assertEqual(recipe.ingredients[0].item, "flour")
        self.assertEqual(recipe.ingredients[0].quantity, 200)
        self.assertEqual(recipe.ingredients[0].unit, "gr")
        self.assertEqual(recipe.preparations, ["Mix well"])

    def test_parse_recipe_with_comment(self) -> None:
        """Test parsing recipe with ingredient comment."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <name>Eggs</name>
            <ingredients>
                <item>eggs</item>
                <quantity>3</quantity>
                <unit></unit>
                <comment>room temperature</comment>
            </ingredients>
        </root>
        """
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            recipe = self.parser.parse(Path(f.name))

        self.assertEqual(recipe.ingredients[0].comment, "room temperature")
        self.assertIsNone(recipe.ingredients[0].unit)

    def test_parse_missing_name_raises_error(self) -> None:
        """Test that missing recipe name raises ParseError."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <ingredients>
                <item>flour</item>
            </ingredients>
        </root>
        """
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            with self.assertRaises(ParseError) as context:
                self.parser.parse(Path(f.name))
            self.assertIn("Recipe name is required", str(context.exception))

    def test_parse_invalid_xml_raises_error(self) -> None:
        """Test that invalid XML raises ParseError."""
        xml_content = "not valid xml <<<"
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            with self.assertRaises(ParseError) as context:
                self.parser.parse(Path(f.name))
            self.assertIn("Invalid XML", str(context.exception))

    def test_parse_nonexistent_file_raises_error(self) -> None:
        """Test that nonexistent file raises FileReadError."""
        with self.assertRaises(FileReadError):
            self.parser.parse(Path("/nonexistent/file.xml"))


class TestYamlRecipeParser(unittest.TestCase):
    """Tests for the YAML recipe parser."""

    def setUp(self) -> None:
        """Create a parser instance for testing."""
        self.parser = YamlRecipeParser()

    def test_supports_yaml_extensions(self) -> None:
        """Test that parser supports .yaml and .yml extensions."""
        self.assertTrue(self.parser.supports_extension(".yaml"))
        self.assertTrue(self.parser.supports_extension(".yml"))
        self.assertTrue(self.parser.supports_extension(".YAML"))
        self.assertFalse(self.parser.supports_extension(".xml"))

    def test_parse_simple_recipe(self) -> None:
        """Test parsing a simple YAML recipe."""
        yaml_content = """
name: Test Recipe
ingredients:
  - item: rice
    quantity: 200
    unit: gr
preparations:
  - Cook rice
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            recipe = self.parser.parse(Path(f.name))

        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(len(recipe.ingredients), 1)
        self.assertEqual(recipe.ingredients[0].item, "rice")
        self.assertEqual(recipe.ingredients[0].quantity, 200)
        self.assertEqual(recipe.ingredients[0].unit, "gr")
        self.assertEqual(recipe.preparations, ["Cook rice"])

    def test_parse_recipe_with_comment(self) -> None:
        """Test parsing recipe with ingredient comment."""
        yaml_content = """
name: Onion Dish
ingredients:
  - item: onion
    quantity: 1
    comment: white or red
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            recipe = self.parser.parse(Path(f.name))

        self.assertEqual(recipe.ingredients[0].comment, "white or red")
        self.assertIsNone(recipe.ingredients[0].unit)

    def test_parse_missing_name_raises_error(self) -> None:
        """Test that missing recipe name raises ParseError."""
        yaml_content = """
ingredients:
  - item: flour
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            with self.assertRaises(ParseError) as context:
                self.parser.parse(Path(f.name))
            self.assertIn("Recipe name is required", str(context.exception))

    def test_parse_invalid_yaml_raises_error(self) -> None:
        """Test that invalid YAML raises ParseError."""
        yaml_content = "invalid: yaml: content:"
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            with self.assertRaises(ParseError) as context:
                self.parser.parse(Path(f.name))
            self.assertIn("Invalid YAML", str(context.exception))

    def test_parse_nonexistent_file_raises_error(self) -> None:
        """Test that nonexistent file raises FileReadError."""
        with self.assertRaises(FileReadError):
            self.parser.parse(Path("/nonexistent/file.yaml"))


class TestParserRegistry(unittest.TestCase):
    """Tests for the parser registry."""

    def setUp(self) -> None:
        """Create a registry with all parsers registered."""
        self.registry = ParserRegistry()
        self.registry.register(XmlRecipeParser())
        self.registry.register(YamlRecipeParser())

    def test_get_parser_for_xml(self) -> None:
        """Test getting parser for XML files."""
        parser = self.registry.get_parser_for_file(Path("recipe.xml"))
        self.assertIsInstance(parser, XmlRecipeParser)

    def test_get_parser_for_yaml(self) -> None:
        """Test getting parser for YAML files."""
        parser = self.registry.get_parser_for_file(Path("recipe.yaml"))
        self.assertIsInstance(parser, YamlRecipeParser)

    def test_get_parser_for_unknown_type(self) -> None:
        """Test that unknown file types return None."""
        parser = self.registry.get_parser_for_file(Path("recipe.json"))
        self.assertIsNone(parser)

    def test_parse_unsupported_raises_error(self) -> None:
        """Test that parsing unsupported files raises UnsupportedFormatError."""
        with self.assertRaises(UnsupportedFormatError) as context:
            self.registry.parse(Path("recipe.txt"))
        self.assertIn("Unsupported file format", str(context.exception))

    def test_get_supported_extensions(self) -> None:
        """Test getting all supported extensions."""
        extensions = self.registry.get_supported_extensions()
        self.assertIn(".xml", extensions)
        self.assertIn(".yaml", extensions)
        self.assertIn(".yml", extensions)


if __name__ == "__main__":
    unittest.main()
