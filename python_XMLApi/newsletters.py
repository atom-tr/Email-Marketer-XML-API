#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# The Newsletter API.
# Sets up the database object for use.
# API base on iem v6.2.0

@package API
@subpackage Newsletters_API

@author: thai.tv (thai.tv@netnam.vn)
@email: sys-sgn@netnam.vn
@status: InProgress
@link: https://github.com/atom-tr/Email-Marketer-XML-API
"""

from .XMLApi import *

class Newsletters_API(API):
    
    def GetLiveNewsletters(self, ownerid: int = 0, newsletterids: int = None) -> dict:
        """[summary]

        Args:
            ownerid (int, optional): [description]. Defaults to 0.
            newsletterids (list, optional): [description]. Defaults to [].
        Return:
            Array Returns an array with the newsletters in it
        """
        details = f'''<ownerid>{ownerid}</ownerid>'''
        if newsletterids: details += f'''<newsletterids><items>{newsletterids}</items></newsletterids>'''
        xml = self.xml_format('newsletters', 'GetLiveNewsletters', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                for d in self.Xmlstring2ListConfig(response.text):
                    if isinstance(d, list): return { 'issuccess': True, 'data': d }
            else: return self.iserror(e)
        return response.raise_for_status()