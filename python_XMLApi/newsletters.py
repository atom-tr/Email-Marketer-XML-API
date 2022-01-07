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


# Import the required library
from lxml import html, etree
from requests.models import Response
from .XMLApi import *

class Newsletters_API(API):
    
    def GetLiveNewsletters(self, ownerid: int = 0, newsletterids: int = None) -> dict:
        """Get all live newsletters

        Args:
            ownerid (int, optional): [description]. Defaults to 0.
            newsletterids (list, optional): [description]. Defaults to [].
        Return:
            Returns an list with the newsletters in it
            { 'issuccess': True, 'data': [
                {'newsletterid': '1194', 'name': 'Copy of demo', 'subject': 'hello'}, 
                ...
                ]
            }
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
    
    def Delete(self, newsletterid: int = 0, userid: int = 0) -> bool:
        """Delete a Campaign

        Args:
            newsletterid (int, optional): Campaign ID to delete. Defaults to 0.
            userid (int, optional): User ID who campaign belongs to. Defaults to 0.
        Return:
            Returns True if success
        """
        details = f'''<newsletterid>{newsletterid}</newsletterid>'''
        if userid: details += f'''<userid>{userid}</userid>'''
        xml = self.xml_format('newsletters', 'Delete', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            return True if self.issuccess(e) else False
        return response.raise_for_status()
    
    def Copy(self, oldid: int = 0) -> bool:
        """Copy a Campaign

        Args:
            oldid (int, optional): Campaign ID to copy. Defaults to 0.
        Return:
            Returns True if success
        """
        details = f'''<oldid>{oldid}</oldid>'''
        xml = self.xml_format('newsletters', 'Copy', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            return True if self.issuccess(e) else False
        return response.raise_for_status()
    
    def GetLastSent(self, newsletterid: int = 0) -> dict:
        """Get the last sent date

        Args:
            newsletterid (int, optional): Campaign ID to get the last sent date. Defaults to 0.
        Return:
            Returns an list with the newsletters in it
            {
                'issuccess': True, 
                'data': {
                    'jobid': '152496', 'starttime': '1640169005', 'total_recipients': '1', 'sendsize': '1', 'finishtime': '1640169011'
                }
            }
        """
        details = f'''<newsletterid>{newsletterid}</newsletterid>'''
        xml = self.xml_format('newsletters', 'GetLastSent', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                for d in self.Xmlstring2ListConfig(response.text):
                    if isinstance(d, dict): return { 'issuccess': True, 'data': d }
            else: return self.iserror(e)
        return response.raise_for_status()
    
class Campaign(Newsletters_API):
    
        campaignid = None
        def setup(self, **kwargs):
            self.ownerid = kwargs.get('ownerid', self.get_userid())
            self.name = kwargs.get('name', '')
            self.subject = kwargs.get('subject', '')
            self.textbody = kwargs.get('textbody', '')
            self.htmlbody = kwargs.get('htmlbody', '')
            self.active = kwargs.get('active', 1)
            self.archive = kwargs.get('archive', 1)
            self.format = kwargs.get('format', 'h')
            
        def set_owner(self, ownerid: int): self.ownerid = ownerid
        def set_name(self, name: str): self.name = name
        def set_subject(self, subject: str): self.subject = subject
        def set_textbody(self, textbody: str): self.textbody = textbody
        def set_htmlbody(self, htmlbody: str ): self.htmlbody = htmlbody
        
        def create(self):
            
            details = f'''
            <ownerid>{self.ownerid}</ownerid>
            <name>{self.name}</name>
            <format>{self.format}</format>
            <active>{self.active}</active>
            <archive>{self.archive}</archive>
            <subject>{self.subject}</subject>
            '''
            if not any([self.textbody, self.htmlbody]): return { 'issuccess': False, 'message': 'No body' }
            
            if self.textbody: details += f'''<textbody><![CDATA[{self.textbody}]]></textbody>'''
            if self.htmlbody: details += '''<htmlbody><![CDATA[{}]]></htmlbody>'''.format(self.htmlbody.encode('ascii', 'xmlcharrefreplace').decode("utf-8") )
            xml = self.xml_format('newsletters', 'Create', details)
            # return xml
            response = requests.post(self.url, data=xml)
            if response.status_code == 200:
                e = ET.fromstring(response.text)
                if self.issuccess(e):
                    self.campaignid = e.find('data').text
                    return { 'issuccess': True, 'data': self.campaignid}
                else: return self.iserror(e)
            return response.raise_for_status()
        
        def send(self, fktype = 'newsletter', fkid: int = campaignid, lists: int = 0, when = 0):
            
            details = f'''
            <jobtype>send</jobtype>
            <when>{when}</when>
            <ownerid>{self.ownerid}</ownerid>
            <fktype>{fktype}</fktype>
            <fkid>{fkid}</fkid>
            <lists>{lists}</lists>
            '''
            xml = self.xml_format('jobs', 'Create', details)
            response = requests.post(self.url, data=xml)
            if response.status_code == 200:
                e = ET.fromstring(response.text)
                if self.issuccess(e):
                    jobid = e.find('data').text
                    return { 'issuccess': True, 'data': jobid }
                else: return self.iserror(e)
            return response.raise_for_status()