import argparse

def grep(search: str):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("searchterm", nargs="*")
    args = parser.parse_args()

    print(args.searchterm)

if __name__ == "__main__":
    main()
