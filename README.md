# Gramify

Create n-grams of wordlists based on words, characters, or charsets for use in offline password attacks and data analysis.

---

## Features

- Generate n-grams by word, character, charset, or all modes at once
- Flexible filtering and output control
- Output to file or screen (STDOUT)
- Advanced options for hybrid password attacks and hashcat rule conversion

---

## Installation

```sh
git clone https://github.com/AnnualMedia1328/gramify.git
cd gramify
pip install -r requirements.txt
```

---

## Usage

Run gramify.py with one of the following commands:

### 1. All Modes at Once

Generate all types of n-grams (word, character, charset) in a single command.

```sh
python gramify.py all <input_file> (<output_file>|--stdout) [OPTIONS]
```

### 2. Word N-Grams

```sh
python gramify.py word <input_file> (<output_file>|--stdout) [OPTIONS]
```

### 3. Character K-Grams

```sh
python gramify.py character <input_file> (<output_file>|--stdout) [OPTIONS]
```

### 4. Charset C-Grams

```sh
python gramify.py charset <input_file> <output_file> [OPTIONS]
```

### 5. Help & Version

```sh
python gramify.py -h
python gramify.py --version
```

---

## Options

- `--min-length=<int>`       Minimum n-gram size
- `--max-length=<int>`       Maximum n-gram size
- `--ngram-more`             Add extra candidates by removing casing and special characters
- `--rolling`                (Character/All) Output all k-gram lengths in one file
- `--mixed`                  (Charset/All) Allow mixed charset c-grams
- `--stdout`                 Output to screen instead of file
- `--filter=<str>`           (Charset) Filter outputs by type (see below)
- `--filter-combo-length-beta=<int>`  (Charset) Auto filter combos by length [BETA]
- `--cgram-rulify-beta`      (Charset) Convert c-grams to hashcat rules [BETA]

---

## Filter Examples (Charset/All)

- `solo`            Only n-grams with one element
- `duo,duostart,duoend`   Only n-grams with two elements or starting/ending with two
- `start,mid,end`   Separate files for first, middle, last elements
- `startmid`        First and middle (for -a6 hybrid attacks)
- `midend`          Middle and end (for -a7 hybrid attacks)

Combine filters with commas:  
`--filter='solo,duo'`

---

## Example Commands

**All n-gram types, output to file:**
```sh
python gramify.py all mywords.txt output.txt --min-length=2 --max-length=5 --ngram-more --rolling
```

**Word n-grams, print to screen:**
```sh
python gramify.py word mywords.txt --stdout --min-length=2 --max-length=3
```

**Character k-grams, classic style:**
```sh
python gramify.py character mywords.txt output.txt --min-length=4 --max-length=8
```

**Charset c-grams with filter:**
```sh
python gramify.py charset mywords.txt output.txt --min-length=3 --max-length=6 --filter='start,mid,end'
```

---

## About N-Gram Modes

- **Word (n-gram):** Sequences of words (good for phrase analysis)
- **Character (k-gram):** Sequences of characters (useful for password patterns)
- **Charset (c-gram):** String segments based on charset type (for hybrid and combinator attacks)
- **All:** Run all the above in one go!

---

## License

[Apache License 2.0](LICENSE)

---

## More Info

For advanced usage, see comments and docstrings in [gramify.py](https://github.com/AnnualMedia1328/gramify/blob/master/gramify.py).
