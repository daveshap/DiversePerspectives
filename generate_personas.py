import re
import os
import json
import openai
from uuid import uuid4
from time import time, sleep
from random import seed, choice, randint


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


openai.api_key = open_file('openaiapikey.txt')


def pick_random(filename):
    lines = open_file(filename).splitlines()
    return choice(lines)


def save_json(payload):
    filename = 'personas/%s.json' % str(uuid4())
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=1)


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            #text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            if not os.path.exists('gpt3_logs'):
                os.makedirs('gpt3_logs')
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def generate_dossier():
    # populate key demographics
    files = [i for i in os.listdir() if 'trait_' in i]
    profile = ''
    dossier = dict()
    for file in files:
        trait = pick_random(file)
        label = file.replace('trait_','').replace('.txt','')
        profile += '%s: %s\n' % (label, trait)
        dossier[label] = trait
    # populate scalars
    profile += '\nPersonality Traits: (1 to 10)\n'
    scalars = open_file('scalars.txt').splitlines()
    for scalar in scalars:
        value = randint(1, 10)
        profile += '%s: %s\n' % (scalar, value)
        dossier[scalar] = value
    #print(profile)
    #print(dossier)
    #save_json(dossier)
    return profile, dossier

if __name__ == '__main__':
    seed()
    for i in list(range(0,500)):
        profile, dossier = generate_dossier()
        print(profile)
        save_json(dossier)