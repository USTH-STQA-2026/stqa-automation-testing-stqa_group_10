"""
test_borrow_return.py — Borrow & Return Tests (REQ-04, REQ-05)
"""
import os
import pytest
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    flutter_click_button,
    login_as,
    open_books_tab,
    open_borrow_return_tab,
    sem_text,
    ACCOUNTS,
    wait_for_flutter,
)

def _scroll_and_find_book(page, book_identifier: str):
    """Cuộn trang xuống dần để tìm book card do Flutter Canvas ẩn các phần tử ngoài màn hình"""
    for _ in range(3):
        card = page.locator(f'flt-semantics:has-text("{book_identifier}")').first
        if card.count() > 0:
            return card
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 800)
        page.wait_for_timeout(1000)
        enable_flutter_semantics(page)
    return page.locator(f'flt-semantics:has-text("{book_identifier}")').first

# Trong test_borrow_return.py
def _borrow_book(page, book_identifier: str):
    # Tăng thời gian chờ lên 15 giây
    card = page.locator(f'flt-semantics:has-text("{book_identifier}")').first
    card.wait_for(state="attached", timeout=15000) 
    
    borrow_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first
    borrow_btn.click()
    
    # CHỜ ĐỢI: Sau khi click, bắt buộc phải chờ UI cập nhật xong
    wait_for_flutter(page, text="Xác nhận", timeout=10000)
    
    confirm_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn")').first
    confirm_btn.click()
    
    # CHỜ ĐỢI: Sau khi xác nhận
    wait_for_flutter(page, text="thành công", timeout=10000)

def test_tc25_borrow_available_book(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_biet"]["email"], ACCOUNTS["member_biet"]["password"])
    _borrow_book(page, "BOOK001")
    wait_for_flutter(page, text="thành công", timeout=5000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-25_borrow_success.png"))
    txt = sem_text(page)
    assert "thành công" in txt.lower() or "Đang mượn" in txt, "TC-25 FAIL"

@pytest.mark.xfail(reason="BUG-08: System does not limit 3rd borrow attempt")
def test_tc26_borrow_rejected_at_limit(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    _borrow_book(page, "BOOK001")
    _borrow_book(page, "BOOK002")
    _borrow_book(page, "BOOK005") # 3rd attempt
    wait_for_flutter(page, text="giới hạn", timeout=5000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-26_borrow_limit_rejected.png"))
    txt = sem_text(page)
    assert "limit" in txt.lower() or "giới hạn" in txt.lower(), "TC-26 FAIL: Expected rejection."

@pytest.mark.xfail(reason="BUG-09: Suspended member shows wrong error message")
def test_tc27_borrow_suspended_member(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_suspended"]["email"], ACCOUNTS["member_suspended"]["password"])
    borrow_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first
    borrow_btn.click()
    enable_flutter_semantics(page)
    confirm = page.locator('flt-semantics[role="button"]:has-text("Mượn")').first
    if confirm.count() > 0:
        confirm.click()
        enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-27_suspended_member.png"))
    txt = sem_text(page)
    assert "suspended" in txt.lower() or "bị khóa" in txt.lower() or "tạm ngưng" in txt.lower(), "TC-27 FAIL"

def test_tc28_borrow_button_hidden_for_borrowed_book(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_dam"]["email"], ACCOUNTS["member_dam"]["password"])
    book_card = _scroll_and_find_book(page, "BOOK003")
    borrow_btn_in_card = page.locator('flt-semantics[aria-label*="BOOK003"] flt-semantics[role="button"]:has-text("Mượn sách này")')
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-28_borrowed_book_no_btn.png"))
    assert borrow_btn_in_card.count() == 0, "TC-28 FAIL: Borrow button visible for borrowed book."

def test_tc29_borrow_expired_member(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_expired"]["email"], ACCOUNTS["member_expired"]["password"])
    borrow_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first
    borrow_btn.click()
    enable_flutter_semantics(page)
    confirm = page.locator('flt-semantics[role="button"]:has-text("Mượn")').first
    if confirm.count() > 0:
        confirm.click()
        enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-29_expired_member.png"))
    txt = sem_text(page)
    assert "expired" in txt.lower() or "hết hạn" in txt.lower(), "TC-29 FAIL"

def test_tc30_borrow_button_hidden_for_lost_book(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    book_card = _scroll_and_find_book(page, "BOOK007")
    borrow_btn_in_card = page.locator('flt-semantics[aria-label*="BOOK007"] flt-semantics[role="button"]:has-text("Mượn sách này")')
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-30_lost_book_no_btn.png"))
    assert borrow_btn_in_card.count() == 0, "TC-30 FAIL"

def test_tc31_return_book_on_time(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    return_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first
    return_btn.wait_for(state="attached", timeout=15000)
    return_btn.click()
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-31_return_on_time.png"))
    txt = sem_text(page)
    assert "thành công" in txt.lower() or "Đã trả" in txt, "TC-31 FAIL"

def test_tc32_return_overdue_book(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_borrow_return_tab(page)
    check_btn = page.locator('flt-semantics[role="button"]:has-text("quá hạn")').first
    if check_btn.count() > 0:
        check_btn.click()
        enable_flutter_semantics(page)

    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    return_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first
    return_btn.wait_for(state="attached", timeout=15000)
    return_btn.click()
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-32_return_overdue.png"))
    txt = sem_text(page)
    assert "Đã trả" in txt or "Returned" in txt, "TC-32 FAIL"

def test_tc33_cannot_return_other_members_book(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-33_no_return_others_book.png"))
    assert page.locator('flt-semantics[aria-label*="BOOK013"]').count() == 0, "TC-33 FAIL"

def test_tc34_book_status_immediate_after_return(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    return_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first
    return_btn.wait_for(state="attached", timeout=15000)
    return_btn.click()
    enable_flutter_semantics(page)
    
    open_books_tab(page)
    wait_for_flutter(page, text="Có sẵn", timeout=10000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-34_after_return.png"))
    txt = sem_text(page)
    assert "Available" in txt or "Có sẵn" in txt, "TC-34 FAIL: Status not updated"

def test_tc35_no_duplicate_popup_on_rapid_return_clicks(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_borrow_return_tab(page)
    return_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first
    return_btn.wait_for(state="attached", timeout=15000)
    for _ in range(3): return_btn.click()
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-35_no_duplicate_popup.png"))
    txt = sem_text(page)
    assert txt.count("thành công") <= 1, "TC-35 FAIL"

@pytest.mark.xfail(reason="BUG-10: System does not show overdue warning")
def test_tc36_overdue_warning_visible_for_member(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-36_overdue_warning.png"))
    txt = sem_text(page)
    assert "quá hạn" in txt.lower() or "overdue" in txt.lower(), "TC-36 FAIL: Warning missing."