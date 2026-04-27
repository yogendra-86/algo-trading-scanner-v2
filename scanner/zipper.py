from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def zip_csv_files(source_dir: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zipf:
        for csv_file in sorted(source_dir.glob("*.csv")):
            zipf.write(csv_file, arcname=csv_file.name)

    return zip_path