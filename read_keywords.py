#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extract all keywords from a excel file."""

import re
import unicodedata
import pandas as pd


def strip_accents(text):
    """Quit accent of vowels."""
    try:
        text = unicode(text, 'utf-8')
    except NameError:  # unicode is a default on python 3
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii',
                                                     'ignore').decode("utf-8")
    return str(text)


def extract_keywords(excel_pathfile, columns):
    """Extract all keywords in lowercase, without: accents, special characters, extra spaces."""
    data_frame = pd.read_excel(excel_pathfile)
    keyword_list = []
    for i in range(columns):
        keyword_list += data_frame.iloc[:, i].dropna().values.tolist()
    keywords_set = set()
    for i, keyword in enumerate(keyword_list):
        keyword = str(keyword)
        if keyword != '':
            keyword = keyword.lower().replace('ñ', 'yn')
            keyword = strip_accents(keyword)
            keyword = re.sub(r"[^a-zA-Z0-9]+", ' ', keyword).strip()
            keyword = keyword.lower().replace('yn', 'ñ')
            keywords_set.add(keyword)
    return list(keywords_set)


def main():
    """Extract all keywords from a excel file."""
    keywords_list = extract_keywords('keywords_revised.xlsx', 4)
    print(len(keywords_list))


if __name__ == '__main__':
    main()
