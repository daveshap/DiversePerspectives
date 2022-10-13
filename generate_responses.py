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


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=1)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def gpt3_completion(prompt, engine='text-davinci-002', temp=1.2, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
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


if __name__ == '__main__':
    files = os.listdir('stories/')
    topic = "There is a proposed bill in my country that would ban all abortions under all circumstances."
    for file in files:
        story = open_file('stories/%s' %file)
        # get feelings
        prompt = open_file('prompt_topic_feeling.txt').replace('<<PROFILE>>', story).replace('<<TOPIC>>', topic)
        feelings = gpt3_completion(prompt)
        print('\n\n', feelings)
        # get concerns
        prompt = open_file('prompt_topic_concrete.txt').replace('<<PROFILE>>', story).replace('<<TOPIC>>', topic)
        concerns = gpt3_completion(prompt)
        print('\n\n', concerns)
        # get compromises
        prompt = open_file('prompt_topic_concrete.txt').replace('<<PROFILE>>', story).replace('<<TOPIC>>', topic)
        compromises = gpt3_completion(prompt)
        print('\n\n', compromises)
        # check if worldview already exists
        filename = file.replace('.txt','.json')
        if os.path.exists('worldviews/%s' % filename):
            worldview = load_json('worldviews/%s' % filename)
        else:
            worldview = {'story': story, 'worldview': list()}
        # save results
        info = {'topic': topic, 'time': time(), 'feelings': feelings, 'concerns': concerns, 'compromises': compromises}
        worldview['worldview'].append(info)
        save_json('worldviews/%s' % filename, worldview)