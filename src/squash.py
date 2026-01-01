import multiprocessing
from pathlib import Path

import click
import pyarrow.parquet as pq

import settings

"""Squashes parquet files in each healpix partition into a single file, to optimize queries."""


def squash_partition(partition_name: str, source_path: Path, destination_path: Path):
    print(partition_name)
    source_filenames = Path(source_path / partition_name).glob("*.parquet")
    source_filenames = sorted([str(f) for f in source_filenames])
    dataset = pq.ParquetDataset(source_filenames, schema=settings.SCHEMA)
    table = dataset.read()

    if "__index_level_0__" in table.column_names:
        table = table.drop_columns("__index_level_0__")

    sorting_columns = ["magnitude"]
    table = table.sort_by([(c, "ascending") for c in sorting_columns])
    sort_columns = [
        pq.SortingColumn(table.column_names.index(c)) for c in sorting_columns
    ]

    outfile_path = destination_path / partition_name
    outfile_path.mkdir(parents=True, exist_ok=True)

    pq.write_table(
        table,
        outfile_path / "stars.parquet",
        compression="snappy",
        row_group_size=100_000,
        sorting_columns=sort_columns,
    )


@click.command()
@click.option("--source", help="Source path of catalog data")
@click.option("--destination", help="Destination path")
@click.option("--num_workers", default=10, help="Number of workers to run")
def main(source, destination, num_workers):
    source_path = Path(source)
    destination_path = Path(destination)
    partition_names = sorted(
        [item.name for item in source_path.iterdir() if item.is_dir()]
    )

    process_args = [
        (partition_name, source_path, destination_path)
        for partition_name in partition_names
    ]

    with multiprocessing.Pool(processes=num_workers) as pool:
        pool.starmap(squash_partition, process_args)


if __name__ == "__main__":
    main()
