"""
test_general.py — General / Cross-cutting Tests
Covers logout (TC-11 from original numbering) and language switch.

These tests apply after a successful login and verify global UI behaviours.
"""
import os
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    login,
    sem_text,
)


def test_logout(page, test_config):
    """Logout — clicking 'Đăng xuất' returns to the login screen.

    Expected: Email input and 'Đăng nhập' button are visible after logout.
    """
    login(page, test_config)
    enable_flutter_semantics(page)

    page.locator('flt-semantics[role="button"]:has-text("Đăng xuất")').click()
    page.locator('input[aria-label="Email"]').wait_for(state="attached", timeout=15000)
    page.locator('flt-semantics[role="button"]:has-text("Đăng nhập")').wait_for(
        state="attached", timeout=15000
    )
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "logout.png"))

    txt = sem_text(page)
    assert "Đăng nhập" in txt or "Email" in txt or "Mật khẩu" in txt, (
        "Logout FAIL: Did not return to login page."
    )


def test_switch_language_to_english(page, test_config):
    """Language switch — clicking 'EN' switches the UI to English.

    Expected: English labels (Logout, Borrow, Search, Library, Members) appear.
    """
    login(page, test_config)
    enable_flutter_semantics(page)

    page.locator('flt-semantics[role="button"]:has-text("EN")').click()
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "switch_language_en.png"))

    txt = sem_text(page)
    english_markers = ["Logout", "Borrow", "Search", "Library", "Members"]
    assert any(marker in txt for marker in english_markers), (
        f"Language switch FAIL: UI did not switch to English. Actual: {txt[:300]}"
    )