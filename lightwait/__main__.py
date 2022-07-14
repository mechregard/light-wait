import argparse
import sys
from lightwait import LightWait
from .exception import LightwaitException

def main():
    """CLI Generate blog content"""

    parser = argparse.ArgumentParser(description="Generate blog post")
    parser.add_argument("-c", "--command", help="import, bulk or generate", required=True)

    # import options
    parser.add_argument("-f", "--file", help="import markdown file path")
    parser.add_argument("-n", "--name", type=str, help="import short unique name")
    parser.add_argument("-d", "--description", type=str, help="import description")
    parser.add_argument("-t", "--tags", type=str, help="import tags list")

    # bulk options
    parser.add_argument("-s", "--src", help="import markdown src directory path")

    # generate options
    parser.add_argument("-o", "--output", help="generate output directory")
    args = parser.parse_args()

    if args.command == "import":
        try:
            if args.file is not None:
                LightWait().import_md(args.file,
                                      name=args.name,
                                      description=args.description,
                                      tags=args.tags.split(","))
                print("Imported markdown:  ", args.file)
            else:
                parser.print_help()
        except LightwaitException as msg:
            print("Import failed:", msg)
        except:
            print("General error:", sys.exc_info()[0])

    elif args.command == 'bulk':
        try:
            if args.src is not None:
                LightWait().import_dir(args.src)
                print("Bulk imported markdown:  ", args.src)
            else:
                parser.print_help()
        except LightwaitException as msg:
            print("Bulk import failed:", msg)
        except:
            print("General error:", sys.exc_info()[0])

    elif args.command == 'generate':
        try:
            if args.output is not None:
                LightWait().generate(args.output)
                print("Generated content to: ", args.output)
            else:
                parser.print_help()
        except LightwaitException as msg:
            print("Generate failed:", msg)
        except:
            print("General error:", sys.exc_info()[0])
    elif args.command == 'export':
        try:
            if args.output is not None:
                LightWait().export(args.output)
                print("Exported content to: ", args.output)
            else:
                parser.print_help()
        except LightwaitException as msg:
            print("export failed:", msg)
        except:
            print("General error:", sys.exc_info()[0])


if __name__ == "__main__":
    main()
