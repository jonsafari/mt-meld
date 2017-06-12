#!/usr/bin/env python3
# By Jon Dehdari, 2017
""" Melds the source, reference, and multiple hypotheses of MT outputs into one entry. """

from __future__ import print_function
import os
import sys
import argparse
import re

def parse_truecase_model(truecase_model_file):
    """ Reads in the textual model file from Moses' truecaser.

    Args:
        truecase_model_file (string): path to Moses' truecaser model

    Returns:
        dict: mapping from any-cased word form to the truecased form
    """

    truecase_dict = {}
    with open(truecase_model_file) as tc_file:
        for line in tc_file:
            split_line = line.split()
            # Populate truecase_dict with lowercase-first-token -> first-token
            truecase_dict[split_line[0].lower()] = split_line[0]
    return truecase_dict

def truecase_line(line, truecase_dict):
    """ Given a string of untokenized text, applies a truecaser to it.

    Args:
        line (string): untokenized text
        truecase_dict (dict): truecase model

    Returns:
        string: truecased untokenized text
    """

    tokens = line.split()
    for i in range(len(tokens)):
        word = tokens[i]
        if word.lower() in truecase_dict:
            tokens[i] = truecase_dict[word.lower()]
    return ' '.join(tokens)


def print_hyp(hyp_num, ref_line, hyp_line):
    """ Prints each hypothesis sentence.

    Args:
        hyp_num (int): ordinal number of which hypothesis it is
        ref_line (string): Reference translation sentence
        hyp_line (string): Hypothesis translation sentence
    """

    print("MT%i: " % hyp_num, end='')
    # If the MT output matches the reference, you get a smiley!
    if ref_line == hyp_line:
        print(":-) ", end='')
    else:
        print("    ", end='')
    print("%s" % hyp_line)

def process_line(cmd_args, line, re_bpe, detok, truecase_dict):
    """ Common stuff that needs to happen for every line, regardless of source. """

    line = line.rstrip()
    if cmd_args.lc:
        line = line.lower()
    elif cmd_args.truecase:
        line = truecase_line(line, truecase_dict)
    if cmd_args.del_bpe:
        line = re_bpe.sub(r'', line)
    if cmd_args.detok:
        line = detok.detokenize(line.split(), return_str=True)
    line = re.sub(r"&apos;", r"'", line) # Fix Moses script output
    return line

def process_lines(cmd_args, src, ref, hyps, truecase_dict):
    """ Traverse all sentences from all sources. """

    re_bpe = re.compile("@@ ")
    if cmd_args.google:
        try:
            import mtranslate
        except ImportError:
            print("Error: Install package 'mtranslate': pip install --user -U mtranslate")
            exit(2)

    if cmd_args.detok:
        try:
            from nltk.tokenize.moses import MosesDetokenizer
            detok = MosesDetokenizer(lang=cmd_args.detok)
        except ImportError: # NLTK isn't installed
            print("Error: Install package 'nltk': pip install --user -U nltk")
            exit(3)
        except LookupError: # NLTK's data package perluniprops isn't installed
            print("Error: Install NLTK data package 'perluniprops': \
                   import nltk; nltk.download('perluniprops')")
            exit(4)


    #all_lines = {ref:[]}
    line_num = 0
    for src_line in src:
        line_num += 1
        if line_num > cmd_args.head:
            break

        src_line = process_line(cmd_args, src_line, re_bpe, detok, truecase_dict)
        print("Src:     %s" % src_line)

        ref_line = ''
        if ref is not None:
            ref_line = ref.readline()
            ref_line = process_line(cmd_args, ref_line, re_bpe, detok, truecase_dict)
            #all_lines[ref.append(ref_line)]
            print("Ref:    ", ref_line)

        hyp_num = 1
        for hyp in hyps:
            hyp_line = hyp.readline()
            hyp_line = process_line(cmd_args, hyp_line, re_bpe, detok, truecase_dict)
            print_hyp(hyp_num, ref_line, hyp_line)
            hyp_num += 1

        if cmd_args.google:
            google_line = mtranslate.translate(src_line, cmd_args.google)
            # Don't truecase Google output
            google_line = process_line(cmd_args, google_line, re_bpe, detok, {})
            print_hyp(hyp_num, ref_line, google_line)

        print()


def main():
    """ Process command-line arguments and print source sentence, reference, and all hypotheses."""

    parser = argparse.ArgumentParser(
        description='Melds the source, reference, and multiple hypotheses of \
                     MT outputs into one entry')
    parser.add_argument('-s', '--src', type=str, default='',
                        help='Source text file')
    parser.add_argument('-r', '--ref', type=str,
                        help='Reference text file')
    parser.add_argument('--hyps', type=str, default=[], nargs='+',
                        help='Hypotheses text file(s)')
    parser.add_argument('--del_bpe', action="store_true",
                        help='Delete BPE symbols')
    parser.add_argument('--lc', action="store_true",
                        help='Lowercase all input')
    parser.add_argument('--truecase', type=str,
                        help='Truecase output, using specified Moses-truecaser model file')
    parser.add_argument('--detok', type=str, default="en",
                        help="Detokenize using NLTK's Moses detokenizer. \
                              Argument is target language code. Default: %(default)s")
    parser.add_argument('--head', type=int, default=sys.maxsize,
                        help='Only show first n lines.')
    parser.add_argument('--google', type=str,
                        help='Also translate source with Google Translate. \
                              Argument is target language code.')
    cmd_args = parser.parse_args()

    if not os.path.isfile(cmd_args.src):
        print("Error: You need to supply a source file.  Add --src <FILE>")
        exit(1)

    truecase_dict = parse_truecase_model(cmd_args.truecase)

    with open(cmd_args.src) as src:
        if cmd_args.ref is not None:
            ref = open(cmd_args.ref)
        else:
            ref = None

        hyps = []
        for hyp_file in cmd_args.hyps:
            try:
                hyps.append(open(hyp_file))
            except IOError:
                print("Error: Could not open hyp_file")

        process_lines(cmd_args, src, ref, hyps, truecase_dict)

if __name__ == '__main__':
    main()
