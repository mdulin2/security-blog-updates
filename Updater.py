import os.path
import sys
from datetime import datetime
from Blog import Blog

# This is a super hack... Not good to use.
# I could not figure out where the encoding issue was happening, so I just went with the back.
reload(sys)
sys.setdefaultencoding('utf8')

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

            for elt in range(len(urls_list_current)):
                print urls_list_previous[elt]
                print urls_list_current[elt]
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
            file_object.write((string_date.encode('utf-8')+'\n'))
        file_object.close()
        print "Write Successful... for " + url

    def write_tags_to_file(self,url):
        filename = self.get_filename(url)
        file_object = open('./storage_info/' + filename,"w+")

        tag_list = self.previous_value_dict[url]
        for tag in tag_list:
            file_object.write(tag.decode('utf-8') +'\n')
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

if __name__ == "__main__":
    U = Updater("Urls.config")
    print U.get_updated_blog_list()
