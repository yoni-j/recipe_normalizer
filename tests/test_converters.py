"""Tests for unit conversion."""

import unittest

from recipe_normalizer.converters.units import UnitConverter


class TestUnitConverter(unittest.TestCase):
    """Tests for the UnitConverter class."""

    def setUp(self) -> None:
        """Create a converter instance for testing."""
        self.converter = UnitConverter()

    def test_convert_gallon_to_liter(self) -> None:
        """Test gallon to liter conversion."""
        result = self.converter.convert(1, "gallon")
        self.assertEqual(result.unit, "liter")
        self.assertGreaterEqual(result.quantity, 3.78)
        self.assertLessEqual(result.quantity, 3.79)

    def test_convert_pound_to_grams(self) -> None:
        """Test pound to grams conversion."""
        result = self.converter.convert(0.44, "pound")
        self.assertEqual(result.unit, "gr")
        self.assertGreaterEqual(result.quantity, 199)
        self.assertLessEqual(result.quantity, 200)

    def test_convert_fluid_ounce_to_ml(self) -> None:
        """Test fluid ounce to ml conversion."""
        result = self.converter.convert(2.02, "fl. oz.")
        self.assertEqual(result.unit, "ml")
        self.assertGreaterEqual(result.quantity, 59)
        self.assertLessEqual(result.quantity, 60)

    def test_convert_cups_to_ml(self) -> None:
        """Test cups to ml conversion (metric cup = 240ml)."""
        result = self.converter.convert(2, "cups")
        self.assertEqual(result.unit, "ml")
        self.assertEqual(result.quantity, 480)

    def test_preserve_metric_units(self) -> None:
        """Test that metric units are preserved."""
        result = self.converter.convert(10, "ml")
        self.assertEqual(result.unit, "ml")
        self.assertEqual(result.quantity, 10)

    def test_handle_none_unit(self) -> None:
        """Test handling of None unit (count-based ingredients)."""
        result = self.converter.convert(12, None)
        self.assertEqual(result.unit, "")
        self.assertEqual(result.quantity, 12)

    def test_handle_empty_unit(self) -> None:
        """Test handling of empty string unit."""
        result = self.converter.convert(5, "")
        self.assertEqual(result.unit, "")
        self.assertEqual(result.quantity, 5)

    def test_handle_unknown_unit(self) -> None:
        """Test handling of unknown units (preserved as-is)."""
        result = self.converter.convert(3, "pinch")
        self.assertEqual(result.unit, "pinch")
        self.assertEqual(result.quantity, 3)

    def test_convert_tablespoon_to_ml(self) -> None:
        """Test tablespoon to ml conversion."""
        result = self.converter.convert(1, "tablespoon")
        self.assertEqual(result.unit, "ml")
        self.assertGreaterEqual(result.quantity, 14)
        self.assertLessEqual(result.quantity, 15)

    def test_convert_teaspoon_to_ml(self) -> None:
        """Test teaspoon to ml conversion."""
        result = self.converter.convert(1, "teaspoon")
        self.assertEqual(result.unit, "ml")
        self.assertGreaterEqual(result.quantity, 4)
        self.assertLessEqual(result.quantity, 5)

    def test_convert_ounce_to_grams(self) -> None:
        """Test ounce to grams conversion."""
        result = self.converter.convert(1, "ounce")
        self.assertEqual(result.unit, "gr")
        self.assertGreaterEqual(result.quantity, 28)
        self.assertLessEqual(result.quantity, 29)


class TestRoundQuantity(unittest.TestCase):
    """Tests for quantity rounding."""

    def setUp(self) -> None:
        """Create a converter instance for testing."""
        self.converter = UnitConverter()

    def test_truncate_to_two_decimals_for_small_values(self) -> None:
        """Test truncation to two decimal places for values < 10."""
        result = self.converter.round_quantity(3.78541)
        self.assertEqual(result, 3.78)

    def test_whole_number_returns_int(self) -> None:
        """Test that whole numbers return as int."""
        result = self.converter.round_quantity(5.0)
        self.assertEqual(result, 5)
        self.assertIsInstance(result, int)

    def test_preserve_meaningful_decimals(self) -> None:
        """Test that meaningful decimals are preserved."""
        result = self.converter.round_quantity(2.5)
        self.assertEqual(result, 2.5)


if __name__ == "__main__":
    unittest.main()
