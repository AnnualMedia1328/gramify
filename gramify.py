#!/usr/bin/env python3
"""n-gram generator on word, char and charset basis

Usage:
  gramify.py word <input_file> (<output_file>|--stdout) [--min-length=<int>] [--max-length=<int>] [--ngram-more]
  gramify.py character <input_file> (<output_file>|--stdout) [--min-length=<int>] [--max-length=<int>] [--rolling]
  gramify.py charset <input_file> <output_file> [--min-length=<int>] [--max-length=<int>] [--mixed] [--filter=<str>] [--filter-combo-length=<str>] [--cgram-rulify-beta]
  gramify.py all <input_file> (<output_file>|--stdout) [--min-length=<int>] [--max-length=<int>] [--ngram-more] [--rolling] [--mixed] [--filter=<str>] [--filter-combo-length=<str>] [--cgram-rulify-beta]
  gramify.py (-h | --help)
  gramify.py --version

Options:
  -h --help                     Show this screen.
  --version                     Show version.
  --min-length=<int>            Minimum size of k,n,c-gram output.
  --max-length=<int>            Maximum size of k,n,c-gram output.
  --stdout                      Print output to screen (STDOUT)
  --rolling                     Make kgrams in one file based on length instead of into three groups of start, mid, end.
  --mixed                       Allow for mixed charset cgrams
  --filter=<str>                Filter for specific outputs using solo, duo, duostart, duoend, start, mid, and end. (Default uses no filter)
  --filter-combo-length-beta=<int>   Create automatic filter combinations of start,mid,end (startmid,startmidmidendend) based on length [BETA]
  --cgram-rulify-beta           Convert cgram output into hashcat-rules [BETA]
  --ngram-more                  Add extra candidates by removing casing and special characters

Gram-types:
  K-Gram (Character):           Letter based https://nlp.stanford.edu/IR-book/html/htmledition/k-gram-indexes-for-wildcard-queries-1.html
  N-Gram (Word):                Word based https://en.wikipedia.org/wiki/N-gram
  C-Gram (Charset):             Charset boundry inspired by https://github.com/hops/pack2/blob/master/src/cgrams.rs

Filter:
  Format filter using a comma separated string of combinations of start, mid, and end.
  using --filter 'solo' will output 1 file containing all passwords with exclusively 1 element.
  using --filter 'duo,duostart,duoend' will output 3 files containing all passwords with exclusively 2 element.
  using --filter 'start,mid,end' will output 3 files containing the first element, the middle elements and the last element respectively (does not include solo or duo).
  using --filter 'startmid' will output 1 file containing the first and middle elements, but not the last which is perfect for -a6 hybrid attacks.
  using --filter 'midend' will output 1 file containing the middle and end elements, but not the first which is perfect for -a7 hybrid attacks.
  You can make any combination yourself. "startmidstartmidendmidstart" for example.
  Recommended filters to play with are listed above
"""
import re
import os
import sys
import binascii
from itertools import permutations
from tqdm import tqdm
from docopt import docopt

sys.setrecursionlimit(5000)
output_file_names = []


# ... [all your helper function definitions unchanged, omitted for brevity] ...
# (copy all functions here as in your original code)

# Everything from output_filter_writer ... to ... cgramify
# These functions are unchanged and should be copied as in your original file.

# ---- insert unchanged functions here ----

def output_filter_writer(output_filter, output_filter_file_handler, matches):
    # ... [function body unchanged]
    for filter_item in output_filter:
        filter_output = []
        if(filter_item == "solo" and len(matches) == 1):
            output_filter_file_handler[filter_item].write(matches[0] + "\n")
            continue

        if len(matches) < 2: continue
        if filter_item == "solo": continue

        if len(matches) == 2:
            if filter_item == "duostart":
                output_filter_file_handler[filter_item].write(matches[0] + "\n")
                continue
            if filter_item == "duoend":
                output_filter_file_handler[filter_item].write(matches[1] + "\n")
                continue
            if filter_item == "duo":
                output_filter_file_handler[filter_item].write(matches[0] + matches[1] + "\n")
                continue
        if len(matches) < 3: continue
        if filter_item == "duostart": continue
        if filter_item == "duoend": continue
        if filter_item == "duo": continue
        if filter_item == "solo": continue

        start = matches[0]
        mid = matches[1:-1]
        end = matches[-1]

        _filter = filter_item
        filter_output = []
        while _filter != "":
            if _filter.startswith("start"):
                filter_output.append(start)
                _filter = _filter[len("start"):]
                continue

            if _filter.startswith("mid"):
                filter_output += mid
                _filter = _filter[len("mid"):]
                continue

            if _filter.startswith("end"):
                filter_output.append(end)
                _filter = _filter[len("end"):]
                continue

        for item in filter_output:
            output_filter_file_handler[filter_item].write(item)
        if len(filter_output) > 0:
            output_filter_file_handler[filter_item].write("\n")

# ... [rest of the helper functions unchanged, copy them here] ...


# -------- NEW FUNCTION --------
def run_all_grams(args):
    """Run all three gram types with appropriate arguments."""
    # Prepare ngram arguments
    ngram_args = args.copy()
    ngram_args['word'] = True
    ngram_args['character'] = False
    ngram_args['charset'] = False
    ngram_args['all'] = False
    print("\n=== Generating n-grams (word) ===")
    ngramify(ngram_args)

    # Prepare kgram arguments
    kgram_args = args.copy()
    kgram_args['word'] = False
    kgram_args['character'] = True
    kgram_args['charset'] = False
    kgram_args['all'] = False
    print("\n=== Generating k-grams (character) ===")
    kgramify(kgram_args)

    # Prepare cgram arguments
    cgram_args = args.copy()
    cgram_args['word'] = False
    cgram_args['character'] = False
    cgram_args['charset'] = True
    cgram_args['all'] = False
    # cgramify requires <output_file>, not --stdout
    if cgram_args.get('<output_file>') is None or cgram_args['--stdout']:
        cgram_args['<output_file>'] = (args.get('<output_file>') or args.get('<input_file>')) + '.cgram'
    print("\n=== Generating c-grams (charset) ===")
    cgramify(cgram_args)

# ----------- MAIN -----------
if __name__ == '__main__':
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

    if ARGS.get('--filter-combo-length') is not None and not ARGS.get('--filter-combo-length').isnumeric():
        print("Filter combo length should be numeric")
        exit()

    if ARGS.get('all'):
        run_all_grams(ARGS)
    elif ARGS.get('word'):
        ngramify(ARGS)
    elif ARGS.get('character'):
        kgramify(ARGS)
    elif ARGS.get('charset'):
        cgramify(ARGS)

    print()
    print("Don't forget to de-duplicate and sort the output.\nRecommended commands:")
    for item in output_file_names:
        print("cat \"" + item + "\" | sort | uniq -c | sort -rn | awk '($1 >= 5)' | awk '{if ($1 >=1) {$1=\"\"; print substr($0, index($0, $2))}}' > \"" + item + ".sorted\"")
