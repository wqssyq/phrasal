#!/usr/bin/env python
#
# Generate a full experiment configuration for PTM UIST 14 experiments.
# This script is dependent upon the document format generated by 
#
# TODO: Currently does not randomize the order of documents since document
# context is one of the "features" of the new UI.
#
# Author: Spence Green
#
import sys
import codecs
from argparse import ArgumentParser
import os
from os.path import join
import json
import string
import random
import itertools
from collections import defaultdict

# UI conditions for UIST14 experiments
UI_CONDITIONS = ['pe','imt']
OUT_FILENAME = 'experiment.json'

def pw_generator(size=8, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    """
    Simple password generator.

    See:
    http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
    """
    return ''.join(random.choice(chars) for x in xrange(size))

def index_to_list(index):
    """
    Convert a newline-delimited file index to a list.
    
    """
    with open(index) as infile:
        return [x.strip() for x in infile]

def make_pilot_layout():
    """
    Generates a Latin square layout for the pilot experiment. Assumes 4 subjects, 2 data sources,
    2 splits per source, and 2 UI conditions

    Output format is a dict->list[tuple] with
    the following format:

    0 -> [(0,0,1),(1,1,0)...]

    Where the tuple format is (source,split,ui).
    
    """

    #TODO(spenceg): This is hand-picked for a small experiment. But the way to generalize this process
    # is to construct the experiment from two basic structures: Latin squares and permutations. A Latin square
    # ensures that all treatments are randomized. A permutation contains all permutations of the input factors.
    user_to_layout = {}
    user_to_layout[0] = [(0,0,0),(1,0,0), (0,1,1),(1,1,1)]
    user_to_layout[1] = [(1,0,1),(0,1,1), (1,1,0),(0,0,0)]
    user_to_layout[2] = [(1,1,0),(0,1,0), (1,0,1),(0,0,1)]
    user_to_layout[3] = [(1,1,1),(0,1,1), (0,0,0),(1,0,0)]
    return user_to_layout

    
def make_experiment(user_prefix, num_users, num_splits, src_lang,
                    tgt_lang, source_a_index, a_url_prefix,
                    source_b_index, b_url_prefix,
                    source_train_index, train_url_prefix):
    """
    Generate a simple 2x|docs| experiment. 
    """
    source_dict = defaultdict(dict)

    # Partition the source documents
    # TODO(spenceg) Move this to a separate section
    source_a = index_to_list(source_a_index)
    split_a_size = int(len(source_a)/num_splits)
    source_b = index_to_list(source_b_index)
    split_b_size = int(len(source_b)/num_splits)
    source_dict[0][0] = source_a[0:split_a_size]
    source_dict[0][1] = source_a[split_a_size:len(source_a)]
    source_dict[1][0] = source_b[0:split_b_size]
    source_dict[1][1] = source_b[split_b_size:len(source_b)]
    source_train = index_to_list(source_train_index)
    
    exp_design = make_pilot_layout()
    spec = defaultdict(dict)
    
    for i in sorted(exp_design.keys()):
        username = user_prefix + str(i)
        password = pw_generator()
        print username,password
        spec[username]['password'] = password
        spec[username]['src_lang'] = src_lang
        spec[username]['tgt_lang'] = tgt_lang
        sessions = []
        for layout in exp_design[i]:
            source_id = layout[0]
            split_id = layout[1]
            condition_id = layout[2]
            url_prefix = a_url_prefix if source_id == 0 else b_url_prefix
            for filename in source_dict[source_id][split_id]:
                url = join(url_prefix, filename)
                sessions.append((url,UI_CONDITIONS[condition_id]))
        spec[username]['sessions'] = sessions

        # Training documents alternate between post-editing
        increment = lambda x,y: x+1 if x < (y-1) else 0
        ui_id = 0
        training = []
        for filename in source_train:
            url = join(train_url_prefix, filename)
            training.append((url,UI_CONDITIONS[ui_id]))
            ui_id = increment(ui_id, len(UI_CONDITIONS))
        spec[username]['training'] = training
        
    # Serialize to json
    with open(OUT_FILENAME,'w') as out_file:
        out_file.write(json.dumps(spec))
    print 'Wrote spec to: ',OUT_FILENAME
    

def main():
    """
    Process command line arguments and generate.
    """
    desc='Make a full experiment configuration'
    parser=ArgumentParser(description=desc)
    parser.add_argument('user_prefix',
                        help='All usernames will have this prefix.')
    parser.add_argument('num_users',
                        type=int,
                        help='Number of user profiles to generate.')
    parser.add_argument('num_splits',
                        type=int,
                        help='Number of splits per source.')
    parser.add_argument('src_lang',
                        help='Source language.')
    parser.add_argument('tgt_lang',
                        help='Target language.')
    parser.add_argument('source_a_index',
                        help='Index of files for source domain A.')
    parser.add_argument('source_a_url_prefix',
                        help='URL prefix to add to A files.')
    parser.add_argument('source_b_index',
                        help='Index of files for source domain B.')
    parser.add_argument('source_b_url_prefix',
                        help='URL prefix to add to B files.')
    parser.add_argument('source_train_index',
                        help='Index of files for training.')
    parser.add_argument('train_url_prefix',
                        help='URL prefix to add to train files.')
    args = parser.parse_args()

    make_experiment(args.user_prefix,
                    args.num_users,
                    args.num_splits,
                    args.src_lang,
                    args.tgt_lang,
                    args.source_a_index,
                    args.source_a_url_prefix,
                    args.source_b_index,
                    args.source_b_url_prefix,
                    args.source_train_index,
                    args.train_url_prefix)
    
if __name__ == '__main__':
    main()


