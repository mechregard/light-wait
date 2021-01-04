import argparse
import sys
from lightwait import LightWait
from .exception import LightwaitException

def main():
    """CLI Generate blog content"""

    parser = argparse.ArgumentParser(description="Generate blog post")
    parser.add_argument("-c", "--command", help="import or  generate")

    # import options
    parser.add_argument("-f", "--file", help="import markdown file path")
    parser.add_argument("-n", "--name", type=str, help="import short unique name")
    parser.add_argument("-d", "--description", type=str, help="import description")
    parser.add_argument("-t", "--tags", type=str, help="import tags list")

    # generate options
    parser.add_argument("-o", "--output", help="generate output directory")
    args = parser.parse_args()

    if args.command == "import":
        try:
            LightWait().import_md(args.file, args.name, args.description, args.tags.split(","))
        except LightwaitException as msg:
            print("Import failed:", msg)
        except:
            print("General error:", sys.exc_info()[0])

    elif args.command == 'generate':
        try:
            LightWait().generate(args.output)
        except LightwaitException as msg:
            print("Generate failed:", msg)
        except:
            print("General error:", sys.exc_info()[0])


if __name__ == "__main__":
    main()
