#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# This has the Base API class in it.
# Sets up the database object for use.
# API base on iem v6.2.0

@package API
@subpackage Stats_API

@author: thai.tv (thai.tv@netnam.vn)
@email: sys-sgn@netnam.vn
@status: InProgress
@link: https://github.com/atom-tr/Email-Marketer-XML-API
"""

from .XMLApi import *

class Stats_API(API):
    
    def GetUserNewsletterStats(self, userid: int = 0) -> dict:
        """[summary]

        Args:
            userid (int, optional): The userid to get the statistics for. Defaults to 0.
        Return:
            Array Returns an array with the statistics in it
        """
        details = f'''<userid>{userid}</userid>'''
        xml = self.xml_format('stats', 'GetUserNewsletterStats', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                for d in self.Xmlstring2ListConfig(response.text):
                    if isinstance(d, dict): return { 'issuccess': True, 'data': d }
            else: return self.iserror(e)
        return response.raise_for_status()
    
  