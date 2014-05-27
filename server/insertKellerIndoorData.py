#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Insert Keller indoor data into the database from a tab-separated
data file.

Usage:
insertKellerIndoorData.py [--email] [--testing]
"""

__author__ = 'David Wilkie & Reed Shinsato'
__copyright__ = 'Copyright (c) 2014, University of Hawaii Smart Energy Project'
__license__ = 'https://raw.github' \
              '.com/Hawaii-Smart-Energy-Project/Maui-Smart-Grid/master/BSD' \
              '-LICENSE.txt'

import csv
import sys
import os
import subprocess
import shutil
from msg_db_connector import MSGDBConnector
from msg_db_util import MSGDBUtil
from msg_notifier import MSGNotifier
from msg_configer import MSGConfiger
from msg_logger import MSGLogger
import argparse

commandLineArgs = None
logger = MSGLogger(__name__, 'debug')

def processCommandLineArguments():
    global argParser, commandLineArgs, filename
    argParser = argparse.ArgumentParser(
        description = 'Perform insertion of Meter Location History contained '
                      'in the file given by --filename to the MECO database '
                      'specified in the configuration file.')
    argParser.add_argument('--email', action = 'store_true', default = False,
                           help = 'Send email notification if this flag is '
                                  'specified.')
    argParser.add_argument('--testing', action = 'store_true', default = False,
                           help = 'If this flag is on, '
                                  'insert data to the testing database as '
                                  'specified in the local configuration file.')
    commandLineArgs = argParser.parse_args()

def getCSVFilenames():
    """Returns a list of strings of filenames of each CSV in working dir."""
    output = subprocess.Popen(['ls'],stdout = subprocess.PIPE, 
             stderr = subprocess.STDOUT, shell = True).communicate()[0]
    #split the string by lines
    output = output.split('\n')
    fileNames = []

    for line in output:
        line = line.split(' ')
        #for each element find the file name of the files in that folder with the
        #extension *.txt
        for element in line:
            if '.csv' in element or '.CSV' in element:
                #if you found a valid filename, put it in a list
                fileNames.append(element)

    return fileNames

if __name__ == '__main__':

    processCommandLineArguments()

    workingDir = os.chdir('/usr/local/smb-share/1.Projects/1.12.NaturalVentilation/Keller_indoor_csv_files/')

    fileNames = getCSVFilenames()
    success = True
    anyFailure = False
    connector = MSGDBConnector(testing = commandLineArgs.testing)
    conn = connector.connectDB()
    cur = conn.cursor()
    dbUtil = MSGDBUtil()
    notifier = MSGNotifier()
    msgBody = ''
    configer = MSGConfiger()

    if commandLineArgs.testing:
        dbName = configer.configOptionValue("Database", "testing_db_name")
    else:
        dbName = "natural_ventilation"

    cols = ["datetime", "position", "value"]

    # for each file in the list of found files
    for filename in fileNames:
        msg = ("Loading Keller indoor data in file %s to database %s.\n" % (
            filename, dbName))
        sys.stderr.write(msg)
        msgBody += msg

        f = open(filename, "r")
        reader = csv.reader(f)
        data = []
        lineCnt = 0

        with open(filename, "rU") as csvFile:
            for line in csv.reader(csvFile, delimiter = ","):
                if lineCnt != 0: # Skip header.
                    data = line[0:len(cols)] # Overshoot columns to get the last column.

                    for i in range(0, len(cols)):
                        if len(data[i]) == 0:
                            data[i] = 'NULL'
                        else:
                            # Escape single quotes with double single quotes in
                            # PostgreSQL.
                            data[i] = data[i].replace("'", "\'\'")
                            data[i] = "'" + data[i] + "'"

                    sql = """INSERT INTO "keller_indoor_data" (%s) VALUES (%s)""" % (
                        ','.join(cols), ','.join(data))
                    success = dbUtil.executeSQL(cur, sql)
                    if not success:
                        anyFailure = True

                lineCnt += 1
        conn.commit()
        msg = ("Processed %s lines.\n" % lineCnt)
        lineCnt = 0
        sys.stderr.write(msg)
        msgBody += msg
        shutil.move(filename, workingDir + '/archive/' + filename)

    if not anyFailure:
        msg = "Finished inserting Keller indoor data records.\n"
        sys.stderr.write(msg)
        msgBody += msg
    else:
        msg = "Keller indoor data records were NOT successfully loaded.\n"
        sys.stderr.write(msg)
        msgBody += msg

    if commandLineArgs.email:
        notifier.sendNotificationEmail(msgBody, testing = commandLineArgs.testing)
