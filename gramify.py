import os
import sys
from docopt import docopt

output_file_names = []

def ngramify(args):
    """Generate word n-grams from the input file."""
    min_length = int(args.get('--min-length', 1))
    max_length = int(args.get('--max-length', 1))
    input_file = args.get('<input_file>')
    output_file = args.get('<output_file>')
    to_stdout = args.get('--stdout', False)
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    ngrams = set()
    for line in lines:
        words = line.split()
        for n in range(min_length, max_length+1):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngrams.add(ngram)

    if to_stdout or output_file is None:
        for ngram in sorted(ngrams):
            print(ngram)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            for ngram in sorted(ngrams):
                f.write(ngram + '\n')
        output_file_names.append(output_file)

def kgramify(args):
    """Generate character k-grams from the input file."""
    min_length = int(args.get('--min-length', 1))
    max_length = int(args.get('--max-length', 1))
    input_file = args.get('<input_file>')
    output_file = args.get('<output_file>')
    to_stdout = args.get('--stdout', False)
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    kgrams = set()
    for line in lines:
        for n in range(min_length, max_length+1):
            for i in range(len(line) - n + 1):
                kgram = line[i:i+n]
                kgrams.add(kgram)

    if to_stdout or output_file is None:
        for kgram in sorted(kgrams):
            print(kgram)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            for kgram in sorted(kgrams):
                f.write(kgram + '\n')
        output_file_names.append(output_file)

def cgramify(args):
    """Generate charset c-grams from the input file (basic version)."""
    min_length = int(args.get('--min-length', 1))
    max_length = int(args.get('--max-length', 1))
    input_file = args.get('<input_file>')
    output_file = args.get('<output_file>')
    to_stdout = args.get('--stdout', False)
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    # This is a basic charset-gram: treat each character as a token.
    cgrams = set()
    for line in lines:
        chars = list(line)
        for n in range(min_length, max_length+1):
            for i in range(len(chars) - n + 1):
                cgram = ''.join(chars[i:i+n])
                cgrams.add(cgram)

    if to_stdout or output_file is None:
        for cgram in sorted(cgrams):
            print(cgram)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            for cgram in sorted(cgrams):
                f.write(cgram + '\n')
        output_file_names.append(output_file)

def run_all_grams(args):
    ngram_args = args.copy()
    ngram_args['word'] = True
    ngram_args['character'] = False
    ngram_args['charset'] = False
    ngram_args['all'] = False
    print("\n=== Generating n-grams (word) ===")
    ngramify(ngram_args)

    kgram_args = args.copy()
    kgram_args['word'] = False
    kgram_args['character'] = True
    kgram_args['charset'] = False
    kgram_args['all'] = False
    print("\n=== Generating k-grams (character) ===")
    kgramify(kgram_args)

    cgram_args = args.copy()
    cgram_args['word'] = False
    cgram_args['character'] = False
    cgram_args['charset'] = True
    cgram_args['all'] = False
    if cgram_args.get('<output_file>') is None or cgram_args.get('--stdout'):
        cgram_args['<output_file>'] = (args.get('<output_file>') or args.get('<input_file>')) + '.cgram'
    print("\n=== Generating c-grams (charset) ===")
    cgramify(cgram_args)

def print_sort_recommendations():
    print()
    print("Don't forget to de-duplicate and sort the output.\nRecommended commands:")
    for item in output_file_names:
        print("cat \"" + item + "\" | sort | uniq -c | sort -rn | awk '($1 >= 5)' | awk '{if ($1 >=1) {$1=\"\"; print substr($0, index($0, $2))}}' > \"" + item + ".sorted\"")

if __name__ == '__main__':
    __doc__ = """
gramify.py

Usage:
    gramify.py all <input_file> (<output_file>|--stdout) [--min-length=<int>] [--max-length=<int>]
    gramify.py word <input_file> (<output_file>|--stdout) [--min-length=<int>] [--max-length=<int>]
    gramify.py character <input_file> (<output_file>|--stdout) [--min-length=<int>] [--max-length=<int>]
    gramify.py charset <input_file> <output_file> [--min-length=<int>] [--max-length=<int>]
    gramify.py -h | --help
    gramify.py --version

Options:
    --min-length=<int>    Minimum n-gram size [default: 1]
    --max-length=<int>    Maximum n-gram size [default: 1]
    --stdout              Output to screen instead of file
    -h --help             Show this screen.
    --version             Show version.
"""
    ARGS = docopt(__doc__, version='2.5')
    if not os.path.exists(ARGS.get('<input_file>')):
        print("Input file does not exist.")
        sys.exit()

    if ARGS.get('--min-length') is not None and int(ARGS.get('--min-length')) < 0:
        print("Min Length should be greater than 0.")
        sys.exit()

    if ARGS.get('--max-length') is not None and int(ARGS.get('--max-length', 1)) < 0:
        print("Max Length should be greater than 0.")
        sys.exit()

    if ARGS.get('--min-length') is not None and ARGS.get('--max-length') is not None:
        if int(ARGS.get('--min-length')) > int(ARGS.get('--max-length')):
            print("Min Length should be smaller or equal to Max length.")
            exit()

    if ARGS.get('all'):
        run_all_grams(ARGS)
    elif ARGS.get('word'):
        ngramify(ARGS)
    elif ARGS.get('character'):
        kgramify(ARGS)
    elif ARGS.get('charset'):
        cgramify(ARGS)

    print_sort_recommendations()
