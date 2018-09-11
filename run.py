import sys

from EmailClient import EmailClient
from CLI_Config import CLI_Config

class run:

    def __init__(self):
        self.CLI = CLI_Config()

    def sendmail(self):
        Client = EmailClient()
        Client.send_email_group()

    def set_cron_job(self):
        pass # should have this automatically set up the cronjob for the user.

    def fix_commands(self, commands):
        updated_commands = []
        for command in commands:
            if command != '\n' and command != ' ' and command != '\t':
                updated_commands.append(command)
        return updated_commands

    def is_valid_date_parameter(self, value):
        #ensures that an overflow will not occur
        info = self.CLI.get_dates(url)
        if(value < len(info)):
            return True
        print "Not a valid date parameter, because of the size."

    def is_valid_header_parameter(self,value):
        # ensures a valid date header
        if(value.isdigit() and int(value) >= 1 and int(value) <= 6):
            return True
        print "Not a valid header parameter"

    def config_interactive(self, commands):
        commands = self.fix_commands(commands)

        if('-i' in commands):
            self.CLI.user_ask()

        elif(commands[1] == '--add_url' or commands[1] == '-add'):
            url = commands[2]
            value = commands[4]
            if('--header' in commands and self.is_valid_header_parameter(value)):
                self.CLI.add_to_settings(url,'header', value)
            elif('--date' in commands and self.is_valid_date_parameter(value)):
                self.CLI.add_to_settings(url, 'date', value)
            else:
                print 'This tag is not supported yet... Try --header or --date'

        elif(commands[1] == '--change_url' or commands[1] == '-change'):
            url = commands[2]
            setting = commands[3]
            value = commands[4]
            if('--header' in commands and self.is_valid_header_parameter(value)):
                self.CLI.change_settings(url,'header', value)
            elif('--date' in commands and self.is_valid_date_parameter(value)):
                self.CLI.change_settings(url, 'date', value)
            else:
                print 'This tag is not supported yet... Try --header or --date'

        elif(commands[1] == '--remove_url' or commands[1] == '-remove'):
            url = commands[2]
            self.CLI.remove_url(url)

        elif(commands[1] == '--view' or commands[1] == '-view'):
            url = commands[2]
            if('--header' in commands or '-head' in commands):
                if(commands[3] == '--header' or commands[3] == '-head'):
                    info = self.CLI.get_tags(url, 'header', commands[4])
                    header_type = commands[4]
                else:
                    info = self.CLI.get_tags(url, 'header', commands[3])
                    header_type = commands[3]
                print 'For type header' + header_type +':'
                for match in info:
                    print match
                print '\nHow does this match up with the site? If this works, then add it with the --add_url flag, with the same settings you just ran on the --view!'

            elif('--date' in commands or '-date' in commands):
                if(commands[3] == '--date' or commands[3] == '-date'):
                    info = self.CLI.get_dates(url)
                for index in range(len(info)):
                    print "{}) {}".format(index, str(info[index])[0:10])

                print "\nTake the number next to the correct date. Now, use the --add_url url date # in order to add this to the blog following!"
            else:
                print 'This tag is not supported yet... Try --header # or --date'

        elif(commands[1] == '--send_email'):
            email = commands[2]
            print "Prepaing email..."
            Client = EmailClient()
            Client.send_email(email)

        elif(commands[1] == '--email' or commands[1] == '--send' or commands[1] == '-send'):
            print "Preparing email..."
            Client = EmailClient()
            Client.send_email_group()

        elif(commands[1] == '--show' or commands[1] == '-show'):
            print "All of your followed blogs:"
            self.CLI.show_urls()
        elif(commands[1] == '--cron' or commands[1] == '-cron'):
            self.CLI.cronjob(commands[2])
        else:
            print "Not a valid command..."

if __name__ == "__main__":
    r = run()
    if(len(sys.argv) == 1):
        print "Sending Email..."
        print "Getting the following blog pages..."
        r.sendmail()
    else:
        r.config_interactive(sys.argv)
