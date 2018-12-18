# -*- coding:utf-8 -*-
from random import randint

import requests
from retrying import retry


class Headers:
    def __init__(self):
        self.windows = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3610.2 Safari/537.36"}
        self.ios = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
        self.android = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3610.2 Mobile Safari/537.36"}
        self.mac = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3610.2 Safari/537.36"}
        self.default = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"}

    def get_headers(self, headers_type):
        headers_all = {
            'default': self.default,
            'windows': self.windows,
            'mac': self.mac,
            'android': self.android,
            'ios': self.ios
        }
        if headers_type != 'random':
            headers = headers_all.get(headers_type)
        else:
            headers = list(headers_all.values())[randint(0, 4)]
        return headers


@retry(stop_max_attempt_number=3)
def _parse_url(url_info, method, data, headers_type):
    headers = Headers().get_headers(headers_type)
    if method == 'POST':
        response = requests.post(url_info, data=data, headers=headers)
    else:
        response = requests.get(url_info, headers=headers, timeout=3)
    assert response.status_code == 200
    return response.content.decode()


def parse_url(url_info, method='GET', data=None, headers_type='default'):
    try:
        result = _parse_url(url_info, method, data, headers_type)
    except Exception:
        result = None

    return result


if __name__ == '__main__':
    url = 'http://www.baidu.com'
    res = parse_url(url, headers_type='random')
    print(len(res))
