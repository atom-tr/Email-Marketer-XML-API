#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# This has the Base API class in it.
# Sets up the database object for use.
# API base on iem v6.2.0

@package API
@subpackage Send_API

@author: thai.tv (thai.tv@netnam.vn)
@email: sys-sgn@netnam.vn
@status: InProgress
@link: https://github.com/atom-tr/Email-Marketer-XML-API
"""

from _typeshed import Self
from .newsletters import *
from .lists import *

class Send_API(Newsletters_API, List_API):
    """Send a campaign with newletter id and contact list id
    
    Args:
        campaign_id (int): id of campaign to send
        list_id (int): id of list to send

    """
    newsletterapi = Newsletters_API()
    listapi = List_API()
    def setup(self, **kwargs):
        self.owneremail = kwargs.get('owneremail', None)
        self.ownername = kwargs.get('ownername', None)
        self.replytoemail = kwargs.get('replytoemail', None)
        self.bounceemail = kwargs.get('bounceemail', None)
    
    def send(self, campaign_id: int, list_id: int, when, filteringOption: int = 1) -> dict:
        userid = self.get_userid()
        newsletters = self.newsletterapi.get_newsletters(ownerid=userid, newsletterids=campaign_id)
        if newsletters:
            pass
    