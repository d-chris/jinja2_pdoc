import subprocess
import sys


def main():
    """
    Check for outdated dependencies for the project.
    """

    p = subprocess.run(
        "poetry show --only=main -T -o",
        shell=True,
        capture_output=True,
        encoding="utf-8",
    )

    try:
        p.check_returncode()
    except subprocess.CalledProcessError as e:
        print(e, e.stderr.replace("\n", " "), sep="\n\n", file=sys.stderr)
        return 2

    if p.stdout.strip():
        print(p.stdout, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
