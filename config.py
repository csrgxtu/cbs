# -*- coding: utf8 -*-
from typing import List
import logging, coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

regions = ['nl', 'us', 'tw', 'uk', 'os', 'ty', 'hk', 'de', 'au', 'ee']