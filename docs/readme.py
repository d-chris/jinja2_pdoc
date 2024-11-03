from jinja2_pdoc import Environment


def main():
    """
    Render the README.md file using the README.md.jinja2 template.

    Requires following PyPi packages:
    - 'pathlibutil'

    Returns non-zero on failure.
    """

    try:
        from pathlibutil import Path

        template = Path(__file__).with_name("README.md.jinja2")
        readme = Path("README.md")

        with template.open("r") as file:
            template = Environment(
                keep_trailing_newline=True,
            ).from_string(file.read())

        with readme.open("w") as file:
            file.write(template.render())

    except Exception as e:
        print(f"{readme=} creation failed!\n\t{e}")
        return 1

    print(f"{readme=} created successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
