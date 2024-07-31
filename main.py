from user_operation import batch_transfer


def main():
    # get address file path from command line argument
    import sys, os
    if len(sys.argv) < 2:
        print("Please provide payment file path")
        sys.exit(1)
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print("File not found")
        sys.exit(1)
    batch_transfer(file_path)


if __name__ == '__main__':
    main()
