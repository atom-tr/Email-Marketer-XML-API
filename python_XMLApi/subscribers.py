from XMLApi import *

class Subscribers_API(API):
    # Subscriber
    def check_contact_list(self, list_id: int, email: str):
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
    
    def is_contact_in_list(self, list_id: int, email: str):
        """
        Return ID of contact if email is in list 
        """
        return self.check_contact_list(list_id, email)
    
    def get_Subscriber_id(self, list_id: int, email: str):
        """[summary]
        
        Arguments:
            list_id {int} -- id of list to check
            email {str} -- email address to check
        
        Returns:
            id {int} -- id of subscriber if found
            False if not found
        """
        return self.check_contact_list(list_id, email)
    
    
    def get_Subscribers(self, list_id: int, email = ''):
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
                return { 'issuccess':  True,  'count': count, 'data': subscribers }
            else: return self.iserror(e)
        else: return response.raise_for_status()
    
    def add_Subscriber(self, list_id: int, email: str, confirmed = True, format = 'html', custom_fields = {}):
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
        
    def delete_Subscriber(self, list_id: int, email: str):
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
       
    
    def get_Subscriber_CustomFields(self, list_id: int, email: str):
        # check if email is in list
        id = self.get_Subscriber_id(list_id, email)
        if id:
            details = f'''
            <subscriberid>{id}</subscriberid>
            <listid>{list_id}</listid>
            '''
            xml = self.xml_format('subscribers', 'LoadSubscriberCustomFields', details)
            response = requests.post(self.url, data=xml)
            if response.status_code == 200:
                e = ET.fromstring(response.text)
                if self.issuccess(e):
                    data = XmlListConfig(ElementTree.fromstring(response.text))
                    for d in data:
                        if isinstance(d, list): return { 'issuccess': True, 'data': d }
                else: return self.iserror(e)
            return response.raise_for_status()
        else: return { 'issuccess': False, 'message': 'Email not found in list' }
        
    def update_Subscriber_custom_field(self, subscriber_id: int, field_id: int, data):
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
        