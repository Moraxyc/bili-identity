import random
import string


def generate_code(length: int = 6) -> str:
    """
    生成指定长度的数字验证码。

    :param length: 验证码的长度，默认为 6
    :type length: int
    :return: 由数字组成的随机验证码字符串
    :rtype: str
    """
    return "".join(random.choices(string.digits, k=length))
