import json
import os
import shutil
import warnings
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def pushd(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield Path(path)
    finally:
        os.chdir(cwd)


class WarningMessageEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, warnings.WarningMessage):
            return {
                k: v
                for k, v in obj.__dict__.items()
                if v is not None and not k.startswith("_")
            }

        if isinstance(obj, type):
            return obj.__name__

        if isinstance(obj, Exception):
            return str(obj).strip().split("\n")

        return super().default(obj)


def main() -> int:
    """
    Create a static html documentation for the project in the 'public' directory.

    Requires follwing PyPi packages:
    - 'pdoc'
    - 'pathlibutil'

    Returns non-zero on failure.
    """

    try:
        from pdoc import pdoc, render

        with pushd(Path(__file__).parent) as cwd:
            print(f"\nrunning docs in {cwd=}...")

            documentation = cwd / "public"

            try:
                print("cleaning output directory.")
                shutil.rmtree(documentation)
            except FileNotFoundError:
                pass

            documentation.mkdir(parents=True)

            config = {
                "template_directory": cwd / "dark-mode",
                "show_source": False,
                "search": False,
            }

            modules = [
                "jinja2_pdoc",
                "pdoc",
                "jinja2",
            ]

            with warnings.catch_warnings(record=True) as messages:
                print(f"rendering {modules=}.")

                render.configure(**config)
                pdoc(*modules, output_directory=documentation)

                log = documentation / "warnings.json"

                with log.open("w", encoding="utf-8") as f:
                    json.dump(
                        messages,
                        f,
                        cls=WarningMessageEncoder,
                    )

                if messages:
                    print(f"{log=} generated with {len(messages)} warnings.")
    except ModuleNotFoundError as e:
        print(f"Creation failed, due missing dependency!\n\tpip install {e.name}")
        return 2
    except Exception as e:
        print(f"{documentation=} creation failed!\n\t{e}")
        return 1

    print(f"{documentation=} generated successfully.\n")

    return 0


if __name__ == "__main__":
    SystemExit(main())
