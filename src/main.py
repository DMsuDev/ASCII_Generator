import sys
from ascii_engine.app import AppEngine
from ascii_engine.log import setup_logging
from ascii_engine.cli.parser import parse_arguments


def main() -> None:
    setup_logging()
    app = AppEngine()

    # If no arguments are provided, run in normal mode
    if len(sys.argv) == 1:
        app.run()
        return

    # Parse command-line arguments
    args = parse_arguments()

    if args.command == "run":
        app.run_headless(
            args.input,
            output_path=args.output,
            dry_run=args.dry_run,
            source_type=args.type,
        )
    elif args.command == "status":
        # show basic status information
        app.settings = app.config_manager.load_normalized()
        print("Application settings:")
        try:
            for k, v in vars(app.settings).items():
                print(f" - {k}: {v}")
        except Exception:
            print(app.settings)


if __name__ == "__main__":
    main()
