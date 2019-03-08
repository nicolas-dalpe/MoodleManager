import getpass
import MySQLdb as db
import os
import sys
import tarfile
import shutil


class mm(object):
    """Moodle Manager"""

    # Current working directory
    wd = os.getcwd()

    # Default database directory
    dDir = os.path.join(os.getcwd(), 'backup/database')

    # Default vagrant directory
    vDir = "/home/ndalpe/w/stretch64"

    # Default git repository directory
    rDir = "/home/ndalpe/w/Repositories"

    # color code \x1b[38;2;R;G;Bm
    CRED = "\x1b[38;2;176;0;32m"
    CBLUE = "\x1b[38;2;36;123;160m"
    CLBLUE = "\x1b[38;2;208;244;234m"
    CGREEN = "\x1b[38;2;58;125;68m"
    CEND = "\x1b[0m"

    def __init__(self, args):

        # initialize the utilities class
        # contains various usefull method
        self.utils = utils()

        # if not arguments given, print help
        if len(args) == 1:
            self.print_help()
        elif len(args) > 1:
            if args[1] == "create":
                self.create(args)
            elif args[1] == "export":
                self.export(args)
            elif args[1] == "fix":
                self.fix(args)
            elif args[1] == "fixutf":
                self.fixutf(args)
            elif args[1] == "plugin":
                self.plugin(args)

    def print_help(self):
        print("\n")

        self.utils.print_msg("create database [import] [archive]", self.CBLUE)
        self.utils.print_msg("\tCreate an utf8mb4 database and import a SQL dump if import is specified")
        self.utils.print_msg("\tdatabase : Database name", self.CLBLUE)
        self.utils.print_msg("\timport   : Import SQL switch.", self.CLBLUE)
        self.utils.print_msg("\tarchive  : File to import (without .sql.tar.gz)", self.CLBLUE)
        self.utils.print_msg("                   Default backup/database/database.sql.tar.gz\n", self.CLBLUE)

        self.utils.print_msg("export database [archive]", self.CBLUE)
        self.utils.print_msg("\tExport the content of a database into a SQL file and compress it")
        self.utils.print_msg("\tdatabase : Database name", self.CLBLUE)
        self.utils.print_msg("\tarchive  : Archive file name. Default is database name.\n", self.CLBLUE)

        self.utils.print_msg("fixutf [SQL file]", self.CBLUE)
        self.utils.print_msg("\tFind and replace the varchar(x) column with a varchar(190)")
        self.utils.print_msg("\tSQL File : The SQL file to F&R in /backup/database\n", self.CLBLUE)

        self.utils.print_msg("fix", self.CBLUE)
        self.utils.print_msg("\tFix Database collation, compress rows and clear MOODLE's cache\n")

        self.utils.print_msg("plugin [force]", self.CBLUE)
        self.utils.print_msg("\tInstall missing plugin from Github and add them to .gitignore")
        self.utils.print_msg("\tforce : Delete plugin if it exists \n", self.CLBLUE)

    def create(self, args):
        """ python3 cdb.py create dbname import archive"""

        dbName = args[2]

        # get a MySQL connection
        cursor = self.utils.getDbConn(dbName)

        self.utils.print_status("Setting innodb_default_row_format")
        cursor.execute("SET GLOBAL innodb_default_row_format = DYNAMIC;")

        self.utils.print_status("Setting collation_server")
        cursor.execute("SET GLOBAL collation_server = utf8mb4_unicode_ci;")

        self.utils.print_status("Setting collation_database")
        cursor.execute("SET GLOBAL collation_database = utf8mb4_unicode_ci;")

        self.utils.print_status("Setting collation_connection")
        cursor.execute("SET GLOBAL collation_connection = utf8mb4_unicode_ci;")

        self.utils.print_status("Setting innodb_file_format")
        cursor.execute("SET GLOBAL innodb_file_format=Barracuda;")

        self.utils.print_status("Setting innodb_file_per_table")
        cursor.execute("SET GLOBAL innodb_file_per_table=1;")

        self.utils.print_status("Setting innodb_large_prefix")
        cursor.execute("SET GLOBAL innodb_large_prefix=1;")

        self.utils.print_status("Droping database {}.".format(dbName))
        cursor.execute("DROP DATABASE IF EXISTS " + dbName + ";")
        self.utils.print_status("Database {} dropped.".format(dbName))

        self.utils.print_status("Creating database {}.".format(dbName))
        cursor.execute("CREATE DATABASE " + dbName + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        self.utils.print_status("Database {} created.".format(dbName))

        if args[3] == "import":
            self.utils.print_status("Starting import of {}".format(args[2]))

            # tar version of the MySQL dump to import
            archive = args[4] + '.sql.tar.gz'

            # if the file exists, extract it from the archive
            if os.path.isfile(os.path.join(self.dDir, archive)):
                self.utils.print_status("Deflate {}".format(archive))
                os.chdir(self.dDir)
                tf = tarfile.open(archive)
                dumpFile = tf.getnames()[0]
                tf.extractall()

                # import the extracted dump file into the database
                self.utils.print_status("Importing {} into {}".format(dumpFile, dbName))
                os.system("mysql -u{} -p{} {} < {}".format(self.dbUserName, self.dbPassword, dbName, os.path.join(self.dDir, dumpFile)))

                # remove the imported SQL dump file
                if os.path.isfile(dumpFile):
                    os.remove(dumpFile)
            else:
                self.utils.print_error("Archive not found. " + archive)

    def export(self, args):
        """ ./cdb.sh export database [archive] """

        # define dababase name
        dbName = args[2]

        # define archive name, if not supplied use database name as archive name
        if len(args) < 4:
            archive = args[2]
        else:
            archive = args[3]

        archive += ".sql"

        # define dump file with full path
        dFile = os.path.join(self.dDir, archive)

        # get a MySQL connection
        cursor = self.utils.getDbConn(dbName)

        # output moodle database as backup
        self.utils.print_status("Starting: MySQL Dump")
        os.system("mysqldump --user=" + self.dbUserName + " --password=" + self.dbPassword + " " + dbName + " --opt --no-create-db > " + dFile)

        self.utils.print_status("Starting: Compress {}".format(archive))

        # Change working dir
        os.chdir(self.dDir)

        # Compress MySQL dump
        dump = tarfile.open(archive + ".tar.gz", mode='w:gz')
        try:
            self.utils.print_msg("    Adding {}".format(archive))
            dump.add(archive)
        finally:
            self.utils.print_msg("    Closing {}".format(archive))
            dump.close()

        # Delete the .sql dump file
        if os.path.isfile(archive):
            os.remove(archive)

        self.utils.print_status("Task Completed")

        # list the backup/database folder
        os.system("ls -l {}".format(self.dDir))

    def fix(self, args):
        """
        Fix Character encoding and row compression in a MySQL database
        """
        self.utils.print_status("Fixing collation")
        os.system("/usr/bin/php {} --collation=utf8mb4_unicode_ci".format(
            os.path.join(self.wd, "admin/cli/mysql_collation.php")
        ))

        self.utils.print_status("Compressing rows")
        os.system("/usr/bin/php {} --fix".format(
            os.path.join(self.wd, "admin/cli/mysql_compressed_rows.php")
        ))

        self.utils.print_status("Clearing Moodle's cache")
        os.system("/usr/bin/php {}".format(
            os.path.join(self.wd, "admin/cli/purge_caches.php")
        ))

    def fixutf(self, args):
        """
        Fix varchar() column in the export.sql before importing it
        Set all varchar(>190) to varchar(190) to avoid key length error when importing in MySQL/MariaDB
        $1 refers to the file name argument passed to the function
        ./cdb.sh fixutf would set $db to default value: export.sql
        ./cdb.sh fixutf kpmy.sql would set $db to kpmy.sql
        """

        # convert the args into a dictionary
        param = self.utils.cargs(args)

        # use default file name if none is passed
        if 2 in param:
            db = param[2] + ".sql"
        else:
            db = "export.sql"

        # join the default database dir with the SQL dump file
        dFile = os.path.join(self.dDir, db)

        if os.path.isfile(dFile):
            print("\nStatus ==> varchar(1333)")
            self.utils.print_status("F+R varchar(1333)")
            os.system("sed -i 's/varchar(1333) COLLATE utf8mb4_unicode_ci/varchar(190) COLLATE utf8mb4_unicode_ci/g' " + dFile)
            self.utils.print_status("F+R varchar(255)")
            os.system("sed -i 's/varchar(255) COLLATE utf8mb4_unicode_ci/varchar(190) COLLATE utf8mb4_unicode_ci/g' " + dFile)
            self.utils.print_status("F+R varchar(200)")
            os.system("sed -i 's/varchar(200) COLLATE utf8mb4_unicode_ci/varchar(190) COLLATE utf8mb4_unicode_ci/g' " + dFile)
            self.utils.print_status("ROW_FORMAT=COMPRESSED")
            os.system("sed -i 's/ROW_FORMAT=COMPRESSED/ROW_FORMAT=DYNAMIC/g' " + dFile)
        else:
            self.utils.print_error("SQL file not found")

    def plugin(self, args):
        """
        Install all plugin from Github
        """

        # convert the args into a dictionary
        param = self.utils.cargs(args)

        # Force switch
        force = False
        if 2 in param:
            if param[2] == 'force':
                force = True

        # define the dictionary of plugin
        plugins = {
            'kpdesktop': {
                'url': "git@github.com:ndalpe/kpdesktop.git",
                'path': 'theme/kpdesktop',
                'branch': 'master'
            },
            'iomadfollowup': {
                'url': 'git@github.com:ndalpe/studentsfollowup.git',
                'path': 'report/iomadfollowup',
                'branch': 'master'
            },
            'iomadanalytics': {
                'url': 'git@github.com:ndalpe/iomadanalytics.git',
                'path': 'report/iomadanalytics',
                'branch': 'master'
            },
            'multilang2': {
                'url': 'git@github.com:iarenaza/moodle-filter_multilang2.git',
                'path': 'filter/multilang2',
                'branch': 'master'
            },
            'deferredallnothing': {
                'url': 'git@github.com:dthies/moodle-qbehaviour_deferredallnothing.git',
                'path': 'question/behaviour/deferredallnothing',
                'branch': 'master'
            },
            'filtered_course_list': {
                'url': 'git@github.com:CLAMP-IT/moodle-blocks_filtered_course_list.git',
                'path': 'blocks/filtered_course_list',
                'branch': 'master'
            }
        }

        for pluginName, pluginInfo in plugins.items():
            # Get the plugin abs path
            pluginPath = os.path.join(self.wd, pluginInfo['path'])

            # Test if the plugin is already installed
            if not os.path.isdir(pluginPath):
                self.utils.install_plugin(pluginName, pluginInfo)
            elif os.path.isdir(pluginPath) and force:
                shutil.rmtree(pluginPath)
                self.utils.install_plugin(pluginName, pluginInfo)
            else:
                self.utils.print_status("Skipping " + pluginName)


class utils(mm):
    def __init__(self):
        pass

    def print_error(self, msg):
        """
        Print red error message
        """
        print(self.CRED + msg + self.CEND)

    def print_status(self, msg):
        """
        Print red error message
        """
        print("\n" + self.CGREEN + "Status ==> " + self.CEND + msg)

    def print_msg(self, msg, color=False):
        """
        Print a colored message
        """
        if len(msg) > 0:
            if not color:
                print(msg)
            else:
                print(color + msg + self.CEND)

    def getDbConn(self, dbName=""):
        """
        Get a database connect and return cursor
        """
        self.dbUserName = input("Please enter MySQL username: ")
        self.dbPassword = getpass.getpass('Please enter MySQL password:')

        if dbName != "":
            MySQL = db.connect(user=self.dbUserName, passwd=self.dbPassword)
        else:
            MySQL = db.connect(user=self.dbUserName, passwd=self.dbPassword, db=dbName)

        return MySQL.cursor()

    def cargs(self, args):
        """
        Convert the args list into a dictionary
        """
        dictArgs = {i: args[i] for i in range(0, len(args))}
        return dictArgs

    def install_plugin(self, pluginName, pluginInfo):
        """
        Install plugin
        """
        self.print_status("Installing " + pluginName)

        os.system("git clone {} {}".format(pluginInfo['url'], pluginInfo['path']))

        if pluginInfo['branch'] != 'master':
            self.print_status("Tracking {}".format(pluginInfo['branch']))

            os.chdir(os.path.join(self.wd, pluginInfo['path']))
            os.system("git branch --track {} origin/{}".format(pluginInfo['branch'], pluginInfo['branch']))

            self.print_status("Checking out " + pluginInfo['branch'])
            os.system("git checkout {}".format(pluginInfo['branch']))

            # set the cwd to the project's root
            os.chdir(self.wd)

        self.print_status("Ignoring {}\n\n".format(pluginName))
        os.system("echo {} >> .git/info/exclude".format(pluginInfo['path']))


a = mm(sys.argv)
