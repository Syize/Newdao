#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from newdao.res import *


class Confer:
    CONF_FILE = res_folder_path + 'config.json'

    def __init__(self):
        # Create empty file
        if not os.path.exists(self.CONF_FILE):
            with open(self.CONF_FILE, 'w+') as f:
                tmp_dict = {}
                json.dump(tmp_dict, f)

    def flush_conf(self, conf_json):
        pass
