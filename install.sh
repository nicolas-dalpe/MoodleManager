python3 mm.py create db_ec_moodle310

# If !config.php
php admin/cli/install.php --lang=en --wwwroot=https://moodle.local --dataroot=/var/www/md_ec_moodle310 --fullname=Sandbox --shortname=sb --adminuser=admin --adminpass=Abc123Def456 --adminemail=nicolas.dalpe@knowledgeone.ca --agree-license=yes

# config.php
php admin/cli/install_database.php --fullname=Sandbox --shortname=Sandbox --lang=en --adminuser=admin --adminpass=Abc123\!\@\# --adminemail=admin.user@knowledgeone.ca --agree-license=yes

# Moosh commands
moosh course-create --category 1 --fullname "QR Code" QRC
moosh user-create --password Abc123\!\@\# --email nicolas.dalpe@knowledgeone.ca --digest 2 --city Montreal --country CA --firstname "Nicolas" --lastname "Dalpe" nicolas.dalpe
moosh course-enrolbyname -r editingteacher -f nicolas -l dalpe -c QRC

moosh user-create --password Abc123\!\@\# --email student1@knowledgeone.ca --digest 2 --city Montreal --country CA --firstname "Student" --lastname "One" student1
moosh user-create --password Abc123\!\@\# --email student2@knowledgeone.ca --digest 2 --city Montreal --country CA --firstname "Student" --lastname "Two" student2
moosh course-enrol 3 student1 student2