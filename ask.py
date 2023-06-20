#!/usr/bin/env python

from os import getenv
from enum import Enum
from dataclasses import dataclass
from pprint import pprint
from argparse import ArgumentParser
from time import sleep
import json
import re
import requests
import random

# small utils ==================================================================

# normalizes whitespace to a single space
def normws(s):
    return re.sub(r"\s+", " ", s).strip()

# requesting ===================================================================

API_KEY = None
ENDPOINT = 'https://api.openai.com/v1/chat/completions'
MODEL = 'gpt-3.5-turbo'

def messager(role):
    return lambda msg: { 'role': role, 'content': msg }

def ask(prompt, system_msg=None):
    if system_msg is None:
        system_msg = DEFAULT_SYSTEM_MSG

    # build conversation
    sys = messager('system')
    user = messager('user')

    convo = [
        sys(system_msg),
        user(prompt),
    ]

    # make request
    return requests.post(
        ENDPOINT,
        json = {
            'model': MODEL,
            'messages': convo,
        },
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {API_KEY}",
        },
    ).json()

# automagic ====================================================================

@dataclass(frozen=True)
class Query:
    """typed construction of prompts"""
    system_msg: str
    prompt: str

    # either fails with an exception or returns the convo
    def send(self, passwd_examples: list[str]):
        passwds = ", ".join(passwd_examples)
        prompt = self.prompt.replace("PASSWORDS", passwds)

        res = ask(prompt, self.system_msg)
        if 'error' in res:
            raise Exception(f"openai error: {res['error']['message']}")

        chat_res = res['choices'][0]['message']

        return [
            messager('system')(self.system_msg),
            messager('user')(prompt),
            chat_res,
        ]

# generator which produces and sends queries iteratively. I would parallelize
# this in js but I have no idea how python async works and no interest honestly
def prompt_matrix(matrix_file, passwd_file, k):
    # load & preprocess matrix
    matrix = json.load(matrix_file)
    matrix['prompts'] = list(map(normws, matrix['prompts']))

    # load passwds
    with open(passwd_file, 'r') as f:
        # easily optimizable if this is a bottleneck
        passwd_examples = random.choices(f.read().split(), k=k)

    # generate queries
    for system_msg in matrix['system']:
        for prompt in matrix['prompts']:
            yield Query(system_msg, prompt).send(passwd_examples)

# ==============================================================================

def parse_args():
    parser = ArgumentParser(
        description="openai DDOSing tool",
    )
    parser.add_argument(
        'passwd_file',
        type=str,
        help="file full of newline-separated passwords to be used in prompting",
    )
    parser.add_argument(
        '-o',
        '--output',
        metavar='output.json',
        type=str,
        required=True,
        help="output json destination filepath",
    )
    parser.add_argument(
        '-m',
        '--matrix',
        metavar='matrix.json',
        type=str,
        required=True,
        help="matrix json filepath",
    )
    parser.add_argument(
        '-k',
        '--number-passwords',
        type=int,
        default=20,
        help="number of passwords to include in each prompt",
    )

    return parser.parse_args()

def main():
    global API_KEY

    # input stuff
    args = parse_args()

    API_KEY = getenv("OPENAI_API_KEY")
    if API_KEY is None:
        print("couldn't read 'OPENAI_API_KEY' from env, make sure it's set " +
              "and try again.")
        exit(1)

    # do requesting, write to output file
    convos = []
    for convo in prompt_matrix(args.m, args.passwd_file):
        pprint(convo)
        convos.append(convo)

    with open(args.o, 'w') as f:
        json.dump(convos, f, indent=2)

if __name__ == '__main__':
    main()
