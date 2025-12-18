"""Tests for recipe data models."""

import unittest

from pydantic import ValidationError

from recipe_normalizer.models import Ingredient, Recipe


class TestIngredient(unittest.TestCase):
    """Tests for the Ingredient model."""

    def test_create_basic_ingredient(self) -> None:
        """Test creating an ingredient with minimal data."""
        ingredient = Ingredient(item="flour")
        self.assertEqual(ingredient.item, "flour")
        self.assertIsNone(ingredient.quantity)
        self.assertIsNone(ingredient.unit)
        self.assertIsNone(ingredient.comment)

    def test_create_full_ingredient(self) -> None:
        """Test creating an ingredient with all fields."""
        ingredient = Ingredient(
            item="sugar", quantity=200, unit="gr", comment="white sugar"
        )
        self.assertEqual(ingredient.item, "sugar")
        self.assertEqual(ingredient.quantity, 200)
        self.assertEqual(ingredient.unit, "gr")
        self.assertEqual(ingredient.comment, "white sugar")

    def test_model_dump_clean_excludes_none(self) -> None:
        """Test that model_dump_clean excludes None values."""
        ingredient = Ingredient(item="salt", quantity=5)
        result = ingredient.model_dump_clean()

        self.assertEqual(result, {"item": "salt", "quantity": 5})
        self.assertNotIn("unit", result)
        self.assertNotIn("comment", result)

    def test_model_dump_clean_excludes_empty_unit(self) -> None:
        """Test that model_dump_clean excludes empty unit strings."""
        ingredient = Ingredient(item="egg", quantity=2, unit="")
        result = ingredient.model_dump_clean()

        self.assertEqual(result, {"item": "egg", "quantity": 2})
        self.assertNotIn("unit", result)

    def test_quantity_rounding(self) -> None:
        """Test that float quantities are rounded appropriately."""
        ingredient = Ingredient(item="milk", quantity=3.78541, unit="liter")
        result = ingredient.model_dump_clean()

        self.assertEqual(result["quantity"], 3.79)

    def test_whole_number_quantity_as_int(self) -> None:
        """Test that whole numbers are serialized as integers."""
        ingredient = Ingredient(item="eggs", quantity=12.0)
        result = ingredient.model_dump_clean()

        self.assertEqual(result["quantity"], 12)
        self.assertIsInstance(result["quantity"], int)

    def test_empty_item_raises_error(self) -> None:
        """Test that empty item name raises ValidationError."""
        with self.assertRaises(ValidationError):
            Ingredient(item="")

    def test_whitespace_item_raises_error(self) -> None:
        """Test that whitespace-only item name raises ValidationError."""
        with self.assertRaises(ValidationError):
            Ingredient(item="   ")

    def test_negative_quantity_raises_error(self) -> None:
        """Test that negative quantity raises ValidationError."""
        with self.assertRaises(ValidationError):
            Ingredient(item="flour", quantity=-1)

    def test_item_name_is_stripped(self) -> None:
        """Test that item names are stripped of whitespace."""
        ingredient = Ingredient(item="  flour  ")
        self.assertEqual(ingredient.item, "flour")


class TestRecipe(unittest.TestCase):
    """Tests for the Recipe model."""

    def test_create_basic_recipe(self) -> None:
        """Test creating a recipe with minimal data."""
        recipe = Recipe(name="Test Recipe")
        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(recipe.ingredients, [])
        self.assertEqual(recipe.preparations, [])

    def test_create_full_recipe(self) -> None:
        """Test creating a recipe with all fields."""
        ingredients = [
            Ingredient(item="flour", quantity=200, unit="gr"),
            Ingredient(item="egg", quantity=2),
        ]
        preparations = ["Mix ingredients", "Bake at 180C"]

        recipe = Recipe(
            name="Cake", ingredients=ingredients, preparations=preparations
        )

        self.assertEqual(recipe.name, "Cake")
        self.assertEqual(len(recipe.ingredients), 2)
        self.assertEqual(len(recipe.preparations), 2)

    def test_model_dump_clean(self) -> None:
        """Test converting recipe to clean dictionary."""
        recipe = Recipe(
            name="Test",
            ingredients=[Ingredient(item="water", quantity=500, unit="ml")],
            preparations=["Boil water"],
        )
        result = recipe.model_dump_clean()

        expected = {
            "name": "Test",
            "ingredients": [{"item": "water", "quantity": 500, "unit": "ml"}],
            "preparations": ["Boil water"],
        }
        self.assertEqual(result, expected)

    def test_empty_name_raises_error(self) -> None:
        """Test that empty recipe name raises ValidationError."""
        with self.assertRaises(ValidationError):
            Recipe(name="")

    def test_whitespace_name_raises_error(self) -> None:
        """Test that whitespace-only recipe name raises ValidationError."""
        with self.assertRaises(ValidationError):
            Recipe(name="   ")

    def test_name_is_stripped(self) -> None:
        """Test that recipe names are stripped of whitespace."""
        recipe = Recipe(name="  Test Recipe  ")
        self.assertEqual(recipe.name, "Test Recipe")


if __name__ == "__main__":
    unittest.main()
