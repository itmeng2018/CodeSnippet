#!/usr/bin/env python
# -*- coding: utf-8 –*-
import requests
import json
import sys

word = ' '.join(sys.argv[1:])

req_url = "http://fanyi.youdao.com/translate"

form_data = {}
form_data['i'] = word
form_data['doctype'] = 'json'

res = json.loads(requests.post(req_url, data=form_data).text)['translateResult'][0][0]['tgt']

'''
{"type":"EN2ZH_CN","errorCode":0,"elapsedTime":0,"translateResult":[[{"src":
    "python is best","tgt":"python是最好的"}]]}
'''
print('✨'*len(word))
print('原文: ', word)
print('✨'*len(word))
print('译文: ', res)
print('✨'*len(word))


