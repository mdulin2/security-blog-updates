import requests
import re
from BeautifulSoup import BeautifulSoup
import datefinder
from datetime import datetime
import os.path
import scrapy

class Blog:

    def __init__(self, url):
        self.url = url

    def tmp_pull_page(self):
        print str(scrapy.Request(self.url).text)

    def pull_page(self):
        print self.url
        request = requests.get(self.url).text
        BeautifulSoupTextObject = BeautifulSoup(request)

        page_without_html_tags = ''.join(BeautifulSoupTextObject.findAll(text=True))

        return page_without_html_tags

    def get_matches_by_page(self, stripped_page):
        date_matches = datefinder.find_dates(stripped_page)

        match_list = []
        for match in date_matches:
            match_list.append(match)
        return match_list

    def get_matched_dates(self):
        stripped_page = self.pull_page()
        dates = self.get_matches_by_page(stripped_page)
        dates_filtered = list(filter(lambda x: x.year >= 1920, dates))
        return dates_filtered

class Updater:

    def __init__(self,filename):
        self.filename = filename
        self.url_list = self.get_url_list()
        self.date_dict = self.date_dict_per_url()
        self.config_dict = self.read_config()

    def date_dict_per_url(self):

        url_to_date_dict = {}
        for url in self.url_list:
            blog_page = Blog(url)
            matched_dates_list = blog_page.get_matched_dates()
            url_to_date_dict[url] = matched_dates_list
        return url_to_date_dict

    def get_url_list(self):
        file_object = open(self.filename,"r")
        urls = file_object.readlines()
        urls_list = [url.rstrip() for url in urls]
        return urls_list

    def get_updated_blog_list(self):

        updated_blogs = []
        for blog in self.date_dict:
            if(self.has_blog_updated(blog)):
                updated_blogs.append(blog)
                self.write_dates_to_file(blog)

        return updated_blogs

    def has_blog_updated(self, url, comparison = "single"):
        if(url in self.config_dict):
            comparison = self.config_dict[url]

        if(self.is_first_time(url) or comparison == 'always'):
            return True

        urls_list_current = self.date_dict[url]
        urls_list_previous = self.read_dates_from_file(url)

        # first date validation
        if(comparison.lower() == "single"):
            if(urls_list_current[0] == urls_list_previous[0]):
                return False
            return True

        # particular date that's being checked
        elif(comparison.isdigit()):
            print urls_list_current[int(comparison)], urls_list_previous[int(comparison)]
            if(urls_list_current[int(comparison)-1] == urls_list_previous[int(comparison)-1]):
                return False
            return True

        # all date validation
        elif(comparison.lower() == 'all'):
            return  (set(urls_list_current) & set(urls_list_previous)) == set(urls_list_current)
        else:
            assert("Not a valid setting")

    # Checks to see if a file already exists for this url or not.
    def is_first_time(self, url):
        filename = self.get_filename(url)
        return not os.path.isfile(filename)

    def get_filename(self,url):
        filename = url.strip("https://").strip("http://").replace("/","")
        return filename + ".txt"

    def read_config(self, filename = "config"):
        file_object = open(filename,"r")
        files_list_per_line = file_object.readlines()

        #format entries correctly
        files_list_per_line = list(filter(lambda x: x != '\n', files_list_per_line))
        formatted_file = list(map(lambda x: x.rstrip(),files_list_per_line))

        config_dict = {}
        for config in formatted_file:
            url = config.split(" ")[0]
            spot = config.split(" ")[1]
            config_dict[url] = spot

        return config_dict

    def write_dates_to_file(self, url):
        filename = self.get_filename(url)
        file_object = open(filename,"w+")

        date_list = self.date_dict[url]
        for date in date_list:
            string_date = date.strftime("%Y-%m-%d %H:%M:%S")
            file_object.write((unicode(string_date)+'\n'))
        file_object.close()
        print "Write Successful... for " + url

    def read_dates_from_file(self, url):
        if(self.is_first_time(url)):
            return []
        filename = self.get_filename(url)
        file_object = open(filename,"r")

        urls = file_object.readlines()
        urls_list = [ datetime.strptime(url.rstrip(),"%Y-%m-%d %H:%M:%S") for url in urls]
        return urls_list

if __name__ == "__main__":
    # need to be able to take in input...
    # need to be able to set up cron job on here, in Python? Lol. So, so, so weird...
    U = Updater("url_list.txt")
    #B = Blog("https://blog.bentkowski.info/?view=classic")

    print U.get_updated_blog_list()