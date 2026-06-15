"""
conftest.py — Shared fixtures and helpers for the Library Book Borrowing System test suite.
Target: https://stqa.rbc.vn  (Flutter Web / CanvasKit)
"""
import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from web_detector import detect_technology, WebTech

load_dotenv()

BASE_URL        = os.getenv("BASE_URL",          "https://stqa.rbc.vn")
TEST_EMAIL      = os.getenv("TEST_EMAIL",         "librarian@library.com")
TEST_PASSWORD   = os.getenv("TEST_PASSWORD",      "admin123")
TEST_DISPLAY_NAME = os.getenv("TEST_DISPLAY_NAME","Nguyễn Thủ Thư")
SCREENSHOT_DIR  = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Accounts used across test files
# ---------------------------------------------------------------------------
ACCOUNTS = {
    "librarian": {
        "email":    "librarian@library.com",
        "password": "admin123",
        "name":     "Nguyễn Thủ Thư",
        "role":     "Librarian",
    },
    "member_ba": {
        "email":    "ba.nguyen@email.com",
        "password": "password123",
        "name":     "Ba Nguyễn",
        "role":     "Member",
    },
    "member_dam": {
        "email":    "dam.tran@email.com",
        "password": "password123",
        "name":     "Dẫm Trần",
        "role":     "Member",
    },
    "member_biet": {
        "email":    "biet.hoang@email.com",
        "password": "password123",
        "name":     "Biết Hoàng",
        "role":     "Member",
    },
    "member_suspended": {
        "email":    "cu.le@email.com",
        "password": "password123",
        "name":     "Cũ Lê",
        "role":     "Member (Suspended)",
    },
    "member_expired": {
        "email":    "binh.pham@email.com",
        "password": "password123",
        "name":     "Bình Phạm",
        "role":     "Member (Expired)",
    },
}


# ---------------------------------------------------------------------------
# Flutter Semantics helpers
# ---------------------------------------------------------------------------

def wait_for_flutter(page, text=None, selector=None, timeout=10000):
    """Smart Wait: wait for Flutter Semantics Tree to update."""
    if text:
        page.locator(
            f'flt-semantics:has-text("{text}"), flt-semantics[aria-label*="{text}"]'
        ).first.wait_for(state="attached", timeout=timeout)
    elif selector:
        page.locator(selector).first.wait_for(state="attached", timeout=timeout)
    else:
        page.locator("flt-semantics").first.wait_for(state="attached", timeout=timeout)


def enable_flutter_semantics(page, timeout=15000):
    """Enable Flutter Semantics Tree for DOM interaction."""
    if page.locator("flt-semantics").count() > 0:
        return
    enable_btn = page.locator('flt-semantics-placeholder[role="button"]').first
    try:
        enable_btn.wait_for(state="attached", timeout=timeout)
        enable_btn.focus()
        enable_btn.dispatch_event("click")
    except Exception:
        page.keyboard.press("Tab")
        page.keyboard.press("Enter")
    page.locator("flt-semantics, input[aria-label], textarea[aria-label]").first.wait_for(
        state="attached", timeout=timeout
    )


def flutter_fill(page, label, value):
    """Fill a Flutter text field via semantics input."""
    field = page.locator(f'input[aria-label="{label}"]').first
    field.wait_for(state="attached", timeout=10000)
    field.click()
    active_input = page.locator("flt-text-editing-host input, flt-text-editing-host textarea")
    try:
        active_input.first.wait_for(state="attached", timeout=3000)
        active_input.first.fill(value)
    except Exception:
        field.fill(value)


def flutter_click_button(page, text):
    """Click a Flutter button via semantics element."""
    btn = page.locator(f'flt-semantics[role="button"]:has-text("{text}")')
    btn.click()


def sem_text(page):
    """Return all visible semantics text as a single string."""
    return " ".join(page.locator("flt-semantics").all_text_contents())


# ---------------------------------------------------------------------------
# Login helper
# ---------------------------------------------------------------------------

def login(page, test_config):
    """Log in and wait for the home page to fully load."""
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email",    test_config["email"])
    flutter_fill(page, "Mật khẩu", test_config["password"])
    flutter_click_button(page, "Đăng nhập")
    wait_for_flutter(page, text=test_config["display_name"], timeout=30000)
    enable_flutter_semantics(page)


def login_as(page, base_url, email, password, display_name=None):
    """Low-level login helper — waits for 'Đăng xuất' or a display_name."""
    page.goto(base_url, wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email",    email)
    flutter_fill(page, "Mật khẩu", password)
    flutter_click_button(page, "Đăng nhập")
    if display_name:
        wait_for_flutter(page, text=display_name, timeout=30000)
    else:
        wait_for_flutter(page, text="Đăng xuất", timeout=30000)
    enable_flutter_semantics(page)


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------

def open_books_tab(page):
    page.locator('flt-semantics[role="tab"][aria-label*="Sách"]').first.click()
    enable_flutter_semantics(page)


def open_borrow_return_tab(page):
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    enable_flutter_semantics(page)


def open_members_tab(page):
    page.locator('flt-semantics[role="tab"][aria-label="Thành viên"]').click()
    enable_flutter_semantics(page)


# ---------------------------------------------------------------------------
# pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser():
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=headless,
            args=["--force-renderer-accessibility"],
        )
        yield b
        b.close()


@pytest.fixture()
def page(browser):
    context = browser.new_context()
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture()
def test_config():
    """Provide test configuration from environment variables."""
    return {
        "base_url":     BASE_URL,
        "email":        TEST_EMAIL,
        "password":     TEST_PASSWORD,
        "display_name": TEST_DISPLAY_NAME,
        "screenshot_dir": SCREENSHOT_DIR,
    }


@pytest.fixture()
def web_tech(page) -> WebTech:
    page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
    page.locator("flt-glass-pane").wait_for(state="attached", timeout=15000)
    tech = detect_technology(page)
    return tech