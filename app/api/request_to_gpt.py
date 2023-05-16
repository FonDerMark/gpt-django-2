import codecs
from gpt4free import Provider, quora
import gpt4free
from os import environ as env



def request_to_gpt(question, mode):
    response = ''
    count = 10
    while response == '' and count > 0:
        response = {
            'you': lambda: gpt4free.Completion.create(Provider.You, prompt=question).encode().decode('unicode_escape'),
            'poe': lambda: gpt4free.Completion.create(Provider.Poe, prompt=question,
                                                      token=quora.Account.create(logging=False), model='ChatGPT'),
            'forefront': lambda: gpt4free.Completion.create(Provider.ForeFront, prompt=question, model='gpt-4',
                                                            token=quora.Account.create(logging=False)),
            'theb': lambda: gpt4free.Completion.create(Provider.Theb, prompt=question),
        }.get(mode)()
        count -= 1
    if response == '':
        return 'Service overloaded, try later'
    else:
        return response
