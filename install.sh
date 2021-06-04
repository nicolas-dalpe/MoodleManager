python3 mm.py create db_ec_moodle310

# If !config.php
php admin/cli/install.php --lang=en --wwwroot=https://moodle.local --dataroot=/var/www/md_ec_moodle310 --fullname=Sandbox --shortname=sb --adminuser=admin --adminpass=Abc123Def456 --adminemail=nicolas.dalpe@knowledgeone.ca --agree-license=yes

# config.php
php admin/cli/install_database.php --fullname=QR Phase3 Moodle396 --shortname=QR396 --lang=en --adminuser=admin --adminpass=Abc123\!\@\# --adminemail=admin.user@knowledgeone.ca --agree-license=yes

# Moosh commands
moosh course-create --category 1 --fullname "QR Code" QRC
moosh user-create --password Abc123\!\@\# --email nicolas.dalpe@knowledgeone.ca --digest 2 --city Montreal --country CA --firstname "Nicolas" --lastname "Dalpe" nicolas.dalpe
moosh course-enrolbyname -r editingteacher -f nicolas -l dalpe -c QRC

moosh user-create --password Abc123\!\@\# --email student1@knowledgeone.ca --digest 2 --city Montreal --country CA --firstname "Student" --lastname "One" student1
moosh user-create --password Abc123\!\@\# --email student2@knowledgeone.ca --digest 2 --city Montreal --country CA --firstname "Student" --lastname "Two" student2
moosh course-enrol 3 student1 student2

# Force users to log in
# Normally, the front page of the site and the course listings (but not courses)
# can be read by people without logging in to the site. If you want to force
# people to log in before they do ANYTHING on the site,
# then you should enable this setting.
php admin/cli/cfg.php --name=forcelogin --set=1

# Default country
# If you set a country here, then this country will be selected by default
# on new user accounts. To force users to choose a country, just leave this unset.
php admin/cli/cfg.php --name=country --set=CA

# Default city
# A city entered here will be the default city when creating new user accounts.
php admin/cli/cfg.php --name=defaultcity --set=Montreal

# Default timezone
# This is the default timezone for displaying dates - each user can override
# this setting in their profile. Cron tasks and other server settings are
# specified in this timezone. You should change the setting if it shows
# as "Invalid timezone"
php admin/cli/cfg.php --name=timezone --set=America/New_York

# Guest Front page
php admin/cli/cfg.php --name=frontpage --set=none

# Guest login button
# You can hide or show the guest login button on the login page.
php admin/cli/cfg.php --name=guestloginbutton --set=0

# Open to search engines
# If you enable this setting, then search engines will be allowed to enter
# your site as a guest. In addition, people coming in to your site via a
# search engine will automatically be logged in as a guest. Note that this
# only provides transparent access to courses that already allow guest access.
php admin/cli/cfg.php --name=opentowebcrawlers --set=0

# Allow indexing by search engines
# This determines whether to allow search engines to index your site.
# "Everywhere" will allow the search engines to search everywhere including
# login and signup pages, which means sites with Force Login turned on are
# still indexed. To avoid the risk of spam involved with the signup page
# being searchable, use "Everywhere except login and signup pages".
# "Nowhere" will tell search engines not to index any page. Note this
# is only a tag in the header of the site. It is up to the search
# engine to respect the tag.
php admin/cli/cfg.php --name=allowindexing --set=2


# Cookie prefix sessioncookie
# This setting customises the name of the cookie used for Moodle sessions.
# This is optional, and only useful to avoid cookies being confused when
# there is more than one copy of Moodle running within the same web site.
php admin/cli/cfg.php --name=sessioncookie --set=moodlelocal

# Automatically check for available updates
# If enabled, your site will automatically check for available updates for
# both Moodle code and all additional plugins. If there is a new update available,
# a notification will be sent to site admins.
php admin/cli/cfg.php --name=updateautocheck --set=0



###############################
############ D E V ############
###############################

# Cache all language strings
# Caches all the language strings into compiled files in the data directory.
# If you are translating Moodle or changing strings in the Moodle source code
# then you may want to switch this off. Otherwise leave it on to see
# performance benefits.
php admin/cli/cfg.php --name=langstringcache --set=0

# Analytics
# Analytics models, such as 'Students at risk of dropping out' or 'Upcoming activities due',
# can generate predictions, send insight notifications and offer further actions
# such as messaging users.
php admin/cli/cfg.php --name=enableanalytics --set=0

# Enable statistics
# If you choose 'yes' here, Moodle's cronjob will process the logs and gather some statistics.
# Depending on the amount of traffic on your site, this can take awhile. If you enable this,
# you will be able to see some interesting graphs and statistics about each of your courses,
# or on a sitewide basis.
php admin/cli/cfg.php --name=enablestats --set=0


# Networking
# MNet allows communication of this server with other servers or services.
php admin/cli/cfg.php --name=mnet_dispatcher_mode --set=off

# KeyboardEvent
# The default keyboard shortcut for local Commander plugin.
php admin/cli/cfg.php --component=local_commander --name=keys --set=32

# Plugin Skel
php admin/cli/cfg.php --component=tool_pluginskel --name=copyright --set=""`date +"%Y"`" KnowledgeOne <nicolas.dalpe@knowledgeone.ca>"
php admin/cli/cfg.php --component=tool_pluginskel --name=version --set=""`date +"%Y%0m%0d"`"00"
