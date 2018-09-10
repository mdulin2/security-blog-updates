import requests
import re
from bs4 import BeautifulSoup
import datefinder
from datetime import datetime
import os.path
import scrapy
import smtplib
import time

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

class Updater:

    def __init__(self,filename):
        self.filename = filename
        self.url_list = self.get_url_list()
        self.config_dict = self.read_config()
        self.previous_value_dict = self.previous_value_dict_per_url()

    def previous_value_dict_per_url(self):

        url_to_previous_value_dict = {}
        for url in self.url_list:
            blog_page = Blog(url)
            if(self.config_dict[url][0] == 'date'):
                matched_dates_list = blog_page.get_matched_dates()
                url_to_previous_value_dict[url] = matched_dates_list
            elif(self.config_dict[url][0] == 'header'):
                matched_header_list = blog_page.get_matched_by_tag(search_type = "header",header_type=self.config_dict[url][1])
                url_to_previous_value_dict[url] = matched_header_list


        return url_to_previous_value_dict

    def get_url_list(self):
        file_object = open(self.filename,"r")
        urls = file_object.readlines()
        urls_list = [url.rstrip() for url in urls]
        return urls_list

    def get_updated_blog_list(self):

        updated_blogs = []
        for blog in self.previous_value_dict:
            if(self.has_blog_updated(blog)): # also passes for brand new sites to the subscription
                updated_blogs.append(blog)
                if(self.config_dict[blog][0] == 'date'):
                    self.write_dates_to_file(blog)
                else:
                    self.write_tags_to_file(blog)

        return updated_blogs

    def has_blog_updated(self, url, comparison = 0):
        if(url in self.config_dict):
            comparison_type, comparison_value = self.config_dict[url]

        if(self.is_first_time(url) or comparison_value == 'always'):
            return True

        urls_list_current = self.previous_value_dict[url]
        if(comparison_type == 'date'):
            urls_list_previous = self.read_previous_dates_from_file(url)
            # particular date that's being checked
            if(comparison_value.isdigit()):
                if(str(urls_list_current[int(comparison_value)-1]) == urls_list_previous[int(comparison_value)-1].replace('\n','')):
                    return False
                return True

            # all date validation
            elif(comparison_value.lower() == 'all'):
                return (set(urls_list_current) & set(urls_list_previous)) == set(urls_list_current)
            else:
                assert("Not a valid setting")
        elif(comparison_type == 'header'):

            urls_list_previous = self.read_previous_tags_from_file(url)
            return not urls_list_current == urls_list_previous

    # Checks to see if a file already exists for this url or not.
    def is_first_time(self, url):
        filename = self.get_filename(url)
        return not os.path.isfile('./storage_info/' + filename)

    def get_filename(self,url):
        filename = url.strip("https://").strip("http://").replace("/","")
        return filename + ".txt"

    def read_config(self, filename = "Settings.config"):
        file_object = open(filename,"r")
        files_list_per_line = file_object.readlines()

        #format entries correctly
        files_list_per_line = list(filter(lambda x: x != '\n', files_list_per_line))
        formatted_file = list(map(lambda x: x.rstrip(),files_list_per_line))

        config_dict = {}
        for config in formatted_file:
            url = config.split(" ")[0]
            search_type = config.split(" ")[1]
            value = config.split(" ")[2]
            config_dict[url] = (search_type, value)

        return config_dict

    def write_dates_to_file(self, url):
        filename = self.get_filename(url)
        file_object = open('./storage_info/'+filename,"w+")

        date_list = self.previous_value_dict[url]
        for date in date_list:
            string_date = date.strftime("%Y-%m-%d %H:%M:%S")
            file_object.write((unicode(string_date)+'\n'))
        file_object.close()
        print "Write Successful... for " + url

    def write_tags_to_file(self,url):
        filename = self.get_filename(url)
        file_object = open('./storage_info/' + filename,"w+")

        date_list = self.previous_value_dict[url]
        for date in date_list:
            file_object.write((unicode(date)+'\n'))
        file_object.close()
        print "Write Successful... for " + url

    def read_previous_dates_from_file(self, url):
        if(self.is_first_time(url)):
            return []

        filename = self.get_filename(url)
        file_object = open('./storage_info/' + filename,"r")
        previous_values = file_object.readlines()
        previous_values_list = [ datetime.strptime(prev_val.rstrip(),"%Y-%m-%d %H:%M:%S") for prev_val in previous_values]
        return previous_values

    def read_previous_tags_from_file(self, url):
        if(self.is_first_time(url)):
            return []

        filename = self.get_filename(url)
        file_object = open('./storage_info/' + filename,"r")
        previous_values = file_object.readlines()
        previous_values = list(map(lambda x: x.rstrip(), previous_values)) #strip all newlines
        return previous_values

class EmailClient:

    def __init__(self):
        # set up the SMTP server
        self.email, self.password = self.get_creditionals("Creditionals.config")
        self.updater_client = Updater("Urls.config")
        self.email_content = self.set_up_email_content()

        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(self.email, self.password)

    def send_email(self, sender_email):
        self.server.sendmail(self.email, sender_email, self.email_content)
        self.close_connection()

    def send_email_group(self, filename):
        # would be easy to implement; simply just read from a text file of some sort... Then move server.quit to here
        pass

    def set_up_email_content(self):
        updated_list = self.updater_client.get_updated_blog_list()
        #updated_list = ["https://krebsonsecurity.com","https://maxwelldulin.com/blog"]
        print updated_list
        msg ="""
        Hey! Security blogs are amazing! So, here's your custom list of followed blogs that have been updated in the last day:

"""
        for blog in updated_list:
            msg += '\t' + blog + '\n'

        msg += "\n Have a wonderful rest of your day; and happy reading!"

        return msg

    def close_connection(self):
        self.server.quit()

    def get_creditionals(self,filename):
        file_object = open(filename,"r")
        files_list_per_line = file_object.readlines()

        files_list_per_line = list(filter(lambda x: x != '\n', files_list_per_line))
        formatted_file = list(map(lambda x: x.rstrip(),files_list_per_line))

        username = formatted_file[0].replace(" ","").split(":")[1]
        password = formatted_file[1].strip(" ").replace(" ","").split(":")[1]
        return username, password

class ConfigFiles:
    def __init__(self):
        pass

    def url_questions(self, url):

        user_input = raw_input("How do you want to setup the file? Use either 'tag'(t) or 'date'(d)\n")
        if(user_input == 't' or user_input == 'tag'):

            tag_type = self.get_valid_tag()
            print tag_type
            if(tag_type == 'header'):

                is_good_tag_value = False
                while(is_good_tag_value == False):
                    tag_value = raw_input("Which type of " + tag_type + " would you like to check? A number from 1-6. \n")

                    if(tag_value.isdigit() and int(tag_value) > 0 and int(tag_value) < 7):
                        is_good_tag_value = True
            else:
                print 'Not a valid tag... Please try again.'

            tag_values = self.get_tags(url, tag_type, tag_value)
            print "Resulting values..."
            time.sleep(.400)
            self.show_tag_info(tag_values)

            return tag_type, tag_value

        elif(user_input == 'd' or user_input == 'date'):
            dates_list = self.get_dates(url)
            print "Resulting values..."
            time.sleep(.400)
            self.show_date_info(dates_list)

            is_good_tag_value = False
            while(is_good_tag_value == False):
                tag_number = raw_input("Which date number(#) is the most current blog post? \n")

                if(tag_number.isdigit() and int(tag_number) > 0 and int(tag_number)-1 <= len(dates_list)):
                    return 'date', tag_number

    def user_ask(self):

        decision = '-1'
        while(decision != '4'):
            decision = raw_input("""
What would you like to do?
1) Add a new blog?
2) Update a blog?
3) Remove a blog?
4) Exit
""")
            if(decision == '1'):
                url = raw_input("What URL would you like to add?\n")
                blog_type, blog_value = self.url_questions(url)
                proceed = raw_input('Are you satisifed with {} using the {} to verify if the blog has been updated with the value {}?\n\nEnter Y for to write changes.\n'.format(url,blog_type,blog_value))
                if(proceed.lower() == 'y' or proceed.lower() == 'yes'):
                    self.add_to_settings(url, blog_type, blog_value)

            elif(decision == '2'):
                url = raw_input("What URL would you like to change?\n")
                blog_type, blog_value = self.url_questions(url)
                proceed = raw_input('Are you satisifed with {} using the {} to verify if the blog has been updated with the value {}?\n\nEnter Y for to write changes.\n'.format(url,blog_type,blog_value))
                if(proceed.lower() == 'y' or proceed.lower() == 'yes'):
                    self.change_settings(url, blog_type, blog_value)

    def remove_url(self):
        pass

    def change_settings(self, url, blog_type, blog_value):
        file_object = open("Settings.config","r")
        config_by_line = file_object.readlines()
        config_by_line = [line.rstrip() for line in config_by_line]
        file_object.close()

        file_object = open("Settings.config","w")
        is_in_file = False
        for line_index in range(len(config_by_line)):
            line = config_by_line[line_index].split(' ')
            old_url = line[0]
            if(old_url == url):
                fixed_entry = "{} {} {}\n".format(url,blog_type, blog_value)
                is_in_file = True
                file_object.write(fixed_entry)
            else:
                file_object.write(config_by_line[line_index] + '\n')

        file_object.close()
        if(is_in_file == False):
            self.add_to_settings(url, blog_type, blog_value)

    def add_to_settings(self, url, blog_type, blog_value):
        with open("Settings.config", "a") as text_file:
            text_file.write('{} {} {}\n'.format(url,blog_type,blog_value))

        with open("Urls.config", "a") as text_file:
            text_file.write(url + '\n')
        # also,need to add to regular URLLlist...
    def get_valid_tag(self):
        while(True):
            tag_value = raw_input("What type of tag would you like to check? Currently support 'header' or 'h'... \n")
            if(tag_value == 'header' or tag_value == 'h'):
                return 'header'

    def get_dates(self,url):
        page = Blog(url)
        return page.get_matched_dates()

    def get_tags(self, url, tag, tag_type):
        page = Blog(url)
        return page.get_matched_by_tag(search_type = tag, header_type = tag_type)

    def show_date_info(self, dates_list):

        iter = 1
        for date in dates_list:
            print str(iter) + ')', date
            iter +=1
        print '\n'

    def show_tag_info(self, tag_list):

        iter = 1
        for tag in tag_list:
            print str(iter) + ')', tag
            iter +=1
        print '\n'

if __name__ == "__main__":
    # need to be able to take in input...
    # need to be able to set up cron job on here, in Python? Lol. So, so, so weird...
    # E = EmailClient()

    #E.get_creditionals("creditionals.config")
    # E.send_email("xxx")
    #B = Blog("https://blog.0patch.com/")
    #B.get_matched_by_tag()
    U = Updater("Urls.config")
    U.get_updated_blog_list()
    #C = ConfigFiles()
    #C.user_ask()
    #C.add_to_config("maxwelldulin.com","date", "3")
    # C.change_settings("maxwelldulin.com","date", "6")
