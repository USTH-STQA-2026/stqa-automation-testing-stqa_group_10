"""
test_admin_features.py — Admin & Lookup Tests (REQ-06, REQ-07, REQ-08)
"""
import os
import pytest
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    flutter_click_button,
    flutter_fill,
    login_as,
    open_borrow_return_tab,
    open_members_tab,
    sem_text,
    ACCOUNTS,
)

def _open_add_member_form(page):
    page.locator('flt-semantics[role="button"]:has-text("Thêm thành viên")').first.click()
    enable_flutter_semantics(page)

def _fill_member_form(page, full_name: str, email: str, phone: str):
    flutter_fill(page, "Họ và tên", full_name)
    flutter_fill(page, "Email", email)
    flutter_fill(page, "Số điện thoại", phone)

def test_tc37_librarian_triggers_overdue_check(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_borrow_return_tab(page)
    check_btn = page.locator('flt-semantics[role="button"]:has-text("quá hạn")').first
    if check_btn.count() > 0: check_btn.click()
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-37_overdue_check.png"))
    txt = sem_text(page)
    assert "quá hạn" in txt.lower() or "updated" in txt.lower(), "TC-37 FAIL"

def test_tc38_member_sees_overdue_receipts(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-38_member_overdue_status.png"))
    txt = sem_text(page)
    assert "quá hạn" in txt.lower() or "đã trả" in txt.lower(), "TC-38 FAIL"

@pytest.mark.xfail(reason="BUG-03: System rejects valid email")
def test_tc39_librarian_adds_valid_member(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    _open_add_member_form(page)
    _fill_member_form(page, "Ngô Chấn Hiệp", "ngohiep010605@gmail.com", "0123456789")
    flutter_click_button(page, "Thêm thành viên")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-39_add_member_success.png"))
    txt = sem_text(page)
    assert "thành công" in txt.lower() or "MEM" in txt, "TC-39 FAIL: Member not added."

def test_tc40_member_cannot_see_add_member_button(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_dam"]["email"], ACCOUNTS["member_dam"]["password"])
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-40_no_add_member_btn.png"))
    assert page.locator('flt-semantics[role="tab"][aria-label="Thành viên"]').count() == 0, "TC-40 FAIL"

@pytest.mark.xfail(reason="BUG-04: System shows incorrect blank field error message")
def test_tc41_add_member_blank_fields(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    _open_add_member_form(page)
    flutter_click_button(page, "Thêm thành viên")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-41_blank_fields_error.png"))
    txt = sem_text(page)
    assert "bắt buộc" in txt.lower() or "required" in txt.lower(), "TC-41 FAIL: Expected standard blank errors."

@pytest.mark.xfail(reason="BUG-02: System accepts email missing dot")
def test_tc42_add_member_email_missing_dot(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    _open_add_member_form(page)
    _fill_member_form(page, "ngo chan hiep", "ghiep342@gmailcom", "0123456789")
    flutter_click_button(page, "Thêm thành viên")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-42_email_missing_dot.png"))
    txt = sem_text(page)
    assert "invalid" in txt.lower() or "không hợp lệ" in txt.lower(), "TC-42 FAIL: System accepted invalid email."

@pytest.mark.xfail(reason="BUG-XX: Error message is incorrect")
def test_tc43_add_member_email_missing_at(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    _open_add_member_form(page)
    _fill_member_form(page, "toi ten la tao", "ghiep242.com", "0941898905")
    flutter_click_button(page, "Thêm thành viên")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-43_email_missing_at.png"))
    txt = sem_text(page)
    assert "invalid" in txt.lower() or "không hợp lệ" in txt.lower(), "TC-43 FAIL"

@pytest.mark.xfail(reason="BUG-03: System shows invalid format instead of duplicate error")
def test_tc44_add_member_duplicate_email(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    _open_add_member_form(page)
    _fill_member_form(page, "Ngô Chấn Hiệp", "dam.tran@email.com", "0941898905")
    flutter_click_button(page, "Thêm thành viên")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-44_duplicate_email.png"))
    txt = sem_text(page)
    assert "already exists" in txt.lower() or "đã tồn tại" in txt.lower(), "TC-44 FAIL: Expected duplicate error."

def test_tc45_librarian_views_member_list(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-45_member_list.png"))
    txt = sem_text(page)
    assert "MEM" in txt or "@" in txt, "TC-45 FAIL"

def test_tc46_librarian_views_all_receipts(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_borrow_return_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-46_librarian_receipts.png"))
    txt = sem_text(page)
    assert "Ngày mượn" in txt or "Hạn trả" in txt, "TC-46 FAIL"

def test_tc47_member_views_own_receipts(page, test_config):
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    open_borrow_return_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-47_member_receipts.png"))
    txt = sem_text(page)
    assert "Ngày mượn" in txt or "BR" in txt, "TC-47 FAIL"

def test_tc48_list_members_info(page, test_config):
    login_as(page, test_config["base_url"], "librarian@library.com", "admin123")
    open_members_tab(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-48_member_list.png"))
    txt = sem_text(page)
    assert len(txt) > 0, "TC-48 FAIL"