import os
import random

from PIL import Image, ImageDraw, ImageFont

from day09 import settings


class VerifyCode(object):
    '''验证码类'''

    def __init__(self, width=100, height=40, len=4):
        '''
        系统初始化
        :param width: 验证码图片宽度
        :param height: 验证码图片高度
        :param len: 验证码长度
        '''
        self.width = width if width > 50 else 100
        self.height = height if height > 30 else 40
        self.len = len if len >= 4 else 4
        self.__code = None  # 验证码字符串
        self.__pen = None  # 画笔

    def output(self):
        '''
        输出验证码
        :return: 验证码图片的二进制流
        '''

        # 1. 创建画布
        img = Image.new('RGB', (self.width, self.height), self.__randColor(120, 200))
        self.__pen = ImageDraw.Draw(img)  # 产生画笔

        # 2. 产生验证码字符串
        self.__randword()

        # 3. 画验证码
        self.__drawCode()

        # 4. 画干扰点
        self.__drawPoint()

        # 5. 画干扰线
        self.__drawLine()

        # 6. 返回图片
        img.save('vc.png', 'PNG')

    def __randColor(self, low, high):
        return random.randint(low, high), random.randint(low, high), random.randint(low, high)

    def __generateCode(self):
        '''
        产生纯数字验证码
        '''
        minNumber = 10 ** (self.len - 1)
        maxNumber = 10 ** self.len - 1
        verify_code = str(random.randint(minNumber, maxNumber))
        self.__code = verify_code

    def __randword(self):
        '''
        产生随机验证码 (A-Z,a-z,0-9) * self.len
        '''
        verify_code = ''
        for i in range(self.len):
            z = random.randint(0, 2)
            if z == 0:  # A-Z
                verify_code += chr(random.randint(65, 90))
            elif z == 1:  # a-z
                verify_code += chr(random.randint(97, 122))
            else:  # 0-9
                verify_code += str(random.randint(0, 9))
        self.__code = verify_code

    def __drawCode(self):
        '''
        画验证码
        '''
        path = os.path.join(settings.STATICFILES_DIRS[0], 'font/SIMKAI.TTF')
        # print(path)    # test
        font1 = ImageFont.truetype(font=path, size=20, encoding='utf-8')
        # print(font1)   # test
        for i in range(self.len):
            width = (self.width - 20) / 4  # 计算一个字符的宽度
            x = 10 + i * width + width / 4  # x 坐标
            y = random.randint(2, self.height - 20)
            self.__pen.text((x, y), self.__code[i], font=font1, fill=self.__randColor(0, 100))

    def __drawPoint(self):
        '''
        画干扰点
        '''
        for i in range(300):
            x = random.randint(1, self.width - 1)
            y = random.randint(1, self.height - 1)
            self.__pen.point((x, y), fill=self.__randColor(70, 190))

    def __drawLine(self):
        '''
        画干扰线
        '''
        for i in range(6):
            start = random.randint(1, self.width - 1), random.randint(1, self.height - 1)
            end = random.randint(1, self.width - 1), random.randint(1, self.height - 1)
            self.__pen.line([start, end], fill=self.__randColor(122, 222))


if __name__ == '__main__':
    vc = VerifyCode()
    vc.output()
