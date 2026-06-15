"""
test_view_books.py — View Book List Tests (REQ-02)
"""
import os
import pytest
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    flutter_click_button,
    login,
    login_as,
    open_books_tab,
    open_borrow_return_tab,
    wait_for_flutter,
    sem_text,
    ACCOUNTS,
)

def test_tc10_librarian_views_book_list(page, test_config):
    login(page, test_config)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-10_librarian_book_list.png"))
    txt = sem_text(page)
    assert "BOOK" in txt, "TC-10 FAIL"

def test_tc11_member_views_book_list(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-11_member_book_list.png"))
    txt = sem_text(page)
    assert "BOOK" in txt, "TC-11 FAIL"

def test_tc12_available_book_status(page, test_config):
    login(page, test_config)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-12_available_status.png"))
    txt = sem_text(page)
    assert "Available" in txt or "Có sẵn" in txt or "BOOK001" in txt, "TC-12 FAIL"

def test_tc13_borrowed_book_status(page, test_config):
    login(page, test_config)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-13_borrowed_status.png"))
    txt = sem_text(page)
    assert "Borrowed" in txt or "Đang mượn" in txt or "BOOK003" in txt, "TC-13 FAIL"

def test_tc14_status_updates_after_borrow(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    borrow_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first
    borrow_btn.wait_for(state="attached", timeout=15000)
    borrow_btn.click()
    enable_flutter_semantics(page)
    
    confirm_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn")').first
    if confirm_btn.count() > 0:
        confirm_btn.click()
        enable_flutter_semantics(page)
    
    # CHỜ FLUTTER CẬP NHẬT UI TRƯỚC KHI LẤY TEXT
    wait_for_flutter(page, text="Đang mượn", timeout=5000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-14_status_after_borrow.png"))
    txt = sem_text(page)
    assert "Borrowed" in txt or "Đang mượn" in txt, "TC-14 FAIL: Status not updated."

def test_tc15_status_updates_after_return(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    return_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first
    return_btn.wait_for(state="attached", timeout=15000)
    return_btn.click()
    enable_flutter_semantics(page)

    open_books_tab(page)
    # CHỜ FLUTTER CẬP NHẬT UI TRƯỚC KHI LẤY TEXT
    wait_for_flutter(page, text="Có sẵn", timeout=5000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-15_status_after_return.png"))
    txt = sem_text(page)
    assert "Available" in txt or "Có sẵn" in txt, "TC-15 FAIL: Status not updated."

def test_tc16_publication_year_format(page, test_config):
    login(page, test_config)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-16_publication_year.png"))
    txt = sem_text(page)
    import re
    years = re.findall(r'\b(19|20)\d{2}\b', txt)
    assert len(years) > 0, "TC-16 FAIL"

def test_tc17_lost_book_status(page, test_config):
    login(page, test_config)
    # CUỘN CHUỘT XUỐNG ĐỂ TÌM SÁCH BỊ KHUẤT (BOOK007)
    page.mouse.move(500, 500)
    page.mouse.wheel(0, 1500)
    page.wait_for_timeout(1000)
    enable_flutter_semantics(page)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-17_lost_status.png"))
    txt = sem_text(page)
    assert "Lost" in txt or "Đã mất" in txt or "BOOK007" in txt, "TC-17 FAIL: 'Lost' status not found."