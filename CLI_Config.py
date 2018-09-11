from crontab import CronTab
import os
import time
from Blog import Blog

class CLI_Config:

    def url_questions(self, url):

        user_input = raw_input("How do you want to setup the file? Use either 'tag'(t) or 'date'(d)\n")
        if(user_input == 't' or user_input == 'tag'):

            tag_type = self.get_valid_tag()
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
        while(decision != '6'):
            decision = raw_input("""
What would you like to do?
1) Add a new blog?
2) Update a blog?
3) Remove a blog?
4) Display followed blogs
5) Setup cronjob
6) Exit
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
            elif(decision == '3'):
                url = raw_input("What URL would you like to change?\n")
                proceed = raw_input('Are you satisifed with deleting {} from your list of followed blogs?\n\nEnter Y for to write changes.\n'.format(url))
                if(proceed.lower() == 'y' or proceed.lower() == 'yes'):
                    url = url.replace('\n','')
                    url = url.replace('\t','')
                    url = url.replace(' ','')
                    print url
                    self.remove_url(url)

            elif(decision == '4'):
                self.show_followed_blogs()
            elif(decision == '5'):
                self.cron_interactive()

    def remove_url(self, url):
        file_object = open("Urls.config","r")
        config_by_line = file_object.readlines()
        config_by_line = [line.rstrip() for line in config_by_line]
        file_object.close()

        file_object = open("Urls.config","w")
        is_in_file = False
        for line_index in range(len(config_by_line)):
            line = config_by_line[line_index].split(' ')
            old_url = line[0]
            if(old_url != url):
                file_object.write(config_by_line[line_index] + '\n')
            else:
                is_in_file = True

        file_object.close()
        if(is_in_file == False):
            print "Could not find URL to remove..."
        else:
            print "The blog at {} has been removed.".format(url)

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

    def is_in_file(self, url, file_type = "Settings"):
        file_object = open(file_type+ ".config","r")
        config_by_line = file_object.readlines()
        config_by_line = [line.rstrip() for line in config_by_line]
        file_object.close()

        if(file_type == "Settings"):
            for line_index in range(len(config_by_line)):
                line = config_by_line[line_index].split(' ')
                old_url = line[0]
                if(old_url == url):
                    return True
            return False
        elif(file_type == 'Urls'):
            for line_index in range(len(config_by_line)):
                old_url = config_by_line[line_index]
                if(old_url == url):
                    return True
            return False
        else:
            print "File search is not supported for this file."

    def add_to_settings(self, url, blog_type, blog_value):
        if(self.is_in_file(url)):
            self.change_settings(url, blog_type, blog_value)
        else:
            with open("Settings.config", "a") as text_file:
                text_file.write('{} {} {}\n'.format(url,blog_type,blog_value))

        if(self.is_in_file(url,file_type = "Urls") == False):
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

    def show_followed_blogs(self):
        file_object = open("Urls.config","r")
        config_by_line = file_object.readlines()
        config_by_line = [line.rstrip() for line in config_by_line]
        for blog in config_by_line:
            print blog
        file_object.close()

    def cronjob(self, hour):
        print "A cronjob is a timing based Linux event! This is how the program knows when to send an email"
        print "This program is currently set to run once per day. But, you can manually configure this to run more than this or less."
        minute = 0
        if(hour.isdigit() == False):
            print "Not a valid hour to use. Please choose a number between 1 and 24 inclusive."
            return

        if(int(hour) > 24 or int(hour < 0)):
            print "Not a valid hour to use. Please choose a number between 1 and 24 inclusive."
            return

        user = os.environ['USER']
        directory = os.getcwd()

        cron = CronTab(user=user)
        cron_job = cron.new(command = "python {}/run.py".format(directory), comment = "For blog updater")
        cron_job.hour.also.on(hour)
        cron.write()

        print "Your cronjob is now configured..."
        print "Please remember, if you move this Python file redo this process. The cronjob is pointing to the run.py in this folder."

    def get_hour(self):
        while(True):
            hour = raw_input("What hour interval would you like this to be sent?\n")
            if(hour.isdigit() and (int(hour) <= 24 and int(hour) >= 0)):
                return hour

    def cron_interactive(self):
        print "A cronjob is a timing based Linux event! This is how the program knows when to send an email"
        print "This program is currently set to run once per day. But, you can manually configure this to run more than this or less."
        minute = 0
        hour = self.get_hour()

        user = os.environ['USER']
        directory = os.getcwd()

        cron = CronTab(user=user)
        cron_job = cron.new(command = "python {}/run.py".format(directory), comment = "For blog updater")
        cron_job.hour.also.on(hour)
        cron.write()

        print "Your cronjob is now configured..."


if __name__ == "__main__":
    C = CLI_Config()
    C.user_ask()
