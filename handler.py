# -*- coding: utf-8 -*-
import json
from sentences_sim import *

def spell_check(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }
    text=json.dumps(body,ensure_ascii=False).encode('utf8')
    text=text.decode()
    ubi=text.find('text')
    original=text[ubi+8:]
    original=original[:original.find("'")]
    ls=original.split(',')
    options=[w for w in ls[:-1]]
    answer=ls[-1]
    output=bestChoice(options,answer)
    response = {
        "statusCode": 200,
        "body": '{"text" : "'+output+'" }'
    }
    return response





