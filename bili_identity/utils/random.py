import random
import secrets
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


def generate_secret(length: int = 32) -> str:
    """
    生成一个由字母和数字组成的随机字符串，用于被动验证

    :param length: 要生成的字符串长度，默认为 32。
    :type length: int
    :return: 随机生成的字符串。
    :rtype: str
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
