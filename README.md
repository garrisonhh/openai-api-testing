# openai api with requests lib

## how do I use your stupid code

written in python 3.11 with the requests library. if you use nix, this includes a nix flake to ensure version parity.

```bash
# this key must be in your env.
export OPENAI_API_KEY="<your openai api key>"

python ask.py [passwd_list.txt] -o [output.json] -m [matrix.json]
```

example matrix file:
```json
{
    "system": [
        "This is a system prompt.",
        "You are a helpful AI assistant."
    ],
    "prompts": [
        "What is up, ChatGPT? Tell me about these passwords: PASSWORDS",
        "The 'PASSWORDS' token will be replaced in each prompt with some number of your passwords.",
        "All of these prompts will be run in combination with each system prompt."
    ]
}
```

once you have your json output, you can open viewer.html in your browser to see the contents of the file in a relatively reader-friendly way.
