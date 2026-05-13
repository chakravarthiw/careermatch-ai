# tests/test_learner.py
# ─────────────────────────────────────────────────────────────
# Tests for src/learner.py
#
# These tests check the memory layer:
# - title correction memory
# - company memory
# - known company lookup
# - correction statistics
#
# The tests temporarily override memory file paths so real user
# data in data/ is not touched.
# ─────────────────────────────────────────────────────────────

import json
from pathlib import Path

import src.learner as learner


def test_record_company_creates_memory_file(tmp_path):
    test_file = tmp_path / "company_memory.json"
    learner.COMPANY_MEMORY_PATH = str(test_file)

    learner.record_company(
        confirmed_company="Tennis Australia",
        detected_company=""
    )

    assert test_file.exists()

    data = json.loads(test_file.read_text())
    assert len(data) == 1
    assert data[0]["company"] == "Tennis Australia"


def test_record_company_avoids_duplicates(tmp_path):
    test_file = tmp_path / "company_memory.json"
    learner.COMPANY_MEMORY_PATH = str(test_file)

    learner.record_company("Tennis Australia", "")
    learner.record_company("tennis australia", "")

    data = json.loads(test_file.read_text())

    assert len(data) == 1


def test_get_known_companies_returns_list(tmp_path):
    test_file = tmp_path / "company_memory.json"
    learner.COMPANY_MEMORY_PATH = str(test_file)

    test_file.write_text(json.dumps([
        {"company": "RMIT University"},
        {"company": "Monash University"}
    ]))

    companies = learner.get_known_companies()

    assert companies == ["RMIT University", "Monash University"]


def test_record_correction_creates_title_memory(tmp_path):
    test_file = tmp_path / "title_memory.json"
    learner.TITLE_MEMORY_PATH = str(test_file)

    learner.record_correction(
        confirmed_title="Data Analyst",
        detected_title="Data Analyst",
        first_line="Data Analyst",
        second_line="Full-time"
    )

    assert test_file.exists()

    data = json.loads(test_file.read_text())
    assert len(data) == 1
    assert data[0]["confirmed_title"] == "Data Analyst"
    assert data[0]["was_corrected"] is False


def test_record_correction_detects_correction(tmp_path):
    test_file = tmp_path / "title_memory.json"
    learner.TITLE_MEMORY_PATH = str(test_file)

    learner.record_correction(
        confirmed_title="Event Coordinator",
        detected_title="Event Assistant",
        first_line="Event Assistant",
        second_line="Melbourne"
    )

    data = json.loads(test_file.read_text())

    assert data[0]["was_corrected"] is True


def test_correction_status_returns_summary(tmp_path):
    title_file = tmp_path / "title_memory.json"
    company_file = tmp_path / "company_memory.json"

    learner.TITLE_MEMORY_PATH = str(title_file)
    learner.COMPANY_MEMORY_PATH = str(company_file)

    learner.record_correction(
        confirmed_title="Data Analyst",
        detected_title="Data Analyst",
        first_line="Data Analyst"
    )

    learner.record_company(
        confirmed_company="RMIT University",
        detected_company=""
    )

    stats = learner.correction_status()

    assert stats["title_entries"] == 1
    assert stats["known_companies"] == 1
    assert "phase" in stats
