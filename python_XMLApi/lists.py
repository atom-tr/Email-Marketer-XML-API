#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# This has the Base API class in it.
# Sets up the database object for use.
# API base on iem v6.2.0

@package API
@subpackage List_API

@author: thai.tv (thai.tv@netnam.vn)
@email: sys-sgn@netnam.vn
@status: InProgress
@link: https://github.com/atom-tr/Email-Marketer-XML-API
"""

from .XMLApi import *

class List_API(API):
    # List
    def get_lists(self) -> dict:
        xml = self.xml_format('user', 'GetLists')
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                data = XmlListConfig(ElementTree.fromstring(response.text))
                for d in data:
                    if isinstance(d, list): return { 'issuccess': True, 'data': d }
            else: return self.iserror(e)
        return response.raise_for_status()
        
    def get_customfields(self, list_id: int) -> dict:
        """Get all custom fields for a list

        Args:
            list_id (int): id of list to get custom fields for

        Returns:
            CustomFields (List): List of custom fields
        """
        details = f'''<listids>{list_id}</listids>'''
        xml = self.xml_format('lists', 'GetCustomFields', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                for d in self.Xmlstring2ListConfig(response.text):
                    if isinstance(d, list): return { 'issuccess': True, 'data': d }
            else: return self.iserror(e)
        return response.raise_for_status()
    
    