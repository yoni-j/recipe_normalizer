"""Data models for recipe representation using Pydantic."""

from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator


class Ingredient(BaseModel):
    """Represents a single ingredient in a recipe."""

    model_config = ConfigDict(extra="ignore")

    item: str
    quantity: float | int | None = None
    unit: str | None = None
    comment: str | None = None

    @field_validator("item")
    @classmethod
    def item_must_not_be_empty(cls, v: str) -> str:
        """Validate that item name is not empty or whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Item name cannot be empty")
        return stripped

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: float | int | None) -> float | int | None:
        """Validate that quantity is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative")
        return v

    @field_serializer("quantity")
    def serialize_quantity(self, value: float | int | None) -> float | int | None:
        """Round quantity to 2 decimal places if float."""
        if value is None:
            return None
        if isinstance(value, float):
            rounded = round(value, 2)
            if rounded == int(rounded):
                return int(rounded)
            return rounded
        return value

    def model_dump_clean(self) -> dict[str, Any]:
        """Export model excluding None/empty values."""
        data = self.model_dump(exclude_none=True)
        if "unit" in data and not data["unit"]:
            del data["unit"]
        return data


class Recipe(BaseModel):
    """Represents a cooking recipe."""

    model_config = ConfigDict(extra="ignore")

    name: str
    ingredients: list[Ingredient] = []
    preparations: list[str] = []

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that recipe name is not empty or whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Recipe name cannot be empty")
        return stripped

    def model_dump_clean(self) -> dict[str, Any]:
        """Export model with cleaned ingredients."""
        return {
            "name": self.name,
            "ingredients": [ing.model_dump_clean() for ing in self.ingredients],
            "preparations": self.preparations,
        }
