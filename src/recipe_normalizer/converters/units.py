"""Unit conversion utilities using pint for imperial to metric conversion."""

import math
from typing import NamedTuple

import pint


class ConversionResult(NamedTuple):
    """Result of a unit conversion."""

    quantity: float
    unit: str


class UnitConverter:
    """Handles conversion of imperial units to metric units using pint.

    Assumptions:
    - Cups are converted to ml (volume measurement) using metric cup (240ml)
    - Weight units (pound, oz) convert to grams
    - Volume units (gallon, fl oz, cup) convert to ml or liter
    - Uses US customary units with cooking-friendly definitions
    """

    UNIT_ALIASES: dict[str, str] = {
        "fl. oz.": "floz",
        "fl oz": "floz",
        "gr": "gram",
    }

    VOLUME_TARGET = "milliliter"
    VOLUME_TARGET_LARGE = "liter"
    WEIGHT_TARGET = "gram"
    VOLUME_THRESHOLD_ML = 1000

    def __init__(self) -> None:
        """Initialize the converter with a pint unit registry."""
        self._ureg: pint.UnitRegistry[pint.Quantity[float]] = pint.UnitRegistry(
            on_redefinition="ignore"
        )
        self._define_cooking_units()

    def _define_cooking_units(self) -> None:
        """Define cooking-friendly unit conversions.

        Uses metric cup (240ml) instead of US cup (236.588ml)
        for more practical cooking measurements.
        """
        self._ureg.define("cup = 240 * milliliter")

    def _normalize_unit_name(self, unit: str) -> str:
        """Normalize unit name for pint compatibility."""
        normalized = unit.lower().strip()
        return self.UNIT_ALIASES.get(normalized, normalized)

    def _is_volume_unit(self, unit_str: str) -> bool:
        """Check if a unit is a volume measurement."""
        try:
            unit = self._ureg.parse_expression(unit_str)
            return unit.dimensionality == self._ureg.milliliter.dimensionality
        except pint.errors.UndefinedUnitError:
            return False

    def _is_weight_unit(self, unit_str: str) -> bool:
        """Check if a unit is a weight measurement."""
        try:
            unit = self._ureg.parse_expression(unit_str)
            return unit.dimensionality == self._ureg.gram.dimensionality
        except pint.errors.UndefinedUnitError:
            return False

    def _format_output_unit(self, unit: str) -> str:
        """Format output unit name for consistency."""
        unit_map = {
            "milliliter": "ml",
            "liter": "liter",
            "gram": "gr",
        }
        return unit_map.get(unit, unit)

    def convert(self, quantity: float | int, unit: str | None) -> ConversionResult:
        """Convert a quantity from imperial to metric units.

        Args:
            quantity: The amount to convert
            unit: The unit of measurement (may be None for count-based ingredients)

        Returns:
            ConversionResult with the converted quantity and unit
        """
        if unit is None or unit.strip() == "":
            return ConversionResult(quantity=float(quantity), unit="")

        normalized_unit = self._normalize_unit_name(unit)

        try:
            source_quantity = self._ureg.Quantity(quantity, normalized_unit)

            if self._is_volume_unit(normalized_unit):
                return self._convert_volume(source_quantity)

            if self._is_weight_unit(normalized_unit):
                return self._convert_weight(source_quantity)

            return ConversionResult(quantity=float(quantity), unit=unit)

        except pint.errors.UndefinedUnitError:
            return ConversionResult(quantity=float(quantity), unit=unit)

    def _convert_volume(
        self, source_quantity: pint.Quantity  # type: ignore[type-arg]
    ) -> ConversionResult:
        """Convert volume quantity to metric."""
        converted = source_quantity.to(self.VOLUME_TARGET)
        if converted.magnitude >= self.VOLUME_THRESHOLD_ML:
            converted = source_quantity.to(self.VOLUME_TARGET_LARGE)
        target_unit = self._format_output_unit(str(converted.units))
        return ConversionResult(quantity=float(converted.magnitude), unit=target_unit)

    def _convert_weight(
        self, source_quantity: pint.Quantity  # type: ignore[type-arg]
    ) -> ConversionResult:
        """Convert weight quantity to metric."""
        converted = source_quantity.to(self.WEIGHT_TARGET)
        target_unit = self._format_output_unit(str(converted.units))
        return ConversionResult(quantity=float(converted.magnitude), unit=target_unit)

    def round_quantity(self, quantity: float) -> float | int:
        """Round quantity using cooking-friendly precision rules.

        For quantities >= 10, rounds to nearest integer.
        For quantities < 10, truncates to 2 decimal places.

        Args:
            quantity: The quantity to round

        Returns:
            Rounded quantity (int if whole number, float otherwise)
        """
        if quantity >= 10:
            return round(quantity)
        truncated = math.floor(quantity * 100) / 100
        if truncated == int(truncated):
            return int(truncated)
        return truncated
