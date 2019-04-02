#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Blueprint

usr = Blueprint(
    'usr',
    __name__,
    template_folder='templates',
    static_folder='static'
)
from . import views