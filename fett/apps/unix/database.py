#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *


@decorate.debugWrap
@decorate.timeWrap
def install(target):
    # target is a fett target object
    outLog = ''
    # All we need to do is install sqlite into a suitable location,
    # like /usr/bin
    outLog += target.runCommand("echo \"Installing sqlite into /usr/bin...\"")[1]
    outLog += target.runCommand("install sqlite /usr/bin")[1]
    return outLog


@decorate.debugWrap
@decorate.timeWrap
def deploy(target):
    return ''

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    target.shutdownAndExit(f"\nNotYetImplemented: The extensive tests are not yet implemented.", exitCode=EXIT.Run)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    sqlite_bin = "/usr/bin/sqlite"
    xDb = 'test.db'
    target.switchUser()
    
    def create_database_and_table(pathToFile='/usr/bin', xFile='sqlite', xTable='food'):
        printAndLog(f"Test-create_database_and_table: Create sqlite {xDb} database and {xTable} table", doPrint=False)
        if target.doesFileExist(xFile=xFile, pathToFile=pathToFile, shutdownOnError=False):
            if getSetting('osImage') in ['debian', 'FreeBSD']:
                target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                                  endsWith="sqlite>")
                target.runCommand(f"CREATE VIRTUAL TABLE IF NOT EXISTS {xTable} USING fts3(title);",
                                  endsWith="sqlite>")
                target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")
                target.runCommand(".exit")
                printAndLog(f"Test-create_database_and_table: The {xDb} database and {xTable} table created successfully!",
                            doPrint=False)
        else:
            target.shutdownAndExit(f"\ncheckFile: Failed to find <{pathToFile}/{xFile}> on target.", exitCode=EXIT.Run)

    def insert_record(xTable='food', title_val='Pancakes'):
        printAndLog(f"Test-insert_record: Insert into  {xTable} table value {title_val}.", doPrint=False)
        if getSetting('osImage') in ['debian', 'FreeBSD']:
            target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                              endsWith="sqlite>")
            target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")
            target.runCommand(f"INSERT INTO {xTable}(title) VALUES('{title_val}');",
                              endsWith="sqlite>")
            target.runCommand(f"SELECT * from {xTable};", expectedContents=[f"{title_val}"], expectExact=True,
                              endsWith="sqlite>")
            target.runCommand(".exit")
            printAndLog(
                f"Test-insert_record: The value {title_val} has been successfully inserted into {xTable} table!",
                doPrint=False)

    def update_record(xTable='food', title_val='Pizza'):
        printAndLog(f"Test-update_record: Update the first record in the table {xTable}  - value {title_val}.",
                    doPrint=False)
        if getSetting('osImage') in ['debian', 'FreeBSD']:
            target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                              endsWith="sqlite>")
            target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")
            target.runCommand(f"SELECT * from {xTable};", expectExact='Pancakes', endsWith="sqlite>")

            target.runCommand(f"Update {xTable} SET title='{title_val}' WHERE title ='Pancakes';",
                              endsWith="sqlite>")
            target.runCommand(f"SELECT * from {xTable};", expectExact=True, expectedContents=[f"{title_val}"],
                              endsWith="sqlite>")
            target.runCommand(".exit")
            printAndLog(f"Test-update_record: The first record has been successfully updated - value {title_val}.",
                        doPrint=False)

    def delete_record(xTable='food', title_val='Pizza'):
        printAndLog(f"Test-delete_record: Delete {title_val} from the {xTable} table.", doPrint=False)
        if getSetting('osImage') in ['debian', 'FreeBSD']:
            target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                              endsWith="sqlite>")
            target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>")
            target.runCommand(f"SELECT * from {xTable};", expectExact=True, expectedContents=[f"{title_val}"],
                              endsWith="sqlite>")
            target.runCommand(f"DELETE FROM {xTable} WHERE title='{title_val}';",
                              endsWith="sqlite>")
            target.runCommand(f"SELECT * from {xTable};", expectedContents=[], endsWith="sqlite>")
            target.runCommand(".exit")
            printAndLog(
                f"Test-delete_record: The value {title_val} has been successfully deleted from the {xTable} table!",
                doPrint=False)

    def drop_table(xTable='food'):
        printAndLog(f"Test-drop_table: Drop {xTable} table", doPrint=False)
        retText = ''
        if getSetting('osImage') in ['debian', 'FreeBSD']:
            target.runCommand(f"{sqlite_bin} {xDb}", expectedContents=["SQLite version", ".help"],
                              endsWith="sqlite>")
            retText += \
                target.runCommand(".tables", expectedContents=[f"{xTable}"], endsWith="sqlite>", shutdownOnError=False,
                                  suppressErrors=True)[1]
            if not (f"{xTable}" in retText):
                target.runCommand(".exit")
                logging.info(f"Test-drop_table: Invalid input parameter table {xTable}. Provide valid table name.")
            else:
                target.runCommand(f"DROP TABLE IF EXISTS {xTable};", endsWith="sqlite>")
                target.runCommand(".tables", expectedContents=[], endsWith="sqlite>")
                target.runCommand(".exit")
                printAndLog(f"Test-drop_table: The {xTable} table has been dropped successfully!", doPrint=False)

    def drop_database(pathToFile='~'):

        printAndLog(f"Test-drop_database: Drop sqlite {xDb} database", doPrint=False)
        if target.doesFileExist(xFile=xDb, pathToFile=pathToFile, shutdownOnError=False):
            if getSetting('osImage') in ['debian', 'FreeBSD']:
                target.runCommand(f"rm -f {pathToFile}/{xDb}")
                printAndLog(f"Test-drop_database: Database {xDb} dropped successfully!", doPrint=False)
        else:
            target.shutdownAndExit(f"\ncheckFile: Failed to find <{pathToFile}/{xDb}> on target.", exitCode=EXIT.Run)

    create_database_and_table()
    insert_record()
    update_record()
    delete_record()
    drop_table(xTable='food1')
    drop_table()
    drop_database()
