#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) ACE 

import os

class Config(object):
    # get a token from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8190086252:AAHkseLMEdl_Hxaoz38C9vQaGujXqIpHVoY")
    API_ID = int(os.environ.get("API_ID", "28712726"))
    API_HASH = os.environ.get("API_HASH", "06acfd441f9c3402ccdb1945e8e2a93b")
    AUTH_USERS = os.environ.get("AUTH_USERS", "1003575883")
