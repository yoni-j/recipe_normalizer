"""Registry for managing recipe parsers."""

import logging
from pathlib import Path

from recipe_normalizer.exceptions import UnsupportedFormatError
from recipe_normalizer.models import Recipe
from recipe_normalizer.parsers.base import RecipeParser

logger = logging.getLogger(__name__)


class ParserRegistry:
    """Registry that manages and dispatches to appropriate parsers."""

    def __init__(self) -> None:
        """Initialize an empty parser registry."""
        self._parsers: list[RecipeParser] = []

    def register(self, parser: RecipeParser) -> None:
        """Register a parser with the registry.

        Args:
            parser: Parser instance to register
        """
        self._parsers.append(parser)
        logger.debug("Registered parser: %s", type(parser).__name__)

    def get_parser_for_file(self, file_path: Path) -> RecipeParser | None:
        """Find a parser that can handle the given file.

        Args:
            file_path: Path to the file to parse

        Returns:
            A parser that supports the file extension, or None if not found
        """
        extension = file_path.suffix
        for parser in self._parsers:
            if parser.supports_extension(extension):
                return parser
        return None

    def parse(self, file_path: Path) -> Recipe:
        """Parse a recipe file using the appropriate parser.

        Args:
            file_path: Path to the recipe file

        Returns:
            Parsed Recipe object

        Raises:
            UnsupportedFormatError: If no parser supports the file type
        """
        parser = self.get_parser_for_file(file_path)
        if parser is None:
            raise UnsupportedFormatError(str(file_path), file_path.suffix)
        return parser.parse(file_path)

    def get_supported_extensions(self) -> set[str]:
        """Get all supported file extensions.

        Returns:
            Set of supported file extensions
        """
        extensions: set[str] = set()
        for parser in self._parsers:
            if hasattr(parser, "SUPPORTED_EXTENSIONS"):
                extensions.update(parser.SUPPORTED_EXTENSIONS)
        return extensions
