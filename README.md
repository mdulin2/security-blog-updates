# Security Blog Updates
![](https://media.giphy.com/media/26ufe7WwGmhaFi5J6/giphy.gif)  
There are just too many security blogs to follow; so many great professionals and companies that we want to keep track of! It is uter choas trying to follow all of our blogs. Or, you want to keep your security team up-to-date with the security world, the new exploits and so on. 
So, this project is mean to fix this problem. Let's clean up the mess!  
To clean up the mess, we're going to follow all of our security blogs, with a daily email being sent to the followering of the blog. 
## Setup 

### Package Installer. 
The progam assumes Python is installed (2.7 has been tested but I'm confident about 3.x).   
First run the command below:
```
./setup.sh
```

### Cronjobs
Cronjobs are wonderful because they are timing based events on a Unix OS. So, I decided to set this up with a `cronjob`(a cronjob is simply just a scheduled task in Linux) or something else to have this script run on certain time
intervals. There are command line options for setting up the cronjob, but you can also do it manually.  

Everything you need to know about cronjobs are be found at https://awc.com.my/uploadnew/5ffbd639c5e6eccea359cb1453a02bed_Setting%20Up%20Cron%20Job%20Using%20crontab.pdf for cronjobs. 

## Configurations 

### Creditionals.config
Put the email and password in here. 
Such as 
```
email: some_email@gmail.com
password: 1234567898iukjhgfbngfdzvcx;a';';';0-
```
An email and password is needed in order to log onto the email account to send the emails.

### Emails.config 
Put your email list in this file. Each email should be its own individual line. Plan on supporting emails that are semi-colon delimited. 

## How It Works
Essentially, this is just a webscapper, looking for particular values. There are two types of settings right now: <i> header </i> and <i> dates </i>. In order to keep track of the changes on the blog, it is handy to be able to manually choose what to look out for. Both of these settings are useful, depending on the website. For instance, https://blog.0patch.com/ does not have dates on the site. Hence, it is a better decision to use the <i>header</i> feature for this one. However, when headers are all similar, such as on https://blog.securityevaluators.com/, it is better to use the dates feature. This a customizable setter for following blogs! You have the power to make this great.  
<b>Note:</b> It is reccomended that the header is used by default, besides on completely static websites for dates, such as https://krebsonsecurity.com. 

## Setting Up The Blog Updater 
At first, a rich understanding of the configuration files was needed, which seemed unreasonable. So, a CLI for adding, removing and setting up the configuration files was created. There is both a interactive version (recommended) and a normal CLI version. When setting up which blogs to follow, it is reccomended that the user has a browser open to know the results that they are looking for. 

### Interactive(recommended):
The interactive version is recommended because of how easy and collaborative it is to use. When choosing the correct date to check if the blog has been updated or not it is convenient to <i>see</i> the dates that you are choosing from. Same as the dates, it is easy to check which header is the title of the newest blog post.   
```
1) Add Blog  
2) Update Blog
3) Remove Blog
4) Display Followed Blogs
5) Setup the cronjob
6) Exit 
```
For add and update here is the flow: 
1) Select a url  
2) Select a type of check(either a date or header tag) which was 'd' and 't'.  
3) For date:  
The page will be loaded, then all of the dates on the website will be shown. Type in the number that corresponds to the date that matches the blogs most recent post.  
4) For tag(header):  
Select the header tag then select which header(value 1-6) you would like to test against.   
5) If the settings match what you would like, then click 'y'. Otherwise, restart the process until a valid check for the site is found. 

<b>Note:</b> Everything that can be done in the interactive can also be done in the CLI and vice-versa. 

### CLI(usable): 
The CLI has the same exact capabilities as the interactive version, but does it call by call. Without any parameters, run.py will check to see if all the blogs have been updated, then send an email to the group. 
#### Flags for CLI

Run this with python run.py _comands_ 
```
-i : Use this to get into interactive mode for configuring the blog following

Add a single url with the settings to the email list:
--add_url url_name --header/--date header_or_date_value       ** -add will also work

Change a single url with the settings to the email list:
--change_url url_name --header/--date header_or_date_value    ** -change will also work

Remove a single url from the email list:
--remove_url url_name                                         ** -remove will also work

View the results of a url with a particular setting: 
--view url_name --header/--date value_to_check                ** -view will also work 

Send a single email: 
--send_email email_address_to_send_to

Send a group of emails, from the email list: 
--email                                                       ** --send and -send will also work 

Show all of the currently followed blogs:
--show                                                        ** -show will also work 

Set up the cronjob...By default, it sends an email once per day: 
--cron hour                                                   ** -cron will also work 

```

## Future
I plan on adding a Twitter follower functionality to this. However, it is quite complicated for someone to use the Twitter API as a user. So, I am trying to find a way around this! 

## Issues 
* I personally run this on an AWS instance. Which, seemed like a great idea, but because of the IP being an AWS ec2 instance, this did not work out wel. Gmail and Outlook blocks all IPs from ec2 instances, because of how much spam it tends to be. I am using my school email, which for some reason bypasses this restriction.
* Some websites will not work, such as my personal website. This process is done, using a webscraper to take the content off of the page. However, with how create-react-app works, the scrapper will not grab the information correctly. 
* Currently, when a header has unicode characters, the check will always return true. I am currently working on fixing this. 
In order to capture dynamic sites, Selenium needs to be set up, which seemed like quite the hassel. 
