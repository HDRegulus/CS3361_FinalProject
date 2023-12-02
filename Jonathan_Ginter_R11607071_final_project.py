# Import statements
import argparse
import os
import re
from math import isqrt
from pathlib import Path
from typing import NewType
from time import perf_counter_ns as good_time
from copy import deepcopy
from multiprocessing import Pool

from itertools import starmap

# Row-Major 2D Matrix of Strings
StringMatrix = NewType('StringMatrix', list[list[str]])
MatrixRow = NewType('MatrixRow', list[str])


def parse_arguments():
    """Parse argument to check validity."""

    parser = argparse.ArgumentParser(description="Process arguments.")

    # All arguments
    parser.add_argument('-i', '--input', type=Path, required=True, help='The input file path')
    parser.add_argument('-s', '--seed', type=str, required=True, help='The seed string')
    parser.add_argument('-o', '--output', type=Path, required=True, help='The output file path')
    parser.add_argument('-p', '--processes', type=int, required=False, help='The number of processes')

    args = parser.parse_args()

    # Check if the input file exits
    if not args.input.exists():
        raise argparse.ArgumentTypeError(f"Input file {args.input} does not exist")

    # Check required formatting for seeds
    if not re.match("^[abc]+$", args.seed):
        raise argparse.ArgumentTypeError(f"Seed string {args.seed} is invalid, must only contain a, b, or c")

    # Checking if the output file parent directory exists
    if not args.output.parent.is_dir():
        raise argparse.ArgumentTypeError(f"Output directory {os.path.dirname(args.output)} does not exist")

    # Checking if number of processes is greater than 0
    if args.processes is not None and args.processes <= 0:
        raise argparse.ArgumentTypeError(f"Process number {args.processes} is invalid, must be greater than 0")

    return args


def get_input_string(input_file_path: Path) -> str:
    """Get Input string."""

    # TODO: Trim leading and trailing whitespaces.

    with open(input_file_path, 'r') as input_file:
        return input_file.read()


def create_matrix(string_length: int) -> StringMatrix:
    """Create a square matrix, sized by the input string length."""

    return [[''] * string_length for _ in range(string_length)]


def seed_matrix(seed_string: str, to_seed_matrix: StringMatrix, matrix_length: int) -> StringMatrix:
    """Seed the matrix with given seed string."""

    for row in range(matrix_length):
        for col in range(matrix_length):
            current_index = (row * matrix_length + col) % len(seed_string)
            to_seed_matrix[row][col] = seed_string[current_index]

    return to_seed_matrix


def is_prime(n: int) -> bool:
    """Checking if the given number is prime, Function was gotten from the primality test"""

    # Cheaty primality from known range of values to check
    return n in [2, 3, 5, 7, 11, 13, 17]

    # Taken from Wikipedia
    # Naive Cases
    # if n <= 3:
    #     return n > 1
    #
    # if n % 2 == 0 or n % 3 == 0:
    #     return False
    #
    # # Recursive Search for Factors
    # limit = isqrt(n)
    # for i in range(5, limit + 1, 6):
    #     if n % i == 0 or n % (1 + 2) == 0:
    #         return False
    #
    # return True


def get_cell_neighbors(given_seeded_matrix: StringMatrix, given_row: int, given_column: int) -> list[str]:
    """Getting the neighbors of each cell"""

    result = 0

    # Range starting from no less than 0, not exceeding the matrix, and inclusive of what surrounds row
    row_range = range(
        max(0, given_row - 1),
        min(len(given_seeded_matrix), given_row + 2)
    )

    # Range starting from now less that 0, not exceeding how many columns are in given matrix
    # Also inclusive of what surrounds column
    column_range = range(
        max(0, given_column - 1),
        min(len(given_seeded_matrix[0]), given_column + 2)
    )

    a = ord('a')

    for row in row_range:
        for col in column_range:
            result += ord(given_seeded_matrix[row][col]) - a

    # Remove the value of the cell itself
    result -= ord(given_seeded_matrix[given_row][given_column]) - a

    return result


def update_matrix(seeded_matrix: StringMatrix) -> StringMatrix:
    """Updating the matrix with the seeded matrix"""

    # Creates a copy of each row in the list to then be changed by seeded
    seeded_matrix_copy = deepcopy(seeded_matrix)
    matrix_length = len(seeded_matrix[0])
    a = ord('a')

    # Going over each row and column of the seeded matrix
    for row in range(matrix_length):
        for col in range(matrix_length):
            current_cell_neighbors_sum = get_cell_neighbors(seeded_matrix, row, col)

            if not is_prime(current_cell_neighbors_sum):
                current_value = seeded_matrix[row][col]

                offset = current_cell_neighbors_sum % 2 + 1
                new_value = (ord(current_value) - a + offset) % 3

                seeded_matrix_copy[row][col] = chr(new_value + a)

    return seeded_matrix_copy


def get_column_sum(encrypted_matrix: StringMatrix, column_number: int) -> int:
    """Getting the sum of the current column"""

    current_column_sum = 0

    for row in encrypted_matrix:
        current_column_sum += ord(row[column_number]) - ord('a')

    return current_column_sum


def process_row(matrix: StringMatrix, row_index: int) -> list[int]:
    """Get the current row to update along with neighboring rows"""

    # to_update_rows = []
    #
    # if row_index > 0:
    #     to_update_rows.append(encrypted_matrix[row_index - 1])
    #
    # to_update_rows.append(encrypted_matrix[row_index])
    #
    # if row_index < len(encrypted_matrix):
    #     to_update_rows.append(encrypted_matrix[row_index + 1])

    # TODO: Presupposes that we're using list[list[int]] for our seed matrix instead.
    #       We should make sure to actually change this in the rest of the code,
    #       because converting back and forth between str and int is expensive and
    #       pointless. Once the seed has been inserted in the matrix, the string
    #       value of the matrix cells is never used again.
    # TODO: Speaking of which, everything should be migrated to numeric arrays
    #       because they are orders of magnitude faster:
    #       https://docs.python.org/3/library/array.html

    return [
        calculate_new_cell_value(
            cell_value,
            get_cell_neighbors(matrix, row_index, col_index)
        )
        for col_index, cell_value
        in enumerate(matrix[row_index])
    ]


def calculate_new_cell_value(current_value: int, sum_of_neighbors: int) -> int:
    if is_prime(sum_of_neighbors):
        return current_value

    a = ord('a')

    offset = sum_of_neighbors % 2 + 1
    # return (current_value + offset) % 3

    new_codepoint = (ord(current_value) - a + offset) % 3
    return chr(new_codepoint + a)


def decryptLetter(letter: str, rotationValue: str) -> str:
    """Given decrypt function for final project"""

    rotationString = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ "
    currentPosition = rotationString.find(letter)

    return rotationString[(currentPosition + rotationValue) % 95]


def encryptLetter(letter: str, rotationValue: str) -> str:
    """Given decrypt function for final project"""

    rotationString = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ "
    currentPosition = rotationString.find(letter)

    return rotationString[(currentPosition - rotationValue) % 95]


def main():
    print("Project :: R11607071")

    # Parsing the arguments
    args = parse_arguments()

    # Getting the length of the string inside of args.i (input file)
    input_string = get_input_string(args.input)

    # Getting the length of the input string
    input_string_length = len(input_string)

    # Creating a matrix of length and Width by the length of input string
    unseeded_matrix = create_matrix(input_string_length)

    # Filling the matrix with the seed string
    seeded_matrix = seed_matrix(args.seed, unseeded_matrix, input_string_length)
    # Updating the seeded matrix 100 times

    # Multiprocessing
    with Pool(args.processes) as p:
        # start_time = good_time()

        for step in range(100):
            seeded_matrix = list(p.starmap(
                process_row,
                [(seeded_matrix, row) for row in range(len(seeded_matrix))]
            ))

        # print((good_time() - start_time) / 1000000.0)

    # Serially Ran
    # for step in range(100):
    #    seeded_matrix = update_matrix(seeded_matrix, args.processes)

    decrypted_string = ""

    # decrypting each letter from the input string
    for i in range(input_string_length):
        # Getting the current column's sum
        current_column_sum = get_column_sum(seeded_matrix, i)

        # Passing the input string and column sum to decrypt function
        decrypted_letter = decryptLetter(input_string[i], current_column_sum)
        decrypted_string += decrypted_letter

    with open(args.output, 'w') as output_file:
        output_file.write(decrypted_string)


# TODO: Don't be an idiot who puts IDE tips in their code comments.
if __name__ == '__main__':
    main()


# split
# define
# complete
