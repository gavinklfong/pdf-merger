import re
from calendar import month_name, month_abbr

def extract_year_month(filename):
    text = filename.lower()

    # Build month lookup
    month_lookup = {
        name.lower(): i for i, name in enumerate(month_name) if name
    }
    month_lookup.update({
        abbr.lower(): i for i, abbr in enumerate(month_abbr) if abbr
    })

    # Sort keys longest-first to avoid substring collisions
    month_keys = sorted(month_lookup.keys(), key=len, reverse=True)
    month_words = "|".join(re.escape(m) for m in month_keys)

    # 1. Glued format: March2021
    glued_regex = rf"({month_words})(19|20)\d{{2}}"
    glued = re.search(glued_regex, text)
    if glued:
        month = month_lookup[glued.group(1)]
        year = int(glued.group(2) + text[glued.end(2):glued.end(2)+2])
        return year, month

    # 2. Extract year
    year_match = re.search(r"(19|20)\d{2}", text)
    year = int(year_match.group()) if year_match else None

    # 3. Month name with custom boundaries
    name_regex = rf"(?<![A-Za-z])({month_words})(?![A-Za-z])"
    name_match = re.search(name_regex, text)
    if name_match:
        month = month_lookup[name_match.group()]
        return year, month

    # 4. Numeric month (fix for underscores)
    num_match = re.search(r"(?<!\d)(0?[1-9]|1[0-2])(?!\d)", text)
    if num_match:
        return year, int(num_match.group())

    # 5. No month found
    return year, None


def sort_files_by_date(filenames, ascending=True):
    def sort_key(name):
        year, month = extract_year_month(name)

        # Treat any file with a year OR a month as "dated"
        if year is not None or month is not None:
            y = year if year is not None else 0   # missing year → 0
            m = month if month is not None else 0 # missing month → 0

            if ascending:
                return (0, y, m, name)
            else:
                return (0, -y, -m, name)
        else:
            # Truly undated files: alphabetical, after dated ones
            if ascending:
                return (1, name)
            else:
                return (1, tuple(-ord(c) for c in name))

    return sorted(filenames, key=sort_key)
