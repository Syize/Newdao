#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import re

tag_re = re.compile('^[a-z0-9]+$')

attribselect_re = re.compile(
    r'^(?P<tag>\w+)?\[(?P<attribute>[\w-]+)(?P<operator>[=~\|\^\$\*]?)' +
    r'=?"?(?P<value>[^\]"]*)"?\]$'
)

# /^(\w+)\[([\w-]+)([=~\|\^\$\*]?)=?"?([^\]"]*)"?\]$/
#   \---/  \---/\-------------/    \-------/
#     |      |         |               |
#     |      |         |           The value
#     |      |    ~,|,^,$,* or =
#     |   Attribute
#    Tag

def attribute_checker(operator, attribute, value=''):
    """
    Takes an operator, attribute and optional value; returns a function that
    will return True for elements that match that combination.
    """
    return {
        '=': lambda el: el.get(attribute) == value,
        # attribute includes value as one of a set of space separated tokens
        '~': lambda el: value in el.get(attribute, '').split(),
        # attribute starts with value
        '^': lambda el: el.get(attribute, '').startswith(value),
        # attribute ends with value
        '$': lambda el: el.get(attribute, '').endswith(value),
        # attribute contains value
        '*': lambda el: value in el.get(attribute, ''),
        # attribute is either exactly value or starts with value-
        '|': lambda el: el.get(attribute, '') == value \
            or el.get(attribute, '').startswith('%s-' % value),
    }.get(operator, lambda el: el.has_key(attribute))


def ss(soup, selector):
    """
    soup should be a BeautifulSoup instance; selector is a CSS selector
    specifying the elements you want to retrieve.
    """
    tokens = selector.split()
    current_context = [soup]
    for index, token in enumerate(tokens):
        if tokens[index - 1] == '>':
            # already found direct descendants in last step
            continue

        m = attribselect_re.match(token)
        if m:
            # Attribute selector
            tag, attribute, operator, value = m.groups()
            if not tag:
                tag = True
            checker = attribute_checker(operator, attribute, value)
            found = []
            for context in current_context:
                found.extend([el for el in context.findAll(tag) if checker(el)])
            current_context = found
            continue

        if '#' in token:
            # ID selector
            tag, id = token.split('#', 1)
            if not tag:
                tag = True
            el = current_context[0].find(tag, {'id': id})
            if not el:
                return [] # No match
            current_context = [el]
            continue

        if '.' in token:
            # Class selector
            tag, klass = token.split('.', 1)
            if not tag:
                tag = True
            classes = set(klass.split('.'))
            found = []
            for context in current_context:
                found.extend(
                    context.findAll(tag,
                        {'class': lambda attr:
                             attr and classes.issubset(attr.split())}
                    )
                )
            current_context = found
            continue

        if token == '*':
            # Star selector
            found = []
            for context in current_context:
                found.extend(context.findAll(True))
            current_context = found
            continue

        if token == '>':
            # Child selector
            tag = tokens[index + 1]
            if not tag:
                tag = True

            found = []
            for context in current_context:
                found.extend(context.findAll(tag, recursive=False))
            current_context = found
            continue

        # Here we should just have a regular tag
        if not tag_re.match(token):
            return []
        found = []
        for context in current_context:
            found.extend(context.findAll(token))
        current_context = found
    return current_context

def monkeypatch(BeautifulSoupClass=None):
    """
    If you don't explicitly state the class to patch, defaults to the most
    common import location for BeautifulSoup.
    """
    if not BeautifulSoupClass:
        from BeautifulSoup import BeautifulSoup as BeautifulSoupClass
    BeautifulSoupClass.findSelect = ss

def unmonkeypatch(BeautifulSoupClass=None):
    if not BeautifulSoupClass:
        from BeautifulSoup import BeautifulSoup as BeautifulSoupClass
    delattr(BeautifulSoupClass, 'findSelect')


import bs4
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import quote


def get_html(x):
    x = quote(x)
    url = urlparse('http://dict.youdao.com/search?q=%s' % x)
    res = urlopen(url.geturl())
    xml = res.read().decode('utf-8')
    return xml


def multi_space_to_single(text):
    cursor = 0
    result = ""
    while cursor < len(text):
        if text[cursor] in ["\t", " ", "\n", "\r"]:
            while text[cursor] in ["\t", " ", "\n", "\r"]:
                cursor += 1
            result += " "
        else:
            result += text[cursor]
            cursor += 1
    return result


# get word info online
def get_text(centent, word):
    #content = get_html(word)
    word_struct = {"raw_word": word}
    root = bs4.BeautifulSoup(content, "lxml")

    for v in root.select('h2 .keyword'):
        word_struct['word'] = v.text
    
    pron = {}

    pron_fallback = False

    for pron_item in ss(root, ".pronounce"):
        pron_lang = None
        pron_phonetic = None

        for sub_item in pron_item.children:
            if isinstance(sub_item, str) and pron_lang is None:
                pron_lang = sub_item
                continue
            if isinstance(sub_item, bs4.Tag) and sub_item.name.lower() == "span" and sub_item.has_attr(
                    "class") and "phonetic" in sub_item.get("class"):
                pron_phonetic = sub_item
                continue
        if pron_phonetic is None:
            # raise SyntaxError("WHAT THE FUCK?")
            pron_fallback = True
            break
        if pron_lang is None:
            pron_lang = ""
        pron_lang = pron_lang.strip()
        pron_phonetic = pron_phonetic.text

        pron[pron_lang] = pron_phonetic

    if pron_fallback:
        for item in ss(root, ".phonetic"):
            if item.name.lower() == "span":
                pron[""] = item.text
                break

    word_struct["pronunciation"] = pron
    #
    #  <--  BASIC DESCRIPTION
    #
    nodes = ss(root, "#phrsListTab .trans-container ul")
    basic_desc = []

    if len(nodes) != 0:
        ul = nodes[0]
        for li in ul.children:
            if not (isinstance(li, bs4.Tag) and li.name.lower() == "li"):
                continue
            basic_desc.append(li.text.strip())
    word_struct["paraphrase"] = basic_desc

    if not word_struct["paraphrase"]:
        d = root.select(".wordGroup.def")
        p = root.select(".wordGroup.pos")
        ds = ""
        dp = ""
        if len(d) > 0:
            ds = d[0].text.strip()
        if len(p) > 0:
            dp = p[0].text.strip()
        word_struct["paraphrase"] = (dp + " " + ds).strip()
    #
    #  -->
    #  <--  RANK
    #
    rank = ""
    nodes = ss(root, ".rank")
    if len(nodes) != 0:
        rank = nodes[0].text.strip()
    word_struct["rank"] = rank
    #
    #  -->
    #  <-- PATTERN
    #
    # .collinsToggle .pattern
    pattern = ""

    nodes = ss(root, ".collinsToggle .pattern")
    if len(nodes) != 0:
        #    pattern = nodes[0].text.strip().replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
        pattern = multi_space_to_single(nodes[0].text.strip())
    word_struct["pattern"] = pattern
    #
    #  -->
    #  <-- VERY COMPLEX
    #
    word_struct["sentence"] = []
    for child in ss(root, ".collinsToggle .ol li"):
        p = ss(child, "p")
        if len(p) == 0:
            continue
        p = p[0]
        desc = ""
        cx = ""
        for node in p.children:
            if isinstance(node, str):
                desc += node
            elif isinstance(node, bs4.Tag) and node.name.lower() == "b" and node.children:
                for x in node.children:
                    if isinstance(x, str):
                        desc += x
            elif isinstance(node, bs4.Tag) and node.name.lower() == "span":
                cx = node.text
        desc = multi_space_to_single(desc.strip())

        examples = []

        for el in ss(child, ".exampleLists"):
            examp = []
            for p in ss(el, ".examples p"):
                examp.append(p.text.strip())
            examples.append(examp)
        word_struct["sentence"].append([desc, cx, examples])
    # 21 new year
    if not word_struct["sentence"]:
        for v in root.select("#bilingual ul li"):
            p = ss(v, "p")
            ll = []
            for p in ss(v, "p"):
                if len(p) == 0:
                    continue
                if 'class' not in p.attrs:
                    ll.append(p.text.strip())
            if len(ll) != 0:
                word_struct["sentence"].append(ll)
    #  -->
    return word_struct


def get_zh_text(word):
    content = get_html(word)
    word_struct = {"word": word}
    root = bs4.BeautifulSoup(content, "lxml")

    # pronunciation
    pron = ''
    for item in ss(root, ".phonetic"):
        if item.name.lower() == "span":
            pron = item.text
            break

    word_struct["pronunciation"] = pron

    #  <--  BASIC DESCRIPTION
    nodes = ss(root, "#phrsListTab .trans-container ul p")
    basic_desc = []

    if len(nodes) != 0:
        for li in nodes:
            basic_desc.append(li.text.strip().replace('\n', ' '))
    word_struct["paraphrase"] = basic_desc

    # DESC
    desc = []
    for child in ss(root, '#authDictTrans ul li ul li'):
        single = []
        sp = ss(child, 'span')
        if sp:
            span = sp[0].text.strip().replace(':', '')
            if span:
                single.append(span)
        ps = []
        for p in ss(child, 'p'):
            ps.append(p.text.strip())
        if ps:
            single.append(ps)
        desc.append(single)

    word_struct["desc"] = desc

    #  <-- VERY COMPLEX
    word_struct["sentence"] = []
    # 21 new year
    for v in root.select("#bilingual ul li"):
        p = ss(v, "p")
        ll = []
        for p in ss(v, "p"):
            if len(p) == 0:
                continue
            if 'class' not in p.attrs:
                ll.append(p.text.strip())
        if len(ll) != 0:
            word_struct["sentence"].append(ll)
    return word_struct


def is_alphabet(uchar):
    if (u'\u0041' <= uchar <= u'\u005a') or \
            (u'\u0061' <= uchar <= u'\u007a') or uchar == '\'':
        return True
    else:
        return False

RED_PATTERN = '\033[31m%s\033[0m'
GREEN_PATTERN = '\033[32m%s\033[0m'
BLUE_PATTERN = '\033[34m%s\033[0m'
PEP_PATTERN = '\033[36m%s\033[0m'
BROWN_PATTERN = '\033[33m%s\033[0m'


def draw_text(word, conf):

    # Word
    print(RED_PATTERN % word['word'])
    # pronunciation
    if word['pronunciation']:
        uncommit = ''
        if '???' in word['pronunciation']:
            uncommit += u'??? ' + PEP_PATTERN % word['pronunciation']['???'] + '  '
        if '???' in word['pronunciation']:
            uncommit += u'??? ' + PEP_PATTERN % word['pronunciation']['???']
        if '' in word['pronunciation']:
            uncommit = u'???/??? ' + PEP_PATTERN % word['pronunciation']['']
        print(uncommit)
    # paraphrase
    for v in word['paraphrase']:
        print(BLUE_PATTERN % v)
    # short desc
    if word['rank']:
        print(RED_PATTERN % word['rank'], end='  ')
    if word['pattern']:
        print(RED_PATTERN % word['pattern'].strip())
    # sentence
    if conf:
        count = 1
        if word['sentence']:
            print('')
            if len(word['sentence'][0]) == 2:
                collins_flag = False
            else:
                collins_flag = True
        else:
            return
        for v in word['sentence']:
            if collins_flag:
                # collins dict
                if len(v) != 3:
                    continue
                if v[1] == '' or len(v[2]) == 0:
                    continue
                if v[1].startswith('['):
                    print(str(count) + '. ' + GREEN_PATTERN % (v[1]), end=' ')
                else:
                    print(str(count) + '. ' + GREEN_PATTERN % ('[' + v[1] + ']'), end=' ')
                print(v[0])
                for sv in v[2]:
                    print(GREEN_PATTERN % u'  ???: ' + BROWN_PATTERN % (sv[0] + sv[1]))
                count += 1
                print('')
            else:
                # 21 new year dict
                if len(v) != 2:
                    continue
                print(str(count) + '. ' + GREEN_PATTERN % '[???]', end=' ')
                print(v[0], end='  ')
                print(BROWN_PATTERN % v[1])
                count += 1
    else:
        print('')


def draw_zh_text(word, conf):
    # Word
    print(RED_PATTERN % word['word'])
    # pronunciation
    if word['pronunciation']:
        print(PEP_PATTERN % word['pronunciation'])
    # paraphrase
    if word['paraphrase']:
        for v in word['paraphrase']:
            v = v.replace('  ;  ', ', ')
            print(BLUE_PATTERN % v)
    # complex
    if conf:
        # description
        count = 1
        if word["desc"]:
            print('')
            for v in word['desc']:
                if not v:
                    continue
                # sub title
                print(str(count) + '. ', end='')
                v[0] = v[0].replace(';', ',')
                print(GREEN_PATTERN % v[0])
                # sub example
                sub_count = 0
                if len(v) == 2:
                    for e in v[1]:
                        if sub_count % 2 == 0:
                            e = e.strip().replace(';', '')
                            print(BROWN_PATTERN % ('    ' + e + '    '), end='')
                        else:
                            print(e)
                        sub_count += 1
                count += 1
        # example
        if word['sentence']:
            count = 1
            print(RED_PATTERN % '\n??????:')
            for v in word['sentence']:
                if len(v) == 2:
                    print('')
                    print(str(count) + '. ' + BROWN_PATTERN % v[0] + '    ' + v[1])
                count += 1


def param_parse(param_list, word):
    if 'h' in param_list or '-help' in param_list:
        print('Usage: wd [OPTION]... [WORD]')
        print('Youdao is wudao, A powerful dict.')
        print('-h, --help                   display this help and exit')
        print('-s, --short-desc             show description without the sentence')
        exit(0)
    # short conf
    if 's' in param_list or '-short-desc' in param_list:
        conf = False
    else:
        conf = True
    if not word:
        print('Usage: wdd [OPTION]... [WORD]')
        exit(0)
    return conf

import sys

if __name__ == '__main__':
    word = ''
    param_list = []
    for v in sys.argv[1:]:
        if v.startswith('-'):
            param_list.append(v[1:])
        else:
            word += ' ' + v
    word = word.strip()
    conf = param_parse(param_list, word)
    xml = get_html(word)
    if is_alphabet(word):
        info = get_text(word)
        draw_text(info, conf)
    else:
        info = get_zh_text(word)
        draw_zh_text(info, conf)

