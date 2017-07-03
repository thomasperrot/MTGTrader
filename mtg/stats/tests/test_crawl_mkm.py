from ..tasks import parse_page
from .mkm_fixtures import page_without_foil, page_with_foil, page_with_not_available


def test_parse_page_with_foil():
    """Asserts that pages with foil are correctly parsed.
    """

    parsed_page = parse_page(page_with_foil)
    assert parsed_page == {
        'available_foils': 147,
        'mean_price': 0.07,
        'min_foil': 0.05,
        'min_price': 0.01,
        'available_items': 1885
    }


def test_parse_page_without_foil():
    """Asserts that pages without foil are correctly parsed.
    """

    parsed_page = parse_page(page_without_foil)
    assert parsed_page == {
        'mean_price': 0.12,
        'min_price': 0.02,
        'available_items': 400
    }


def test_parse_page_without_available():
    """Asserts that pages with no items available are correctly parsed.
    """

    parsed_page = parse_page(page_with_not_available)
    assert parsed_page == {
        'available_items': 0
    }
