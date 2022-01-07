#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# This has the Base API class in it.
# Sets up the database object for use.
# API base on iem v6.2.0

@author: thai.tv (thai.tv@netnam.vn)
@email: sys-sgn@netnam.vn
@status: InProgress
@link: https://github.com/atom-tr/Email-Marketer-XML-API
"""

import requests

import xml.etree.cElementTree as ElementTree
import xml.etree.ElementTree as ET
# from pprint import pprint

# from requests.models import Response

class IntersectException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)
                    
class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})
                
class API():
    def __init__(self, url: str, username: str, usertoken: str):
        self.url = url
        self.user = username
        self.token = usertoken
    
    def __str__(self) -> str:
        pass
    
    def get_url(self): return self.url
    
    def issuccess(self, e): return True if e.find('status').text == 'SUCCESS' else False

    def iserror(self, e):
        return { 'issuccess': False, 'status': e.find('status').text, 'message': e.find('errormessage').text }
    
    def email_format(f): return { 'h': 'HTML', 't': 'Text', 'b': 'TextAndHTML'}[f]
    
    def xml_format(self, type, method, data = ""):
        xml = '''
        <xmlrequest>
            <username>{}</username>
            <usertoken>{}</usertoken>
            <requesttype>{}</requesttype>
            <requestmethod>{}</requestmethod>
            <details>
                {}
            </details>
        </xmlrequest>
        '''
        return xml.format(self.user, self.token, type, method, data)
    
    def Xmlstring2ListConfig(self, str): return XmlListConfig(ElementTree.fromstring(str))
    
    def is_authenticated(self): 
        """
        Check if user is authenticated
        """
        response = requests.post(self.url, data=self.xml_format('authentication', 'xmlapitest'))
        if response.status_code == 200:
            if response.text.find('<status>SUCCESS</status>') != -1: return True
            else: return False
        else: return response.raise_for_status()
    
    def get_userid(self) -> int:
        """Get current user id

        Returns:
            int: id of current user
        """
        response = requests.post(self.url, data=self.xml_format('authentication', 'xmlapitest'))
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e): 
                for i in self.Xmlstring2ListConfig(response.text):
                    if isinstance(i, dict): return i['user']['userid']
            else: return self.iserror(e)
        else: return response.raise_for_status()
    
    