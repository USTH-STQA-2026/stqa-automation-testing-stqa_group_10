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
    """Cuộn trang xuống dần để tìm book card.
    Flutter CanvasKit expose book code qua aria-label của group element,
    không phải text content trực tiếp — dùng aria-label selector.
    """
    # Thử tìm bằng aria-label trước (cách Flutter expose book code)
    for _ in range(5):
        card = page.locator(f'flt-semantics[aria-label*="{book_identifier}"]').first
        if card.count() > 0:
            return card
        # Fallback: tìm bằng has-text
        card = page.locator(f'flt-semantics:has-text("{book_identifier}")').first
        if card.count() > 0:
            return card
        page.mouse.move(500, 500)
        page.mouse.wheel(0, 800)
        page.wait_for_timeout(1000)
        enable_flutter_semantics(page)
    # Trả về locator aria-label sau khi đã scroll hết
    return page.locator(f'flt-semantics[aria-label*="{book_identifier}"]').first


def _borrow_book(page, book_identifier: str):
    """Tìm sách và thực hiện mượn. Gọi hàm này khi đã ở tab Sách."""
    card = _scroll_and_find_book(page, book_identifier)
    card.wait_for(state="attached", timeout=15000)

    borrow_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first
    borrow_btn.wait_for(state="attached", timeout=10000)
    borrow_btn.click()

    # Chờ dialog xác nhận xuất hiện
    wait_for_flutter(page, text="Xác nhận", timeout=10000)

    confirm_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn")').first
    confirm_btn.click()

    # Chờ thông báo thành công
    wait_for_flutter(page, text="thành công", timeout=10000)

def test_tc25_borrow_available_book(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_biet"]["email"], ACCOUNTS["member_biet"]["password"])
    open_books_tab(page)
    _borrow_book(page, "BOOK001")
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
    open_books_tab(page)
    borrow_btn = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first
    borrow_btn.wait_for(state="attached", timeout=15000)
    borrow_btn.click()
    enable_flutter_semantics(page)
    confirm = page.locator('flt-semantics[role="button"]:has-text("Mượn")').first
    if confirm.count() > 0:
        confirm.click()
        enable_flutter_semantics(page)
    page.wait_for_timeout(3000)
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
    # Chờ thông báo thành công trước khi chuyển tab
    wait_for_flutter(page, text="thành công", timeout=10000)
    page.wait_for_timeout(1500)

    open_books_tab(page)
    # Chờ danh sách sách render xong (chờ nút Mượn sách này xuất hiện)
    page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first.wait_for(
        state="attached", timeout=10000
    )
    page.wait_for_timeout(1000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-34_after_return.png"))

    # Status "Có sẵn"/"Available" có thể nằm trong aria-label của group node (không phải leaf)
    # Kiểm tra cả aria-label lẫn leaf text
    all_aria = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('flt-semantics[aria-label]'))
            .map(n => n.getAttribute('aria-label'))
            .join(' ');
    }""")
    txt = sem_text(page)
    combined = txt + " " + all_aria
    assert "Available" in combined or "Có sẵn" in combined, "TC-34 FAIL: Status not updated"

def test_tc35_no_duplicate_popup_on_rapid_return_clicks(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_borrow_return_tab(page)
    return_btn = page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first
    return_btn.wait_for(state="attached", timeout=15000)
    # Click nhanh 3 lần liên tiếp để kiểm tra hệ thống không xử lý trùng lặp
    return_btn.click()
    return_btn.click()
    return_btn.click()
    # Chờ Flutter settle hoàn toàn, rồi refresh semantics tree
    page.wait_for_timeout(4000)
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-35_no_duplicate_popup.png"))
    # sem_text() mới chỉ lấy leaf nodes — không bị lặp do DOM tích luỹ
    txt = sem_text(page)
    success_count = txt.lower().count("thành công")
    assert success_count <= 1, f"TC-35 FAIL: 'thành công' appeared {success_count} times (expected ≤ 1)"

@pytest.mark.xfail(reason="BUG-10: System does not show overdue warning")
def test_tc36_overdue_warning_visible_for_member(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-36_overdue_warning.png"))
    txt = sem_text(page)
    assert "quá hạn" in txt.lower() or "overdue" in txt.lower(), "TC-36 FAIL: Warning missing."