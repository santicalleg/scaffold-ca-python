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


# T009: US2 — to_snake_case normalises hyphens
def test_to_snake_case_from_kebab() -> None:
    assert to_snake_case("my-project") == "my_project"


def test_to_snake_case_multi_word_kebab() -> None:
    assert to_snake_case("my-order-service") == "my_order_service"


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


# T013: US3 — to_pascal_case works correctly after kebab normalisation
def test_to_pascal_case_from_snake_after_kebab_normalisation() -> None:
    assert to_pascal_case(to_snake_case("my-model")) == "MyModel"
    assert to_pascal_case(to_snake_case("my-order-service")) == "MyOrderService"


# ---------------------------------------------------------------------------
# validate_name
# ---------------------------------------------------------------------------


def test_validate_name_rejects_pascal_case() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("MyProject")


def test_validate_name_accepts_snake_case() -> None:
    assert validate_name("my_project") == "my_project"


def test_validate_name_accepts_alphanumeric() -> None:
    assert validate_name("project2025") == "project2025"


def test_validate_name_rejects_starting_with_digit() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("1Invalid")


def test_validate_name_rejects_spaces() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("My Project")


def test_validate_name_accepts_kebab_case() -> None:
    assert validate_name("my-project") == "my-project"


def test_validate_name_rejects_empty() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("")


def test_validate_name_rejects_path_traversal() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("../etc/passwd")


# T003: additional US1 edge cases
def test_validate_name_accepts_multi_word_kebab() -> None:
    assert validate_name("my-order-service") == "my-order-service"


def test_validate_name_rejects_camel_case() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("myProject")


def test_validate_name_rejects_mixed_case_with_hyphen() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("My-Project")


def test_validate_name_rejects_consecutive_hyphens() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("my--project")


def test_validate_name_rejects_leading_hyphen() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("-myproject")


def test_validate_name_rejects_trailing_underscore() -> None:
    with pytest.raises(ScaffoldError, match="kebab-case"):
        validate_name("myproject_")
