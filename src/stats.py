import multiprocessing

from pathlib import Path

from starplot import Star
from starplot.data import Catalog

COMBINED_PATH = Path("/Volumes/Blue2TB/build/gdr3/")


mag_min = 6
mag_max = 18


def calc(partition_name):
    # for partition_name in partition_path_names:
    print(partition_name)

    total_stars = 0
    total_stars_mag_under_threshold = 0
    total_stars_mag_over_threshold = 0

    pq_path = COMBINED_PATH / partition_name / "stars.parquet"
    partition_catalog = Catalog(path=pq_path)

    all_stars = Star.all(catalog=partition_catalog)

    for star in all_stars:
        total_stars += 1

        if star.magnitude < mag_min:
            total_stars_mag_under_threshold += 1

        if star.magnitude > mag_max:
            total_stars_mag_over_threshold += 1

    print(f"total_stars = {total_stars:,}")
    print(f"total_stars_mag_under_threshold = {total_stars_mag_under_threshold:,}")
    print(f"total_stars_mag_over_threshold = {total_stars_mag_over_threshold:,}")

    return total_stars, total_stars_mag_under_threshold, total_stars_mag_over_threshold


if __name__ == "__main__":
    partition_path_names = sorted(
        [item.name for item in COMBINED_PATH.iterdir() if item.is_dir()]
    )

    with multiprocessing.Pool(processes=12) as pool:
        results = pool.map(calc, partition_path_names)

    total_stars = 0
    total_stars_mag_under_threshold = 0
    total_stars_mag_over_threshold = 0

    for total, total_under, total_over in results:
        total_stars += total
        total_stars_mag_under_threshold += total_under
        total_stars_mag_over_threshold += total_over

    print(f"total_stars = {total_stars:,}")
    print(f"total_stars_mag_under_threshold = {total_stars_mag_under_threshold:,}")
    print(f"total_stars_mag_over_threshold = {total_stars_mag_over_threshold:,}")
