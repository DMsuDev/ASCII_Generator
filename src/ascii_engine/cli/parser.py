import argparse
import sys
from typing import Optional


def parse_arguments(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """
    Function that parses the command-line arguments.
    Useful for testing and for reuse in other contexts.
    """

    # If no arguments are provided, use sys.argv
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="ascii_generator",
        description="Ascii art generator from images and videos.",
        epilog="Example: python ascii_generator run --input path/to/file --type image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", title="available commands", required=True)

    # run command
    p_run = subparsers.add_parser("run", help="Execute processing in headless mode")
    p_run.add_argument("--input", "-i", required=True, help="Input file, directory or 'camera'")
    p_run.add_argument("--output", "-o", default="output/", help="Output folder or file path")
    p_run.add_argument("--dry-run", action="store_true", help="Simulate execution without making changes")
    p_run.add_argument(
        "--type", "-t",
        choices=["image", "video", "camera"],
        default="image",
        help="Type of the input source",
    )

    # status command
    p_status = subparsers.add_parser("status", help="Show application status or information")
    p_status.add_argument("--json", action="store_true", help="Output in JSON format")

    return parser.parse_args(argv)