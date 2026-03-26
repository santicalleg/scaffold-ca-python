"""Name normalisation utilities for scaffold-ca-python."""
from __future__ import annotations

import keyword
import re


def to_snake_case(name: str) -> str:
    """Convert a name to snake_case.

    Handles PascalCase, camelCase, hyphen-case, and space-separated inputs.
    """
    # Replace hyphens and spaces with underscores
    name = re.sub(r"[-\s]+", "_", name)
    # Insert underscore before uppercase letters preceded by lowercase/digit
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # Insert underscore before a run of uppercase letters followed by lowercase
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = name.lower()
    # Collapse multiple underscores
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def to_pascal_case(name: str) -> str:
    """Convert a name to PascalCase."""
    snake = to_snake_case(name)
    return "".join(part.capitalize() for part in snake.split("_"))


def validate_name(name: str) -> tuple[str, bool]:
    """Return (normalised_name, was_normalised).

    Raises ValueError for reserved keywords or names that cannot be safely
    normalised to a valid Python identifier.
    """
    if not name or not name.strip():
        raise ValueError("Component name must not be empty.")

    normalised = to_snake_case(name)

    if not normalised:
        raise ValueError(
            f"Name {name!r} cannot be normalised to a valid Python identifier."
        )

    if not re.match(r"^[a-z][a-z0-9_]*$", normalised):
        raise ValueError(
            f"Name {name!r} normalises to {normalised!r}, which is not a valid "
            "Python identifier. Use letters, digits, and underscores; start with a letter."
        )

    if is_reserved_keyword(normalised):
        raise ValueError(
            f"Name {normalised!r} is a Python reserved keyword and cannot be used "
            "as a component name. Choose a different name."
        )

    was_normalised = normalised != name
    return normalised, was_normalised


def is_reserved_keyword(name: str) -> bool:
    """Return True if *name* is a Python keyword or soft keyword."""
    return keyword.iskeyword(name) or keyword.issoftkeyword(name)


def extract_package_root(package: str) -> str:
    """Return the last dot-segment of *package* as the Python package root dir.

    Examples:
        "org.example.payments" -> "payments"
        "my_app"               -> "my_app"
    """
    if not package:
        raise ValueError("Package name must not be empty.")
    segment = package.split(".")[-1]
    normalised, _ = validate_name(segment)
    return normalised
