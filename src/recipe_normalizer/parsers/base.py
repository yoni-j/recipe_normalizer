"""Base parser interface for recipe files."""

from abc import ABC, abstractmethod
from pathlib import Path

from recipe_normalizer.models import Recipe


class RecipeParser(ABC):
    """Abstract base class for recipe parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> Recipe:
        """Parse a recipe file and return a Recipe object.

        Args:
            file_path: Path to the recipe file

        Returns:
            Parsed Recipe object

        Raises:
            ValueError: If the file cannot be parsed
        """

    @abstractmethod
    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension.

        Args:
            extension: File extension (e.g., '.xml', '.yaml')

        Returns:
            True if this parser can handle the file type
        """
