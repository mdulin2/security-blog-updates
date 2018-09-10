# Security Blog Updates
The world of security has so much to offer, with so many people posting about new vulnerabilities, discovers and word around the industry.
However, there are just so many blogs to follow! So, these scripts are meant to be used as a daily email to be sent to the user of which blogs
have been updated that day! 

## Setup 

### Package Installer. 
The progam assumes Python is installed (2.7 has been tested but I'm confident about 3.x).   
First run the command below:
```
./setup.sh
```

### Cronjobs
This will install all of the Python packages needed.   
Next, set this up with a `cronjob`(a cronjob is simply just a scheduled task in Linux) or something else to have this script run on certain time
intervals. Everything you need to know about cronjobs are be found at https://awc.com.my/uploadnew/5ffbd639c5e6eccea359cb1453a02bed_Setting%20Up%20Cron%20Job%20Using%20crontab.pdf. 

## Configurations 
### URLList.config:  

This is used in order to specify the URL's being kept track of. A sample file could look like the file below. Make sure to keep the name and use URLs. 
```
https://krebsonsecurity.com
https://research.checkpoint.com/
https://www.bleepingcomputer.com/
```

### Settings.config:   
In order to know which date to be verifying the checks on, set this file for a URL. By default, the first date is used. 
```
https://krebsonsecurity.com 2
https://research.checkpoint.com/ 2
https://www.bleepingcomputer.com/ 3
https://googleprojectzero.blogspot.com/ 5
https://duo.com/blog 7
https://www.thezdi.com/blog/ 18
```

Simply put, use `URL date#`.  
In order to figure out the correct date, go to the file that corresponds with the URL. Find the date that matches the most recent
post and use that value for the config's post date number. 

### creditionals.config
Put the email and password in here. 
Such as 
```
email: some_email@gmail.com
password: 1234567898iukjhgfbngfdzvcx;a';';';0-
```

## Issues 
* I personally run this on an AWS instance. Which, seemed like a great idea, but because of the IP being an AWS ec2 instance, this did not work.
Gmail blocks all IPs from ec2 instances, because of how much spam it tends to be. 
* This will not work with all websites. I decided to do this for mostly static websites (which most blogs are) because it is much simplier. 
In order to capture dynamic sites, Selenium needs to be set up, which seemed like quite the hassel. 
