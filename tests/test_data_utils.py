from __future__ import annotations
from dev_qol_toolkit import data_utils

def test_case_conversions():
    assert data_utils.to_snake("SpamEggs") == "spam_eggs"
    assert data_utils.to_camel("spam_eggs") == "spamEggs"