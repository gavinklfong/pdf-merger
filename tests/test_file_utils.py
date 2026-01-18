import pytest

from file_utils import extract_year_month, sort_files_by_date


# -----------------------------
# Tests for extract_year_month()
# -----------------------------

def test_extract_full_month_name():
    assert extract_year_month("report_March_2021.pdf") == (2021, 3)

def test_extract_full_month_name_no_space_1():
    assert extract_year_month("report_March2021.pdf") == (2021, 3)

def test_extract_full_month_name_no_space_2():
    assert extract_year_month("report_2021March.pdf") == (2021, 3)

def test_extract_full_month_name_range_1():
    assert extract_year_month("report_2021January-March.pdf") == (2021, 1)

def test_extract_full_month_name_range_2():
    assert extract_year_month("report_2021March-July.pdf") == (2021, 3)

def test_extract_abbreviated_month():
    assert extract_year_month("summary_Feb_2020.txt") == (2020, 2)

def test_extract_abbreviated_month_no_space_1():
    assert extract_year_month("summary_Feb2020.txt") == (2020, 2)

def test_extract_abbreviated_month_no_space_2():
    assert extract_year_month("summary_Feb2020.txt") == (2020, 2)

def test_extract_abbreviated_month_range_1():
    assert extract_year_month("summary_2020-Jan-Dec.txt") == (2020, 1)

def test_extract_abbreviated_month_range_2():
    assert extract_year_month("summary_2020-Mar-Dec.txt") == (2020, 3)

def test_extract_abbreviated_month_range_3():
    assert extract_year_month("summary_2020Mar-Dec.txt") == (2020, 3)

def test_extract_numeric_month():
    assert extract_year_month("data_2021_07.csv") == (2021, 7)

def test_extract_numeric_month_single_digit():
    assert extract_year_month("notes_2018_7.txt") == (2018, 7)

def test_extract_year_only():
    assert extract_year_month("archive_2022_backup.zip") == (2022, None)

def test_extract_month_only():
    assert extract_year_month("meeting_Jan.doc") == (None, 1)

def test_extract_no_date():
    assert extract_year_month("randomfile.txt") == (None, None)


# -----------------------------
# Tests for sort_files_by_date()
# -----------------------------

def test_sort_ascending_basic():
    files = [
        "report_2021_Jan.pdf",
        "summary_2020_12.xlsx",
        "invoice_March_2019.docx",
    ]
    expected = [
        "invoice_March_2019.docx",
        "summary_2020_12.xlsx",
        "report_2021_Jan.pdf",
    ]
    assert sort_files_by_date(files, ascending=True) == expected


def test_sort_descending_basic():
    files = [
        "report_2021_Jan.pdf",
        "summary_2020_12.xlsx",
        "invoice_March_2019.docx",
    ]
    expected = [
        "report_2021_Jan.pdf",
        "summary_2020_12.xlsx",
        "invoice_March_2019.docx",
    ]
    assert sort_files_by_date(files, ascending=False) == expected


def test_sort_with_undated_files_alphabetical():
    files = [
        "zeta.doc",
        "alpha.doc",
        "report_2021_Jan.pdf",
    ]
    expected = [
        "report_2021_Jan.pdf",
        "alpha.doc",
        "zeta.doc",
    ]
    assert sort_files_by_date(files) == expected


def test_sort_undated_files_descending():
    files = [
        "zeta.doc",
        "alpha.doc",
        "report_2021_Jan.pdf",
    ]
    expected = [
        "report_2021_Jan.pdf",
        "zeta.doc",
        "alpha.doc",
    ]
    assert sort_files_by_date(files, ascending=False) == expected


def test_sort_mixed_formats():
    files = [
        "file_2021_1.txt",
        "file_Jan_2021.txt",
        "file_2021_January.txt",
    ]
    expected = [
        "file_2021_1.txt",
        "file_2021_January.txt",
        "file_Jan_2021.txt",
    ]
    assert sort_files_by_date(files) == expected



def test_sort_same_year_month_tiebreaker():
    files = [
        "b_2021_Jan.txt",
        "a_2021_Jan.txt",
    ]
    expected = [
        "a_2021_Jan.txt",
        "b_2021_Jan.txt",
    ]
    assert sort_files_by_date(files) == expected


def test_sort_missing_month_but_has_year():
    files = [
        "file_2021.txt",
        "file_2020.txt",
        "file_2022.txt",
    ]
    expected = [
        "file_2020.txt",
        "file_2021.txt",
        "file_2022.txt",
    ]
    assert sort_files_by_date(files) == expected


def test_sort_missing_year_but_has_month():
    files = [
        "file_Jan.txt",
        "file_March.txt",
        "file_Feb.txt",
    ]
    expected = [
        "file_Jan.txt",
        "file_Feb.txt",
        "file_March.txt",
    ]
    assert sort_files_by_date(files) == expected


def test_sort_all_undated_files():
    files = ["z.txt", "b.txt", "a.txt"]
    expected = ["a.txt", "b.txt", "z.txt"]
    assert sort_files_by_date(files) == expected


def test_sort_all_undated_files_descending():
    files = ["z.txt", "b.txt", "a.txt"]
    expected = ["z.txt", "b.txt", "a.txt"]
    assert sort_files_by_date(files, ascending=False) == expected
