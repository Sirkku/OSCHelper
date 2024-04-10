import re


def contains_chinese(text):
    if text:
        return re.search(u"[\u4e00-\u9fff]", text)
    return False
