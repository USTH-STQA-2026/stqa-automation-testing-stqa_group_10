"""
test_login.py — Login Tests (REQ-01)
"""
import os
import pytest
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    flutter_click_button,
    flutter_fill,
    wait_for_flutter,
    sem_text,
)

def test_tc01_login_success_valid_credentials(page, test_config):
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email",    "librarian@library.com")
    flutter_fill(page, "Mật khẩu", "admin123")
    flutter_click_button(page, "Đăng nhập")
    wait_for_flutter(page, text=test_config["display_name"], timeout=30000)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-01_login_success.png"))
    txt = sem_text(page)
    assert test_config["display_name"] in txt or "Đăng xuất" in txt, "TC-01 FAIL"

@pytest.mark.parametrize(
    "email, password, expected_msg, screenshot",
    [
        ("", "", "Please enter email and password", "TC-02_blank_both.png"),
        ("librarian@library.com", "", "Please enter email and password", "TC-03_blank_password.png"),
    ],
    ids=["TC-02", "TC-03"],
)
def test_tc02_tc03_blank_fields(page, test_config, email, password, expected_msg, screenshot):
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    if email: flutter_fill(page, "Email", email)
    if password: flutter_fill(page, "Mật khẩu", password)
    flutter_click_button(page, "Đăng nhập")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, screenshot))
    txt = sem_text(page)
    assert expected_msg in txt or "Đăng nhập" in txt, "TC-02/03 FAIL"

def test_tc04_wrong_password(page, test_config):
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email",    "librarian@library.com")
    flutter_fill(page, "Mật khẩu", "hehe")
    flutter_click_button(page, "Đăng nhập")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-04_wrong_password.png"))
    txt = sem_text(page)
    assert "Incorrect password" in txt or "Đăng nhập" in txt, "TC-04 FAIL"

@pytest.mark.xfail(reason="System does not normalize capitalized email")
def test_tc05_email_capitalised(page, test_config):
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email",    "Librarian@library.com")
    flutter_fill(page, "Mật khẩu", "admin123")
    flutter_click_button(page, "Đăng nhập")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-05_email_capitalised.png"))
    txt = sem_text(page)
    assert test_config["display_name"] in txt or "Đăng xuất" in txt, "TC-05 FAIL: Login rejected."

def test_tc06_password_masked(page, test_config):
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Mật khẩu", "admin123")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-06_password_masked.png"))
    pwd_input = page.locator('input[aria-label="Mật khẩu"]').first
    assert pwd_input.get_attribute("type") == "password", "TC-06 FAIL"

@pytest.mark.xfail(reason="BUG-01: System shows 'Can not find member' instead of format error")
@pytest.mark.parametrize(
    "email, password, screenshot",
    [
        ("librarianlibrarycom", "anypass",  "TC-07_invalid_email_no_at_no_dot.png"),
        ("librarianlibrary.com", "admin123", "TC-08_invalid_email_no_at.png"),
        ("librarian@librarycom", "admin123", "TC-09_invalid_email_no_dot.png"),
    ],
    ids=["TC-07", "TC-08", "TC-09"],
)
def test_tc07_tc08_tc09_invalid_email_format(page, test_config, email, password, screenshot):
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email",    email)
    flutter_fill(page, "Mật khẩu", password)
    flutter_click_button(page, "Đăng nhập")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, screenshot))
    txt = sem_text(page)
    assert "Email or password is invalid" in txt or "Email is invalid" in txt, "TC-07/08/09 FAIL: Format error missing."