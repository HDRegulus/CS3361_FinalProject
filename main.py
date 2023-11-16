# Import statements
import argparse
import os
import re


# Parse argument to check validity
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process arguments.")

    # All arguments
    parser.add_argument('-i', type=str, requried=True, help='The input file path')
    parser.add_argument('-s', type=str, required=True, help='The seed string')
    parser.add_argument('-o', type=str, required=True, help='The output file path')
    parser.add_argument('-p', type=int, required=False, help='The number of processes')

    # Parse arguments
    args = parser.parse_args()

    # Check if the input file exits || returns true if file exists
    if not os.path.isfile(args.i):
        raise argparse.ArgumentTypeError("Input file {args.i} does not exist")

    # Check if seed string only has a, b, and c || returns match
    if not re.match("^[abc]+$", args.s):
        raise argparse.ArgumentTypeError("Seed string {args.s} is invalid, must only contain a, b, or c")

    # Checking if the output file path exists || returns true if directory exists
    if not os.path.isdir(os.path.dirname(args.o)):
        raise argparse.ArgumentTypeError("Output directory {os.path.dirname(args.o)} does not exist")

    # Checking if number of processes is greater than 0
    if args.p <= 0:
        raise argparse.ArgumentTypeError("Number of processes {args.p} is invalid, must be greater than 0")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    args = parse_arguments()
    print('Input file:', args.i)
    print('Seed string:', args.s)
    print('Output file:', args.o)
    print('Number of Processes:', args.p)

# FOR LATER: PLEASE USE .map FOR SOME SHIT LATER
