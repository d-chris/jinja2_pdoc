from . import documentation, readme


def main():
    """
    Render the README.md file and create a static html documentation for the project
    in the 'public' directory.

    Returns non-zero on failure.
    """

    return readme() or documentation()


if __name__ == "__main__":
    raise SystemExit(main())
