"""
test_borrow_receipt.py — Borrow Receipt Lookup Tests (REQ-08)
Covers TC-49 and TC-50.
"""
import os
from conftest import (
    SCREENSHOT_DIR,
    enable_flutter_semantics,
    login,
    login_as,
    open_borrow_return_tab,  # FIX: Import thêm hàm chuyên mở tab mượn trả
    sem_text,
    ACCOUNTS,
)

def test_tc49_librarian_receipt_lookup(page, test_config):
    """TC-49 — Librarian checks full transaction/receipt history list."""
    login(page, test_config)
    
    # FIX: Dùng hàm mở Tab mượn trả thay vì click nút bằng text thủ công
    open_borrow_return_tab(page)
    
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-49_librarian_receipts.png"))
    
    txt = sem_text(page)
    assert len(txt) > 0, "TC-49 FAIL: No borrow receipts displayed for Librarian."

def test_tc50_member_receipt_lookup(page, test_config):
    """TC-50 — Normal member checks their personal borrow receipt list."""
    login_as(page, test_config["base_url"], ACCOUNTS["member_ba"]["email"], ACCOUNTS["member_ba"]["password"])
    
    # FIX: Dùng hàm mở Tab mượn trả
    open_borrow_return_tab(page)
    
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "TC-50_member_receipts.png"))
    
    txt = sem_text(page)
    assert len(txt) > 0, "TC-50 FAIL: No borrow receipts displayed for Member."