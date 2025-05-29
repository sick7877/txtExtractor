#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) ACE 

import os

class Config(object):
    # get a token from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7521656101:AAHTd7x6z2A_9JuzmE13vgbpLd5w81pfeW8")
    API_ID = int(os.environ.get("API_ID", "29375864"))
    API_HASH = os.environ.get("API_HASH", "a0253a0c0e2abf04e54e035d7a855afd)
    AUTH_USERS = os.environ.get("AUTH_USERS", "7624302999")
