"""Custom exceptions for the recipe normalizer."""


class RecipeNormalizerError(Exception):
    """Base exception for all recipe normalizer errors."""


class ParseError(RecipeNormalizerError):
    """Raised when a recipe file cannot be parsed."""

    def __init__(self, file_path: str, message: str) -> None:
        self.file_path = file_path
        self.message = message
        super().__init__(f"Failed to parse '{file_path}': {message}")


class ValidationError(RecipeNormalizerError):
    """Raised when recipe data fails validation."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"Validation error in '{field}': {message}")


class FileReadError(RecipeNormalizerError):
    """Raised when a file cannot be read."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Cannot read file '{file_path}': {reason}")


class FileWriteError(RecipeNormalizerError):
    """Raised when output cannot be written."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Cannot write to '{file_path}': {reason}")


class UnsupportedFormatError(RecipeNormalizerError):
    """Raised when a file format is not supported."""

    def __init__(self, file_path: str, extension: str) -> None:
        self.file_path = file_path
        self.extension = extension
        super().__init__(f"Unsupported file format '{extension}' for '{file_path}'")


class EmptyDirectoryError(RecipeNormalizerError):
    """Raised when no recipe files are found in a directory."""

    def __init__(self, directory: str) -> None:
        self.directory = directory
        super().__init__(f"No recipe files found in '{directory}'")
