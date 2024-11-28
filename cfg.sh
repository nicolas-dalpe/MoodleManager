#############################################################################
# Those are the basic settings that should be run on a new Moodle instance. #
#############################################################################

# Declare the settings array
# This array contains all the Moodle settings to be set
# Look at the bottom of the file for plugin settings
declare -A settings


# https://stackoverflow.com/questions/918886/how-do-i-split-a-string-on-a-delimiter-in-bash


# Add instance of manual enrolment to new courses
php admin/cli/cfg.php --component=enrol_manual --name=defaultenrol --set=1

# Disable the guest enrolment methode.
php admin/cli/cfg.php --component=enrol_guest --name=defaultenrol --set=0

# Keep logs for (number of days)
# This specifies the length of time you want to keep logs about user activity.
# Logs that are older than this age are automatically deleted. It is best
# to keep logs as long as possible, in case you need them, but if you have
# a very busy server and are experiencing performance problems, then you may
# want to lower the log lifetime. Values lower than 30 are not recommended
# because statistics may not work properly.
php admin/cli/cfg.php --component=logstore_standard --name=loglifetime --set=60

# Disable course recycle bin.
settings["coursebinenable"]=0

# Disable category recycle bin.
settings["categorybinenable"]=0

# Automatically check for available updates
# If enabled, your site will automatically check for available updates
# for both Moodle code and all additional plugins. If there is a new update
# available, a notification will be sent to site admins.
settings["updateautocheck"]=0

# Notify about new builds
# If enabled, the available update for Moodle code is also reported when a
# new build for the current version is available. Builds are continuous
# improvements of a given Moodle version. They are generally released every week.
# If disabled, the available update will be reported only when there is a
# higher version of Moodle released. Checks for plugins are not affected by this setting.
settings["updatenotifybuilds"]=0

# Allow course themes
# If enabled, then courses will be allowed to set their own themes.
# Course themes override all other theme choices
# (site, user, category, cohort or URL-defined themes).
settings["allowcoursethemes"]=1

# Allow guest access to Dashboard
# If enabled guests can access Dashboard, otherwise guests are
# redirected to the site front page.
settings["allowguestmymoodle"]=0

# Self registration
# If an authentication plugin, such as email-based self-registration,
# is selected, then it enables potential users to register themselves
# and create accounts. This results in the possibility of spammers
# creating accounts in order to use forum posts, blog entries etc. for spam.
settings["registerauth"]=''

# Force users to log in
# Normally, the front page of the site and the course listings (but not courses)
# can be read by people without logging in to the site. If you want to force
# people to log in before they do ANYTHING on the site,
# then you should enable this setting.
settings["forcelogin"]=1

# Default country
# If you set a country here, then this country will be selected by default
# on new user accounts. To force users to choose a country, just leave this unset.
settings["country"]='CA'

# Default city
# A city entered here will be the default city when creating new user accounts.
settings["defaultcity"]='Montreal'

# Default timezone
# This is the default timezone for displaying dates - each user can override
# this setting in their profile. Cron tasks and other server settings are
# specified in this timezone. You should change the setting if it shows
# as "Invalid timezone"
settings["timezone"]='America/Toronto'

# Guest Front page
# The items selected above will be displayed on the site's front page.
settings["frontpage"]='none'

# Guest login button
# You can hide or show the guest login button on the login page.
settings["guestloginbutton"]=0

# Open to search engines
# If you enable this setting, then search engines will be allowed to enter
# your site as a guest. In addition, people coming in to your site via a
# search engine will automatically be logged in as a guest. Note that this
# only provides transparent access to courses that already allow guest access.
settings["opentowebcrawlers"]=0

# Allow indexing by search engines
# This determines whether to allow search engines to index your site.
# "Everywhere" will allow the search engines to search everywhere including
# login and signup pages, which means sites with Force Login turned on are
# still indexed. To avoid the risk of spam involved with the signup page
# being searchable, use "Everywhere except login and signup pages".
# "Nowhere" will tell search engines not to index any page. Note this
# is only a tag in the header of the site. It is up to the search
# engine to respect the tag.
settings["allowindexing"]=2

# Cookie prefix sessioncookie
# This setting customises the name of the cookie used for Moodle sessions.
# This is optional, and only useful to avoid cookies being confused when
# there is more than one copy of Moodle running within the same web site.
settings["sessioncookie"]='sandbox_moodle4x'

# Automatically check for available updates
# If enabled, your site will automatically check for available updates for
# both Moodle code and all additional plugins. If there is a new update available,
# a notification will be sent to site admins.
settings["updateautocheck"]=0

# No-reply address
# Emails are sometimes sent out on behalf of a user (eg forum posts).
# The email address you specify here will be used as the "From" address
# in those cases when the recipients should not be able to reply directly
# to the user (eg when a user chooses to keep their address private).
# This setting will also be used as the envelope sender when sending email.
settings["noreplyaddress"]='no-reply@knowledgeone.ca'

# Support email
# If SMTP is configured on this site and a support page is not set,
# this email address will receive messages submitted through the support form.
# If sending fails, the email address will be displayed to logged-in users.
settings["supportemail"]='no-reply@knowledgeone.ca'


echo -e "\n"

for setting in "${!settings[@]}"
do
    php admin/cli/cfg.php --name=$setting --set=${settings[$setting]}
    echo -n "$setting is now set to: "
    php admin/cli/cfg.php --name=$setting
    echo -e "\n"
done

#####################################################
############   D E V   S E T T I N G S   ############
#####################################################

# Cache all language strings
# Caches all the language strings into compiled files in the data directory.
# If you are translating Moodle or changing strings in the Moodle source code
# then you may want to switch this off. Otherwise leave it on to see
# performance benefits.
# php admin/cli/cfg.php --name=langstringcache --set=0

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
#php admin/cli/cfg.php --name=mnet_dispatcher_mode --set=off

# Plugin Skel
php admin/cli/cfg.php --component=tool_pluginskel --name=copyright --set=""`date +"%Y"`"eConcordia <tech@knowledgeone.ca>"
php admin/cli/cfg.php --component=tool_pluginskel --name=version --set=""`date +"%Y%0m%0d"`"00"
echo admin/tool/pluginskel/ >> .git/info/exclude

# KeyboardEvent
# The default keyboard shortcut is the ` Backquote (above the TAB).
php admin/cli/cfg.php --component=local_commander --name=keys --set=12
echo local/commander/ >> .git/info/exclude

# Moodle Adminer
# Start adminer with current database
php admin/cli/cfg.php --component=local_adminer --name=startwithdb --set=1
echo local/adminer/ >> .git/info/exclude

# Exclude dev plugins from git
echo local/codechecker/ >> .git/info/exclude
echo local/moodlecheck/ >> .git/info/exclude
echo report/benchmark/ >> .git/info/exclude
echo moosh/ >> .git/info/exclude
