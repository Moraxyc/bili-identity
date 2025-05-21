import re


def extract_code_from_message(message: str, length: int = 32) -> str | None:
    """
    从用户消息中提取出可能的验证码。

    :param message: 用户发送的消息内容
    :param length: 验证码的长度
    :return: 提取出的验证码字符串，如果未找到则返回 None
    """
    pattern = rf"\b[a-zA-Z0-9]{{{length}}}\b"
    match = re.search(pattern, message)
    if match:
        return match.group(0)
    return None
