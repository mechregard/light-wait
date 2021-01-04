import argparse
from lightwait import LightWait
import os

def main():
    """CLI Generate blog content"""

    print("CWD:",os.getcwd())
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

    lw = LightWait()
    if args.command == "import":
        lw.import_md(args.file, args.name, args.description, args.tags.split(","))
    elif args.command == 'generate':
        lw.generate(args.output)


if __name__ == "__main__":
    main()
