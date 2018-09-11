from bs4 import BeautifulSoup
import requests
import datefinder
import re
import tweepy

class Blog:

    def __init__(self, url):
        self.url = url

    def pull_page_dates(self):
        print self.url
        request = requests.get(self.url).text
        BeautifulSoupTextObject = BeautifulSoup(request,'html.parser')

        page_without_html_tags = ''.join(BeautifulSoupTextObject.findAll(text=True))

        return page_without_html_tags

    def get_matched_by_tag(self, search_type = "header", header_type='2'):
        # need to have different settings for different headers
        print self.url
        request  = requests.get(self.url,'html.parser')
        page = request.text
        soup = BeautifulSoup(page,"lxml")

        if(search_type == "header"):
            header_list = []
            for header in soup.find_all(re.compile('^h['+header_type+']$')):
                tag_re = re.compile(r'<[^>]+>')
                header_list.append(tag_re.sub('', str(header)).replace('\n',''))
            return header_list
        else:
            assert('Not implemented...Only header tag and dates are currently accepted')

    def get_matches_by_page(self, stripped_page):
        date_matches = datefinder.find_dates(stripped_page)

        match_list = []
        for match in date_matches:
            match_list.append(match)
        return match_list

    def get_matched_dates(self):
        stripped_page = self.pull_page_dates()
        dates = self.get_matches_by_page(stripped_page)
        dates_filtered = list(filter(lambda x: x.year >= 1920, dates))
        return dates_filtered


    def get_pull_page_tweets(self):
        auth = tweepy.BasicAuthHandler("dooflin5", "Airjordan23!?")
        api = tweepy.API(auth)

if __name__ == "__main__":
    B = Blog("@dooflin5")
    B.get_pull_page_tweets()
