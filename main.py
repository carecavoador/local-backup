import filecmp
import shutil
import tomllib
from pathlib import Path

import click

CONFIG = tomllib.load(Path("config.toml").open("rb"))
ORIGEM = Path(CONFIG["origem"])
DESTINO = Path(CONFIG["destino"])


def copy_new_files(src: Path, dst: Path) -> None | list[Path]:
    failed: list[Path] = []

    comparacao = filecmp.dircmp(src, dst)
    # Files
    with click.progressbar(
        comparacao.left_only,
        label=f"{src.as_posix()}",
    ) as all_files:
        for diff_filename in all_files:
            new_file = src.joinpath(diff_filename)
            if new_file.is_file():
                shutil.copy2(src=new_file, dst=dst.joinpath(diff_filename))
            else:
                new_directory = dst.joinpath(diff_filename)
                if not new_directory.exists():
                    new_directory.mkdir()
                    copy_new_files(src=src.joinpath(diff_filename), dst=new_directory)

    # Directories
    for directory in comparacao.common_dirs:
        copy_new_files(src=src.joinpath(directory), dst=dst.joinpath(directory))

    # Funny files
    if comparacao.funny_files:
        failed.extend(failed)
    else:
        return None

    return failed


def main() -> None:
    errors = copy_new_files(src=ORIGEM, dst=DESTINO)
    if errors:
        print(errors)


if __name__ == "__main__":
    main()
