"""Python script to fetch NASA Earth science data from Earthdata."""

import argparse
import os
from calendar import monthrange
from datetime import datetime, timedelta

os.system("conda install -c conda-forge earthaccess -y")

import earthaccess

# ---------------------------
# Argument parser
# ---------------------------
parser = argparse.ArgumentParser()

parser.add_argument("--short_name", type=str, required=True)

parser.add_argument("--lat_min", type=float, required=True)
parser.add_argument("--lat_max", type=float, required=True)
parser.add_argument("--lon_min", type=float, required=True)
parser.add_argument("--lon_max", type=float, required=True)

parser.add_argument("--start_date", type=str, required=True)
parser.add_argument("--end_date", type=str, required=True)

parser.add_argument(
    "--exclude_dates",
    type=str,
    required=False,
    default="",
    help="Comma-separated dates to exclude (YYYY-MM-DD)"
)

parser.add_argument(
    "--exclude_ranges",
    type=str,
    default="",
    help="Comma-separated date ranges (YYYY-MM-DD:YYYY-MM-DD)"
)

parser.add_argument(
    "--resolution",
    choices=["daily", "monthly"],
    help="Increment dates daily or monthly")

parser.add_argument("--out_file", type=str, required=True)

ARGS = parser.parse_args()

os.environ["EARTHDATA_USERNAME"] = ""
os.environ["EARTHDATA_PASSWORD"] = ""

# ---------------------------
# Login
# ---------------------------
earthaccess.login(strategy="environment", persist=True)


def increment(current, step):
    """
    Increment a datetime object by one step based on the specified temporal \
    resolution.

    Parameters
    ----------
    current : datetime
        The current datetime to increment.
    step : str
        The step type. Supported values:
        - "month": advances to the first day of the next month
        - "day": advances by one day

    Returns
    -------
    datetime
        A new datetime object incremented according to the specified step.

    Notes
    -----
    - For monthly increments, the returned date is always normalized to the
      first day of the next month to avoid invalid dates (e.g., transitioning
      from January 31 to February).
    - For daily increments, a standard timedelta of one day is applied.
    """
    if step == "month":
        year = current.year + (current.month // 12)
        month = (current.month % 12) + 1
        return datetime(year, month, 1)  # ALWAYS safe
    else:
        return current + timedelta(days=1)


# ---------------------------
# Parse & Prepare excluded dates
# ---------------------------
RESOLUTION = ARGS.resolution

if RESOLUTION == "monthly":
    DATE_FORMAT = "%Y-%m"
    STEP = "month"
else:
    DATE_FORMAT = "%Y-%m-%d"
    STEP = "day"

excluded = set()

if ARGS.exclude_dates:
    for d in ARGS.exclude_dates.split(","):
        d = d.strip()
        dt = datetime.strptime(d, DATE_FORMAT)
        excluded.add(dt.strftime(DATE_FORMAT))

for label, value in [("start_date", ARGS.start_date),
                     ("end_date", ARGS.end_date)]:
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValueError(
            f"Invalid {label} for {RESOLUTION}: expected {DATE_FORMAT}"
        )

start = datetime.strptime(ARGS.start_date, DATE_FORMAT)
end = datetime.strptime(ARGS.end_date, DATE_FORMAT)

if start > end:
    raise ValueError(
        "start_date must be earlier than or equal to end_date"
    )


if STEP == "month":
    start = start.replace(day=1)
    end = end.replace(day=1)

# ---------------------------
# Parse excluded ranges
# format: YYYY-MM-DD:YYYY-MM-DD
#         YYYY-MM:YYYY-MM
# ---------------------------
if ARGS.exclude_ranges:
    for r in ARGS.exclude_ranges.split(","):
        if ":" in r:
            start_r, end_r = r.split(":")
            start_r = datetime.strptime(start_r.strip(), DATE_FORMAT)
            end_r = datetime.strptime(end_r.strip(), DATE_FORMAT)

            current = start_r
            while current <= end_r:
                excluded.add(current.strftime(DATE_FORMAT))
                current = increment(current, STEP)

# ---------------------------
# Prepare output path
# ---------------------------

DOWNLOAD_PATH = os.path.join(os.getcwd(), "Data")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

all_files = []

# ---------------------------
# MONTHLY logic
# ---------------------------
if RESOLUTION == "monthly":
    current = start

    while current <= end:
        month_str = current.strftime("%Y-%m")

        if month_str not in excluded:
            year, mon = current.year, current.month
            last_day = monthrange(year, mon)[1]

            start_date = f"{month_str}-01"
            end_date = f"{month_str}-{last_day:02d}"

            results = earthaccess.search_data(
                short_name=ARGS.short_name,
                temporal=(start_date, end_date),
                bounding_box=(
                    ARGS.lon_min, ARGS.lat_min,
                    ARGS.lon_max, ARGS.lat_max)
            )

            if results:
                try:
                    files = earthaccess.download(results, DOWNLOAD_PATH)
                    if files:
                        all_files.extend(files)

                except Exception as e:
                    print(f"Download failed: {e}")

        # increment month
        current = increment(current, STEP)

# ---------------------------
# DAILY logic
# ---------------------------
else:
    current = start

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        if date_str not in excluded:
            results = earthaccess.search_data(
                short_name=ARGS.short_name,
                temporal=(date_str, date_str),
                bounding_box=(
                    ARGS.lon_min, ARGS.lat_min,
                    ARGS.lon_max, ARGS.lat_max)
            )

            if results:
                try:
                    files = earthaccess.download(results, DOWNLOAD_PATH)
                    if files:
                        all_files.extend(files)

                except Exception as e:
                    print(f"Download failed: {e}")

        current = increment(current, STEP)

# ---------------------------
# Output
# ---------------------------
with open(ARGS.out_file, "w") as f:
    if all_files:
        for file in all_files:
            f.write(f"{os.path.abspath(file)}\n")
    else:
        f.write("No files downloaded\n")

print(f"Using temporal resolution: {RESOLUTION}")
