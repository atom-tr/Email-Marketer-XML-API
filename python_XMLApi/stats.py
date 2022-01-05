from XMLApi import *

class Stats_API(API):
    def GetUserNewsletterStats(self, userid: int = 0):
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
                data = XmlListConfig(ElementTree.fromstring(response.text))
                for d in data:
                    if isinstance(d, list): return { 'issuccess': True, 'data': d }
            else: return self.iserror(e)
        return response.raise_for_status()
    
  