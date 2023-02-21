# -*- coding: utf-8 -*-

import json
import os
from newdao.res import *


class UserHistory:
    MAX_LATEST_LEN = 100
    MAX_CACHE_LEN = 10000
    MAX_COUNT_LEN = 50000
    content = {}
    conf = {}
    latest_word = []
    DICT_FILE_NAME = usr_word_path
    LATEST_FILE_NAME = latest_txt_path
    ONLINE_CACHE = online_cache_path
    NOTE_NAME = notebook_path
    CONF_NAME = conf_json_path

    def __init__(self):
        # Create empty file
        if not os.path.exists(self.DICT_FILE_NAME):
            with open(self.DICT_FILE_NAME, 'w+', encoding='utf-8') as f:
                tmp_dict = {}
                json.dump(tmp_dict, f)
        if not os.path.exists(self.LATEST_FILE_NAME):
            open(self.LATEST_FILE_NAME, 'w+', encoding='utf-8').close()
        if not os.path.exists(self.ONLINE_CACHE):
            with open(self.ONLINE_CACHE, 'w+', encoding='utf-8') as f:
                json.dump({}, f)
        if not os.path.exists(self.CONF_NAME):
            with open(self.CONF_NAME, 'w+', encoding='utf-8') as f:
                json.dump({"short": False, "save": True}, f)

        # Load file
        with open(self.LATEST_FILE_NAME, 'r', encoding='utf-8') as f:
            self.latest_word = [v.strip() for v in f.readlines()]
        with open(self.ONLINE_CACHE, 'r', encoding='utf-8') as f:
            self.cache_dic = json.load(f)
        with open(self.DICT_FILE_NAME, 'r', encoding='utf-8') as f:
            self.word_co_map = json.load(f)
        with open(self.CONF_NAME, 'r', encoding='utf-8') as f:
            self.conf = json.load(f)
    # save conf

    def save_conf(self, conf):
        if 'short' in conf and 'save' in conf:
            with open(self.CONF_NAME, 'w+') as f:
                    json.dump(conf, f)

    # add item to history
    def add_item(self, word_info):
        word = word_info['word']
        # Update word dict
        if word in self.word_co_map:
            self.word_co_map[word] += 1
        else:
            self.word_co_map[word] = 1
        with open(self.DICT_FILE_NAME, 'w', encoding='utf-8') as f:
            # too much usr word
            if len(self.word_co_map) <= self.MAX_COUNT_LEN:
                json.dump(self.word_co_map, f, indent=4)
        # Update latest word list
        if len(self.latest_word) < self.MAX_LATEST_LEN:
            self.latest_word.append(word)
        else:
            self.latest_word.pop(0)
            self.latest_word.append(word)
        with open(self.LATEST_FILE_NAME, 'w', encoding='utf-8') as f:
            for v in self.latest_word:
                f.write(v + '\n')


    # add word info to online cache
    def add_word_info(self, word_info):
        # too much usr word
        if len(self.cache_dic) > self.MAX_CACHE_LEN:
            # remove
            self.cache_dic = {}
            os.remove(self.ONLINE_CACHE)
        with open(self.ONLINE_CACHE, 'w', encoding='utf-8') as f:
            self.cache_dic[word_info['word'].lower()] = word_info
            json.dump(self.cache_dic, f)

    # get word info from online cache
    def get_word_info(self, word):
        if word.lower() in self.cache_dic:
            return self.cache_dic[word.lower()]
        else:
            return None
    # save word to notebook

    def save_note(self, word_struct, notename='notebook'):
        if word_struct['word'] in self.latest_word:
            return
        else:
            with open(res_folder_path + notename + '.txt', 'a+', encoding='utf-8') as f:
                space1 = ' '*(20 - len(word_struct['word'])) + ' '
                pn = ''
                if '' in word_struct['pronunciation']:
                    pn = word_struct['pronunciation']['']
                elif '美' in word_struct['pronunciation']:
                    pn = word_struct['pronunciation']['美']
                space2 = ' '*(20 - len(pn)) + ' '
                ph = ' '.join(word_struct['paraphrase']).replace('\n', ' ')
                f.write(word_struct['word'] + space1 + pn + space2 + ph + '\n')
