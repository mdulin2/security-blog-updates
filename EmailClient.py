import smtplib
import time

from Updater import Updater

class EmailClient:

    def __init__(self):
        self.updater_client = Updater("Urls.config")
        self.email_content = self.set_up_email_content()

        # set up the SMTP server
        self.email, self.password = self.get_creditionals("Creditionals.config")
        self.server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        #self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(self.email, self.password)

    def send_email(self, sender_email, single = True):
        # the single parameter is used in order to dictate if the connection is closed or not.
        self.server.sendmail(self.email, sender_email, self.email_content)
        if(single):
            self.close_connection()

    def get_emails(self):
        file_object = open("Emails.config","r")
        config_by_line = file_object.readlines()
        config_by_line = [line.rstrip() for line in config_by_line]
        file_object.close()
        return config_by_line

    def send_email_group(self):
        # would be easy to implement; simply just read from a text file of some sort... Then move server.quit to here
        email_list = self.get_emails()
        for email in email_list:
            print "Sending email to {}...".format(email)
            self.send_email(email, single = False)
        self.close_connection()

    def set_up_email_content(self):
        updated_list = self.updater_client.get_updated_blog_list()
        #updated_list = ["https://krebsonsecurity.com","https://maxwelldulin.com/blog"]
        msg ="""
Hey! Security blogs are amazing! So, here's your custom list of followed blogs that have been updated in the last day:

"""
        blogs_updated = ""
        for blog in updated_list:
            blogs_updated += '\t' + blog + '\n'

        if(blogs_updated == ""):
            msg += "No blogs you are following have been updated. :( "
        else:
            msg += blogs_updated
            msg += "\n Have a wonderful rest of your day; and happy reading!\n"
            msg += "This blog follower list was created by Maxwell Dulin at http://maxwelldulin.com"
        
        subject="Security Blog Post Update"  
        message = "Subject: {}\n\n{}".format(subject,msg) 
        return message

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

if __name__ == "__main__":
    # need to be able to take in input...
    # need to be able to set up cron job on here, in Python? Lol. So, so, so weird...
    E = EmailClient()
    E.send_email_group()
