# THIS SCRIPT WILL EXECUTE THE QUEIRIES BELOW TO PARSE OUT DATA FOR THE SELECTED APPLICATION.
# APPLICATION: TikTok Mobile for Android as of 2023-03-10
# DATABASES REQUIRED: [USER-ID-OF-ACCOUNT]_im.db, db_im_xx
#
#       /data/data/com.zhiliaoapp.musically/databases/[USER-ID-OF-ACCOUNT]_im.db
#       /data/data/com.zhiliaoapp.musically/databases/db_im_xx
#
# Version 1.0
# Date  2023-03-03
# Copyright (C) 2023 - Aaron Dee Roberts
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>

import sys
import os


# PROMPT TO INFORM WHAT DATABASES ARE NEEDED AND ASK TO PROCEED OR ABORT
response = input("This program requireds the following database files to proceed.  \nIf you don't have them press \"N\" to exit or any other key to proceed. \nYou will need to input the user id of the account (the long number of the _im.db file)\n   DATABASE:  [USER-ID-OF-ACCOUNT]_im.db \n   DATABASE:  db_im_xx\n\nINPUT: ")

if response == "N" or response == "n": 
    print('"N" selected, aborting')
    sys.exit(0)

response = "" #RESET THE RESPONSE
print("Proceeding with the operation.\n")
print()
user_account_id = input('Plese provide the user id (number portiof the table ending in "_im.db").  If you do not have it, press "N" to abort.\n  INPUT:  ')

if user_account_id == "N" or user_account_id == "n": 
    print('"N" selected, aborthing')
    sys.exit(0)

# ASSIGN THE NAME OF THE DATABASE DISPLAY AND MAKE SURE THEY EXIST
account_database = user_account_id + "_im.db"
name_database = "db_im_xx"
print(f"Using database:  {account_database}")
print(f"Using database:  {name_database}")

if os.path.isfile(account_database) is True:
    print(f'Checking if {account_database} exists.  It DOES exist so proceeding.')
    print()
else:
    print(f'Checking if {account_database} exists.  It does NOT exist so exiting.')
    print('You may want to check the spelling of that file name.')
    sys.exit(0)

if os.path.isfile(name_database) is True:
    print(f'Checking if {name_database} exists.  It DOES exist so proceeding.')
    print()
else:
    print(f'Checking if {name_database} exists.  It does NOT exist so exiting.')
    print('You NEED this database to connect all the relevant tables and fields.')
    sys.exit(0)

# SETTING UP LOGGING TO BE ABLE TO LOG ACTIONS
import logging
level    = logging.INFO
format   = '%(message)s'
handlers = [logging.FileHandler(user_account_id + '_TikTok_Messages.log'), logging.StreamHandler()]
logging.basicConfig(level = level, format = format, handlers = handlers)

#GET DATE AND TIME FOR LOGGING
import datetime
now = datetime.datetime.now()
# USAGE: # print (now.strftime("%Y-%m-%d %H:%M:%S LT"))

print('Starting the log file')
logging.info(f'Starting log for parsing of files {account_database} and {name_database}.')
logging.info(now.strftime('Time started:  %Y-%m-%d %H:%M:%S LT'))
logging.info('')

# sys.exit(0) #HERE FOR TESTING
import sqlite3
con = sqlite3.connect(user_account_id + '_TikTok_Messages.db')

con.row_factory = sqlite3.Row
cur = con.cursor()

# ATTACH THE DATABASE FOR THE MESSAGES AND PARTICIPANTS
logging.info(f'Attaching database {user_account_id}_im.db to access it\'s tables')
sqlquery = """ATTACH DATABASE '""" + user_account_id + """_im.db' AS tt_user_account_id_im"""
cur.execute(sqlquery)
logging.info(f'Executed: \n{sqlquery}')
logging.info('')

# ATTACH THE TABLE FOR THE HUMAN READABLE IDENTIFIERS (NAMES AND NICK NAMES)
logging.info('Attaching database db_im_xx to access it\'s tables')
sqlquery = """ATTACH DATABASE 'db_im_xx' as tt_db_im_xx"""
cur.execute(sqlquery)
logging.info(f'Executed: \n{sqlquery}')
logging.info('')

# CREATE A TABLE WITH THE MESSAGES AND USER ID COMBINED
logging.info('Matching the unique id and nick names to message user id in the Messages table')
sqlquery = """CREATE TABLE 'comb_message_user' AS \
SELECT  \
tt_user_account_id_im.msg.msg_uuid AS msg_uuid, tt_user_account_id_im.msg.conversation_id AS conversation_id,  \
tt_user_account_id_im.msg.created_time AS created_time, tt_user_account_id_im.msg.sender AS msg_sender_id,  \
tt_user_account_id_im.msg.content AS msg_content, tt_user_account_id_im.msg.ext AS msg_ext, \
tt_user_account_id_im.msg.local_info AS msg_local_info, tt_user_account_id_im.msg.read_status AS read_status,  \
tt_user_account_id_im.msg.sec_sender AS msg_sec_senderm, \
tt_db_im_xx.SIMPLE_USER.UID AS user_user_uid, tt_db_im_xx.SIMPLE_USER.NICK_NAME AS user_sender_nick_name,  \
tt_db_im_xx.SIMPLE_USER.UNIQUE_ID AS user_unique_id, tt_db_im_xx.SIMPLE_USER.SIGNATURE AS user_signature, \
tt_db_im_xx.SIMPLE_USER.AVATAR_THUMB AS user_thumb \
FROM tt_user_account_id_im.msg \
LEFT JOIN tt_db_im_xx.SIMPLE_USER \
ON tt_user_account_id_im.msg.sender = tt_db_im_xx.SIMPLE_USER.UID \
ORDER BY tt_user_account_id_im.msg.created_time"""
cur.execute(sqlquery)
con.commit()
logging.info(f'Executed: \n{sqlquery}')
logging.info('')

# CREATE A TABLE GIVING NAMES TO THE PARTICIPANTS 
logging.info('Matchin the unique id and nick name with user ids in the participants table')
sqlquery = """CREATE TABLE 'comb_user_participant' AS \
SELECT \
tt_user_account_id_im.participant.conversation_id AS participant_conversation_id, \
tt_user_account_id_im.participant.user_id AS participant_id, \
tt_db_im_xx.SIMPLE_USER.UID AS user_user_uid, tt_db_im_xx.SIMPLE_USER.NICK_NAME AS user_sender_nick_name,  \
tt_db_im_xx.SIMPLE_USER.UNIQUE_ID AS user_unique_id, tt_db_im_xx.SIMPLE_USER.SIGNATURE AS user_signature, \
tt_db_im_xx.SIMPLE_USER.AVATAR_THUMB AS user_thumb \
FROM tt_user_account_id_im.participant \
LEFT JOIN tt_db_im_xx.SIMPLE_USER \
ON tt_user_account_id_im.participant.user_id = tt_db_im_xx.SIMPLE_USER.UID"""
cur.execute(sqlquery)
con.commit()
logging.info(f'Executed: \n{sqlquery}')
logging.info('')

# CREATE A PARTICIPANTS LIST FOR EACH CONVERSATION
logging.info('Combingin participants with uniqu id and nick name for concatinating.  This will allow the participant list for each message.')
sqlquery = """CREATE TABLE 'concat_participants' AS \
SELECT \
comb_user_participant.participant_conversation_id,  \
GROUP_CONCAT(comb_user_participant.user_unique_id, ', ') AS participants \
FROM comb_user_participant \
GROUP BY comb_user_participant.participant_conversation_id \
ORDER BY comb_user_participant.participant_conversation_id"""
cur.execute(sqlquery)
con.commit()
logging.info(f'Executed: \n{sqlquery}')
logging.info('')

# LIST THE MESSAGES WITH THE SENDER AND PARTICIPANTS ALL INCLUDED IN A NEW TABLE
logging.info('Generating the final table containing the messages with names and participant lists.')
sqlquery = """CREATE TABLE 'comb_tiktok_messages' AS \
SELECT \
datetime(comb_message_user.created_time/1000,'unixepoch') AS created_time, comb_message_user.user_sender_nick_name || ' (' || comb_message_user.user_unique_id || ')' AS sender, \
concat_participants.participants, comb_message_user.msg_content AS content \
FROM comb_message_user \
LEFT JOIN concat_participants \
ON comb_message_user.conversation_id = concat_participants.participant_conversation_id \
ORDER BY comb_message_user.created_time"""
cur.execute(sqlquery)
con.commit()
logging.info(f'Executed: \n{sqlquery}')
logging.info('')

logging.info(now.strftime('Time finished:  %Y-%m-%d %H:%M:%S LT'))
logging.info('')
logging.info(f'Final product in the table "comb_tiktok_messages" within the file "{user_account_id}_TikTok_Messages.db".')
logging.info(f'Log stored as "{user_account_id}_TikTok_Messages.log"')

print()
print(f'If you did not get any error messages, your decoded messages will be in the table "comb_tiktok_messages"\nwithin the database {user_account_id}_TikTok_Messages.  \nA log file with the same name with the added "_log.txt" is with the new database file.')
print()



