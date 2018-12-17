#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import json
import requests

class Dict:
	def __init__(self, word):
		self.word = word
		self.lang_detect_url = 'https://fanyi.baidu.com/langdetect'
		self.translate_url = 'https://fanyi.baidu.com/basetrans'
		self.headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36"}

	def parse_url(self, url, data):
		# 发送post请求
		response = requests.post(url=url, data=data, headers=self.headers)
		# 返回字典
		return json.loads(response.content.decode())

	def ZhaoMengLi(self, language):
		# 让赵梦丽识别语言，返回数据包
		tolanguage = 'zh' if language == 'en' else 'en'
		data = {'query': self.word, 'from': language, 'to': tolanguage}
		return data

	def run(self):
		lang_detect_data = {'query': self.word}
		language = self.parse_url(self.lang_detect_url, lang_detect_data)
		data = self.ZhaoMengLi(language.get('lan'))
		result = self.parse_url(self.translate_url, data)
		print('----'*len(self.word))
		print('原文: ', self.word)
		print('----'*len(self.word))
		print('译文：', result['trans'][0]['dst'])
		print('----'*len(self.word))

def main():
	word = ' '.join(sys.argv[1:])
	trans = Dict(word)
	trans.run()


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print('参数错误')
