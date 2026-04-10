"""Tests for name_utils: snake_case, PascalCase, validate_name (T017)."""

import pytest

from scaffold_ca_python.core.name_utils import ScaffoldError, to_pascal_case, to_snake_case, validate_name

# ---------------------------------------------------------------------------
# to_snake_case
# ---------------------------------------------------------------------------


def test_snake_case_from_pascal() -> None:
    assert to_snake_case("MyOrder") == "my_order"


def test_snake_case_from_already_snake() -> None:
    assert to_snake_case("my_order") == "my_order"


def test_snake_case_from_all_caps() -> None:
    assert to_snake_case("HTTPClient") == "http_client"


def test_snake_case_with_numbers() -> None:
    assert to_snake_case("Project2025") == "project2025"


def test_snake_case_single_word() -> None:
    assert to_snake_case("Order") == "order"


# ---------------------------------------------------------------------------
# to_pascal_case
# ---------------------------------------------------------------------------


def test_pascal_case_from_snake() -> None:
    assert to_pascal_case("my_order") == "MyOrder"


def test_pascal_case_already_pascal() -> None:
    assert to_pascal_case("MyOrder") == "MyOrder"


def test_pascal_case_single_word() -> None:
    assert to_pascal_case("order") == "Order"


def test_pascal_case_multiple_underscores() -> None:
    assert to_pascal_case("create_order_use_case") == "CreateOrderUseCase"


# ---------------------------------------------------------------------------
# validate_name
# ---------------------------------------------------------------------------


def test_validate_name_accepts_pascal_case() -> None:
    assert validate_name("MyProject") == "MyProject"


def test_validate_name_accepts_snake_case() -> None:
    assert validate_name("my_project") == "my_project"


def test_validate_name_accepts_alphanumeric() -> None:
    assert validate_name("Project2025") == "Project2025"


def test_validate_name_rejects_starting_with_digit() -> None:
    with pytest.raises(ScaffoldError, match="Hint:"):
        validate_name("1Invalid")


def test_validate_name_rejects_spaces() -> None:
    with pytest.raises(ScaffoldError, match="Hint:"):
        validate_name("My Project")


def test_validate_name_rejects_hyphens() -> None:
    with pytest.raises(ScaffoldError, match="Hint:"):
        validate_name("my-project")


def test_validate_name_rejects_empty() -> None:
    with pytest.raises(ScaffoldError, match="Hint:"):
        validate_name("")


def test_validate_name_rejects_path_traversal() -> None:
    with pytest.raises(ScaffoldError, match="Hint:"):
        validate_name("../etc/passwd")
