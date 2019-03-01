import getpass
import MySQLdb as db
import os
import sys
import tarfile


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

    CBLACK = "\33[30m"
    CRED = "\33[31m"
    CGREEN = "\33[32m"
    CYELLOW = "\33[33m"
    CBLUE = "\33[34m"
    CVIOLET = "\33[35m"
    CBEIGE = "\33[36m"
    CWHITE = "\33[37m"
    CEND = "\033[0m"

    def __init__(self, args):
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

    def print_help(self):
        print("\n")

        print("./cdb.py create database [import] [archive]")
        print(self.CWHITE + "\tcreate   : Create an utf8mb4 database" + self.CEND)
        print(self.CWHITE + "\tdatabase : Database name" + self.CEND)
        print(self.CWHITE + "\timport   : Import SQL switch." + self.CEND)
        print(self.CWHITE + "\tarchive  : File to import (without .sql.tar.gz)" + self.CEND)
        print(self.CWHITE + "                   Default backup/database/database.sql.tar.gz\n" + self.CEND)

        print("./cdb.py export database [archive]")
        print(self.CWHITE + "\texport   : Export the database in SQL format and tar it" + self.CEND)
        print(self.CWHITE + "\tdatabase : Database name" + self.CEND)
        print(self.CWHITE + "\tarchive  : Archive file. Default is database name.\n" + self.CEND)

        print("./cdb.py fixutf [SQL file]")
        print(self.CWHITE + "\tF&R the varchar(x) column with a varchar(190)" + self.CEND)
        print(self.CWHITE + "\tSQL File : The SQL file to F&R in /backup/database\n" + self.CEND)

        print("./cdb.py fix")
        print("\tFix Database collation, compress rows and clear MOODLE's cache\n")

    def print_error(self, msg):
        """
        Print red error message
        """
        print(self.CRED + msg + self.CEND)

    def getDbConn(self, dbName=""):
        """ Get a database connect and return cursor """
        self.dbUserName = input("Please enter MySQL username: ")
        self.dbPassword = getpass.getpass('Please enter MySQL password:')

        if dbName != "":
            MySQL = db.connect(user=self.dbUserName, passwd=self.dbPassword)
        else:
            MySQL = db.connect(user=self.dbUserName, passwd=self.dbPassword, db=dbName)

        return MySQL.cursor()

    def create(self, args):
        """ python3 cdb.py create dbname import archive"""

        dbName = args[2]

        # get a MySQL connection
        cursor = self.getDbConn(dbName)

        print("Status ==> Setting innodb_default_row_format")
        cursor.execute("SET GLOBAL innodb_default_row_format = DYNAMIC;")

        print("Status ==> Setting collation_server")
        cursor.execute("SET GLOBAL collation_server = utf8mb4_unicode_ci;")

        print("Status ==> Setting collation_database")
        cursor.execute("SET GLOBAL collation_database = utf8mb4_unicode_ci;")

        print("Status ==> Setting collation_connection")
        cursor.execute("SET GLOBAL collation_connection = utf8mb4_unicode_ci;")

        print("Status ==> Setting innodb_file_format")
        cursor.execute("SET GLOBAL innodb_file_format=Barracuda;")

        print("Status ==> Setting innodb_file_per_table")
        cursor.execute("SET GLOBAL innodb_file_per_table=1;")

        print("Status ==> Setting innodb_large_prefix")
        cursor.execute("SET GLOBAL innodb_large_prefix=1;")

        print("Status ==> Droping database {}.".format(dbName))
        cursor.execute("DROP DATABASE IF EXISTS " + dbName + ";")
        print("Status ==> Database {} dropped.".format(dbName))

        print("Status ==> Creating database {}.".format(dbName))
        cursor.execute("CREATE DATABASE " + dbName + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("Status ==> Database {} created.".format(dbName))

        if args[3] == "import":
            print("Status ==> Starting import of {}".format(args[2]))

            # tar version of the MySQL dump to import
            archive = args[4] + '.sql.tar.gz'

            # if the file exists, extract it from the archive
            if os.path.isfile(os.path.join(self.dDir, archive)):
                print("Status ==> Deflate {}".format(archive))
                os.chdir(self.dDir)
                tf = tarfile.open(archive)
                dumpFile = tf.getnames()[0]
                tf.extractall()

                # import the extracted dump file into the database
                print("Status ==> Importing {} into {}".format(dumpFile, dbName))
                os.system("mysql -u{} -p{} {} < {}".format(self.dbUserName, self.dbPassword, dbName, os.path.join(self.dDir, dumpFile)))

                # remove the imported SQL dump file
                if os.path.isfile(dumpFile):
                    os.remove(dumpFile)
            else:
                print("Status ==> Archive not found")

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
        cursor = self.getDbConn(dbName)

        # output moodle database as backup
        print("==> Starting: MySQL Dump")
        os.system("mysqldump --user=" + self.dbUserName + " --password=" + self.dbPassword + " " + dbName + " --opt --no-create-db > " + dFile)

        print("==> Starting: Compress {}".format(archive))

        # Change working dir
        os.chdir(self.dDir)

        # Compress MySQL dump
        dump = tarfile.open(archive + ".tar.gz", mode='w:gz')
        try:
            print("    Adding {}".format(archive))
            dump.add(archive)
        finally:
            print("    Closing {}".format(archive))
            dump.close()

        # Delete the .sql dump file
        if os.path.isfile(archive):
            os.remove(archive)

        print("==> Task Completed")

        # list the backup/database folder
        os.system("ls -l {}".format(self.dDir))

    def fix(self, args):
        """
        Fix Character encoding and row compression in a MySQL database
        """
        os.system("/usr/bin/php {} --collation=utf8mb4_unicode_ci".format(
            os.path.join(self.wd, "admin/cli/mysql_collation.php")
        ))

        print("\n\nStatus ==> Compressing rows")
        os.system("/usr/bin/php {} --fix".format(os.path.join(self.wd, "admin/cli/mysql_compressed_rows.php")))

        print("\n\nStatus ==> Clearing Moodle's cache")
        os.system("/usr/bin/php {}".format(os.path.join(self.wd, "admin/cli/purge_caches.php")))

    def cargs(self, args):
        """
        Convert the args list into a dictionary
        """
        dictArgs = {i: args[i] for i in range(0, len(args))}
        return dictArgs

    # Fix varchar() column in the export.sql before importing it
    # Set all varchar(>190) to varchar(190) to avoid key length error when importing in MySQL/MariaDB
    # $1 refers to the file name argument passed to the function
    # ./cdb.sh fixutf would set $db to default value: export.sql
    # ./cdb.sh fixutf kpmy.sql would set $db to kpmy.sql

    def fixutf(self, args):

        # convert the args into a dictionary
        param = self.cargs(args)

        # use default file name if none is passed
        if 2 in param:
            db = param[2] + ".sql"
        else:
            db = "export.sql"

        # join the default database dir with the SQL dump file
        dFile = os.path.join(self.dDir, db)

        if os.path.isfile(dFile):
            print("\n\nStatus ==> varchar(1333)")
            os.system("sed -i 's/varchar(1333) COLLATE utf8mb4_unicode_ci/varchar(190) COLLATE utf8mb4_unicode_ci/g' " + dFile)
            print("\n\nStatus ==> varchar(255)")
            os.system("sed -i 's/varchar(255) COLLATE utf8mb4_unicode_ci/varchar(190) COLLATE utf8mb4_unicode_ci/g' " + dFile)
            print("\n\nStatus ==> varchar(200)")
            os.system("sed -i 's/varchar(200) COLLATE utf8mb4_unicode_ci/varchar(190) COLLATE utf8mb4_unicode_ci/g' " + dFile)
            print("\n\nStatus ==> ROW_FORMAT=COMPRESSED")
            os.system("sed -i 's/ROW_FORMAT=COMPRESSED/ROW_FORMAT=DYNAMIC/g' " + dFile)
        else:
            self.print_error("SQL file not found")


a = mm(sys.argv)
