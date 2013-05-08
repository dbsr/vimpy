# -*- coding: utf-8 -*-
# dydrmntion@gmail.com ~ 2013

import logging
import os


def init_log():
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)

    lpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'impy.debug')

    fh = logging.FileHandler(lpath)

    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    logger.debug('Initiated debug log.')
