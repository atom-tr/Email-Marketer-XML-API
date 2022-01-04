# 
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
    def __init__(self, url, username, usertoken):
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
    
    def is_authenticated(self): 
        response = requests.post(self.url, data=self.xml_format('authentication', 'xmlapitest'))
        if response.status_code == 200:
            if response.text.find('<status>SUCCESS</status>') != -1: return True
            else: return False
        else: return response.raise_for_status()
    # List
    def get_lists(self):
        xml = self.xml_format('user', 'GetLists')
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                data = XmlListConfig(ElementTree.fromstring(response.text))
                for d in data:
                    if isinstance(d, list): return { 'issuccess': True, 'Lists': d }
            else: return self.iserror(e)
        return response.raise_for_status()
        
    def get_customfields(self, list_id):
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
                data = XmlListConfig(ElementTree.fromstring(response.text))
                for d in data:
                    if isinstance(d, list): return { 'issuccess': True, 'CustomFields': d }
            else: return self.iserror(e)
        return response.raise_for_status()
    # Subscriber
    def check_contact_list(self, list_id, email):
        """
        Return ID of contact if email is in list
        """
        details = f'''
        <emailaddress>{email}</emailaddress>
        <listids>{list_id}</listids>
        '''
        xml = self.xml_format('subscribers', 'IsSubscriberOnList', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e): return e.find('data').text
            else: return False
        else: return response.raise_for_status()
    
    def is_contact_in_list(self, list_id, email):
        """
        Return ID of contact if email is in list 
        """
        return self.check_contact_list(list_id, email)
    
    def get_subscriber_id(self, list_id, email):
        """[summary]
        
        Arguments:
            list_id {int} -- id of list to check
            email {str} -- email address to check
        
        Returns:
            id {int} -- id of subscriber if found
            False if not found
        """
        return self.check_contact_list(list_id, email)
    
    def get_subscribers(self, list_id, email = ''):
        """
        Search for subscribers in a list.
        Input:
            - int list_id: ID of the list to search
            - email: Email address to search for
        Output:
            - list of subscribers:
                + int list_id: ID of the list
                + int subscriberid: ID of the subscriber
                + str emailaddress: Email address of the subscriber
                + str format: Format of mail content for the subscriber
                + int subscribedate: Timestamp of when the subscriber subscribed
                + bool confirmed: Whether the subscriber has confirmed their subscribed
                + bool unsubscribed: Whether the subscriber has unsubscribed
                + bool bounced: Whether the subscriber has bounced
        """
        details = '''
        <searchinfo>
        <List>{}</List>
        <Email>{}</Email>
        </searchinfo>
        '''.format(list_id, email)
        xml = self.xml_format('subscribers', 'GetSubscribers', details)

        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            # xml to dictionary
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                count = e.find('data').find('count').text
                # subscribers list in data > items > item
                data = XmlListConfig(e.find('data'))
                subscribers = []
                for item in data:
                    if isinstance(item, dict):
                        subscribers = [ subitem for subitem in item['items']['item'] if isinstance(subitem, dict)]
                    else: continue   
                return { 'issuccess':  True,  'count': count, 'subscribers': subscribers }
            else: return self.iserror(e)
        else: return response.raise_for_status()
    
    def add_subscriber(self, list_id, email, confirmed = True, format = 'html', custom_fields = {}):
        details = f'''
        <emailaddress>{email}</emailaddress>
        <mailinglist>{list_id}</mailinglist>
        <format>{format}</format>
        <confirmed>{confirmed}</confirmed>
        <customfields>
        '''
        if custom_fields: details.join(f"<item><fieldid>{key}</fieldid><value>{value}</value></item>" for key, value in custom_fields.items())
        
        details += "</customfields>"
        xml = self.xml_format('subscribers', 'AddSubscriberToList', details)
        
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e):
                return { 'issuccess':  True, 'id': e.find('data').text }
            else: return self.iserror(e)
            
        else: return response.raise_for_status()
        
    def delete_subscriber(self, list_id, email):
        details = f'''
        <list>{list_id}</list>
        <emailaddress>{email}</emailaddress>
        '''
        xml = self.xml_format('subscribers', 'DeleteSubscriber', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e): return { 'issuccess':  True }
            else: return self.iserror(e)
        else: return response.raise_for_status()
        
    def update_subscriber_custom_field(self, subscriber_id, field_id, data):
        details = f'''
        <subscriberids>
          <id>{subscriber_id}</id>
        </subscriberids>
        <fieldid>{field_id}</fieldid>
        <data>{data}</data>
        '''
        xml = self.xml_format('subscribers', 'SaveSubscriberCustomField', details)
        response = requests.post(self.url, data=xml)
        if response.status_code == 200:
            e = ET.fromstring(response.text)
            if self.issuccess(e): return { 'issuccess':  True }
            else: return self.iserror(e)
        else: return response.raise_for_status()
        