import json
from app.core.config import settings


def translate_column_name(terms: list, api_source: str = 'ak') -> list:
    """
    将中文列名转换为统一的英文列名，
    :param terms: 待转换的中文列名列表
    :return: 转换后的英文列名列表
    """
    if api_source not in ['ak', 'ts']:
        raise ValueError("api_source must be either 'ak' or 'ts'")
    with open(str(settings.STATIC_DIR) + '/column_name_map.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    result = []
    for term in terms:
        if term in translations[api_source + '_column']:
            result.append(translations[api_source + '_column'][term])
        else:
            result.append(term)
    return result


def translate_term_zh2iden(term) -> str:
    """实现股票术语中英文的翻译功能，对系统进行统一

    术语参考：
    1.https://wiki.mbalib.com/wiki/%E8%82%A1%E7%A5%A8%E6%9C%AF%E8%AF%AD%E8%8B%B1%E6%B1%89%E5%AF%B9%E7%85%A7%E8%A1%A8
    2.https://www.cnblogs.com/interdrp/p/17064304.html
    3.https://www.lse.ac.uk/cibl/assets/documents/resources/sentence-of-the-week/%E8%82%A1%E7%A5%A8%E6%9C%AF%E8%AF%AD.pdf
    4.https://zhuanlan.zhihu.com/p/137858515

    对股票术语、常用语等词语的中文、英文以及其标识符进行相互转换
    Attributes:
        translations: dict， 读取json文件获利词语dict
            每个词语的表示如下：
            词语标识符[identifier]: {
                'zh': '', # 中文
                'en': '', # 英语
            }
            词语标识符唯一，其中文、英文可能存在多个，以','进行分割
            标识符用于建表字段等，在项目中保持一致

    将中文[zh]转换为标识符[identifier]，
    由于zh可以包含多个词语，需要用正则表达式或分割再匹配

    :param term: 待转换的中文词语数组
    :return: 转换后的词语标识符
    """
    with open(str(settings.STATIC_DIR) + '/stock_terms.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    for iden in translations.keys():
        zhs = set(translations[iden]['zh'].split(','))
        if term in zhs:
            return iden
    return term
