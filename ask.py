#!/usr/bin/env python

from os import getenv
import requests

ENDPOINT = 'https://api.openai.com/v1/chat/completions'
MODEL = 'gpt-3.5-turbo'

def messager(role):
    return lambda msg: { 'role': role, 'content': msg }

def ask(api_key, prompt, system_msg=None):
    if system_msg is None:
        system_msg = "You are a helpful AI assistant."

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
            'Authorization': f"Bearer {api_key}" if api_key else ""
        },
    ).json()

def main():
    # read api key from env variable
    api_key = getenv("OPENAI_API_KEY")
    if api_key is None:
        print("couldn't read 'OPENAI_API_KEY' from env, make sure it's set " +
              "and try again.")
        exit(1)

    # get prompt
    print("what's your prompt?")
    prompt = input("> ")

    # ask model
    res = ask(api_key, prompt)
    
    if 'error' in res:
        print(f"openai error: {res['error']['message']}")
        exit(1)
    
    print(res)

if __name__ == '__main__':
    main()