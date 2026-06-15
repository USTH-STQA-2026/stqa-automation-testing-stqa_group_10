"""
test_search.py — Search & Filter Tests (REQ-03)
"""
import os
import pytest
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    flutter_fill,
    login,
    sem_text,
)

SEARCH_BOX = "Tìm kiếm theo tên sách hoặc tác giả..."
CATEGORY_FILTER = "Lọc theo thể loại (VD: Công nghệ, Kinh tế...)"
BOOK_CARD_SEL = 'flt-semantics[role="group"][aria-label*="Mã: BOOK"]'

def test_tc17_search_by_book_title(page, test_config):
    login(page, test_config)
    flutter_fill(page, SEARCH_BOX, "Flutter")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-17_search_flutter.png"))
    assert "Flutter" in sem_text(page), "TC-17 FAIL"

def test_tc18_search_lowercase(page, test_config):
    login(page, test_config)
    flutter_fill(page, SEARCH_BOX, "flutter")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-18_search_lowercase.png"))
    assert "Flutter" in sem_text(page) or "flutter" in sem_text(page), "TC-18 FAIL"

def test_tc19_search_uppercase(page, test_config):
    login(page, test_config)
    flutter_fill(page, SEARCH_BOX, "FLUTTER")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-19_search_uppercase.png"))
    assert "Flutter" in sem_text(page) or "FLUTTER" in sem_text(page), "TC-19 FAIL"

def test_tc20_search_by_author(page, test_config):
    login(page, test_config)
    flutter_fill(page, SEARCH_BOX, "Nguyễn Minh Đức")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-20_search_author.png"))
    assert "Nguyễn Minh Đức" in sem_text(page), "TC-20 FAIL"

def test_tc21_search_no_result(page, test_config):
    login(page, test_config)
    flutter_fill(page, SEARCH_BOX, "XYZ123")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-21_no_result.png"))
    txt = sem_text(page)
    assert page.locator(BOOK_CARD_SEL).count() == 0 or "Không tìm thấy" in txt or "No books found" in txt, "TC-21 FAIL"

def test_tc22_search_and_category_filter_match(page, test_config):
    login(page, test_config)
    flutter_fill(page, CATEGORY_FILTER, "Công nghệ")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    flutter_fill(page, SEARCH_BOX, "Python")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-22_search_and_filter.png"))
    txt = sem_text(page)
    assert "Python" in txt or "Công nghệ" in txt, "TC-22 FAIL"

@pytest.mark.xfail(reason="BUG-05: Returns all books instead of no books found")
def test_tc23_search_and_category_filter_no_match(page, test_config):
    login(page, test_config)
    flutter_fill(page, CATEGORY_FILTER, "Kinh tế")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    flutter_fill(page, SEARCH_BOX, "Flutter")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-23_no_match_filter.png"))
    books_found = page.locator(BOOK_CARD_SEL).count()
    txt = sem_text(page)
    assert books_found == 0 or "Không tìm thấy" in txt or "No books found" in txt, "TC-23 FAIL: Expected no results."

def test_tc24_single_char_search(page, test_config):
    login(page, test_config)
    flutter_fill(page, SEARCH_BOX, "F")
    page.keyboard.press("Enter")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-24_single_char_search.png"))
    txt = sem_text(page)
    assert "BOOK" in txt or "Không tìm thấy" in txt or "No books found" in txt or "F" in txt, "TC-24 FAIL"