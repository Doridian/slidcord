import sys

from slidge.__main__ import main as slidge_main


def main() -> None:
    sys.argv.extend(["--legacy", "slidcord"])
    slidge_main()


if __name__ == "__main__":
    main()
