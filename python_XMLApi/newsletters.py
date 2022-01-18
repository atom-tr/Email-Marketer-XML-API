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
import time
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
    
        # Define all the variables for a campaign
        campaign = dict.fromkeys( ["campaignid", "ownerid", "name", "subject", "textbody", "htmlbody", ], None )
        campaign.update({  "active": 1, "archive": 1, "format": "h", })
        
        def setup_campaign(self, **kwargs):
            self.campaign.update(kwargs)
            self.campaign['ownerid'] = kwargs.get('ownerid', self.get_userid())
            # self.name = kwargs.get('name', '')
            # self.subject = kwargs.get('subject', '')
            # self.textbody = kwargs.get('textbody', '')
            # self.htmlbody = kwargs.get('htmlbody', '')
            # self.active = kwargs.get('active', 1)
            # self.archive = kwargs.get('archive', 1)
            # self.format = kwargs.get('format', 'h')
        
        def is_campaign_ready(self):
            """Check if the campaign is ready to be created"""
            if self.campaign['name'] and self.campaign['subject'] and self.campaign['textbody'] and self.campaign['htmlbody']:
                return True
            else: return False
            
        def create(self):
            """Create a campaign with the setup_campaign function

            Returns:
                campaignid [int]: ID of the created campaign
            """
            if not self.is_campaign_ready(): return { 'issuccess': False, 'message': 'Campaign is not ready' }
            
            # Create XML for API calling
            details = f'''
            <ownerid>{self.campaign['ownerid']}</ownerid>
            <name>{self.campaign['name']}</name>
            <format>{self.campaign['format']}</format>
            <active>{self.campaign['active']}</active>
            <archive>{self.campaign['archive']}</archive>
            <subject>{self.campaign['subject']}</subject>
            '''
            # Check if body is html or text aready set
            if not any([self.campaign['textbody'], self.campaign['htmlbody']]): return { 'issuccess': False, 'message': 'No body' }
            
            if self.campaign['textbody']: details += f'''<textbody><![CDATA[{self.campaign['textbody']}]]></textbody>'''
            if self.campaign['htmlbody']: details += '''<htmlbody><![CDATA[{}]]></htmlbody>'''.format(self.campaign['htmlbody'].encode('ascii', 'xmlcharrefreplace').decode("utf-8") )
            xml = self.xml_format('newsletters', 'Create', details)
            # return xml
            response = requests.post(self.url, data=xml)
            if response.status_code == 200:
                e = ET.fromstring(response.text)
                if self.issuccess(e):
                    self.campaign['campaignid'] = e.find('data').text
                    return { 'issuccess': True, 'data': self.campaign['campaignid']}
                else: return self.iserror(e)
            return response.raise_for_status()
        
        # define all the methods for sending a campaign
        job = dict.fromkeys( ["SendFromName", "SendFromEmail", "ReplyToEmail", "BounceEmail", ], None )
        job.update(dict.fromkeys([ "Multipart", "TrackOpens", "TrackLinks", "NotifyOwner"], 1))
        job.update({ "EmbedImages": 0, "Charset": 'UTF-8',})
        
        def setup_job(self, **kwargs): self.job.update(kwargs)
            # self.fromname = kwargs.get('fromname', '')
            # self.fromemail = kwargs.get('fromemail', '')
            # self.replyemail = kwargs.get('replyemail', '')
            # self.bounceemail = kwargs.get('bounceemail', '')
        
        def is_job_ready(self):
            """Check if the job is ready to be created"""
            if self.job['SendFromName'] and self.job['SendFromEmail'] and self.job['ReplyToEmail'] and self.job['BounceEmail']: return True
            else: return False
            
        def send(self, fktype = 'newsletter', fkid: int = 0, lists: list = [0], when = 0):
            """ Create a job for sending a campaign
            
            Required:
                fktype [str]: Type of the foreign key. Can be 'newsletter' or 'campaign'
                fkid [int]: ID of the campaign
                lists [list]: List of list to send to
                when [timestamp]: When to send the campaign. Can be 0 (now), or at a specific time 
                details: {
                    NewsletterChosen (int): id campaign
                    Lists (list): id lists
                    SendCriteria (array): {
                        Confirmed (bool): 1
                        CustomFields (array): {}
                        List (list): id list
                        Status (int): a
                    }
                    Multipart (bool): 1
                    TrackOpens (bool): 1
                    TrackLinks (bool): 1
                    EmbedImages (bool): 0
                    Newsletter (int): id newsletter
                    SendFromName (string): Name of sender
                    SendFromEmail (string): Email of sender
                    ReplyToEmail (string): Email to reply
                    BounceEmail (string): Email which really send the email
                    Charset (string): utf-8
                    NotifyOwner (bool): 1
                    SendStartTime (timestamp): 0 
                }
            """
            
            if not self.is_job_ready(): return { 'issuccess': False, 'message': 'Campaign not ready' }
            
            if fkid == 0 and self.campaign['campaignid']: fkid = self.campaign['campaignid']
            # Create XML for API calling
            lists_xml = ''.join("<Lists>{}</Lists>\n".format(i) for i in lists)
            list_xml = ''.join("<List>{}</List>\n".format(i) for i in lists)
            
            if when == 0: when = int(time.time())
            
            details_xml = f'''
            <jobtype>send</jobtype>
            <when>{when}</when>
            <ownerid>{self.campaign['ownerid']}</ownerid>
            <approved>{self.campaign['ownerid']}</approved>
            <fktype>{fktype}</fktype>
            <fkid>{fkid}</fkid>
            {lists_xml.lower()}
            <details>
                <NewsletterChosen>{fkid}</NewsletterChosen>
                {lists_xml}
                <SendCriteria>
                    <Confirmed>1</Confirmed>
                    <CustomFields></CustomFields>
                    {list_xml}
                    <Status>a</Status>
                </SendCriteria>
                <Multipart>{self.job['Multipart']}</Multipart>
                <TrackOpens>{self.job['TrackOpens']}</TrackOpens>
                <TrackLinks>{self.job['TrackLinks']}</TrackLinks>
                <EmbedImages>{self.job['EmbedImages']}</EmbedImages>
                <Newsletter>{fkid}</Newsletter>
                <SendFromName>{self.job['SendFromName']}</SendFromName>
                <SendFromEmail>{self.job['SendFromEmail']}</SendFromEmail>
                <ReplyToEmail>{self.job['ReplyToEmail']}</ReplyToEmail>
                <BounceEmail>{self.job['BounceEmail']}</BounceEmail>
                <Charset>{self.job['Charset']}</Charset>
                <NotifyOwner>{self.job['NotifyOwner']}</NotifyOwner>
                <SendStartTime>{when}</SendStartTime>
            </details>
            '''
            xml = self.xml_format('jobs', 'Create', details_xml)
            # Send request
            response = requests.post(self.url, data=xml)
            # Check response
            if response.status_code == 200:
                e = ET.fromstring(response.text)
                if self.issuccess(e):
                    jobid = e.find('data').text
                    return { 'issuccess': True, 'data': jobid }
                else: return self.iserror(e)
            return response.raise_for_status()