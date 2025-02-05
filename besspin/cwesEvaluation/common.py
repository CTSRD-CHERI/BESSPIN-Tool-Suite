import pexpect

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import scoreTests, prettyVulClass, tabulate

import besspin.cwesEvaluation.bufferErrors.vulClassTester
import besspin.cwesEvaluation.PPAC.vulClassTester
import besspin.cwesEvaluation.resourceManagement.vulClassTester
import besspin.cwesEvaluation.informationLeakage.vulClassTester
import besspin.cwesEvaluation.numericErrors.vulClassTester
import besspin.cwesEvaluation.hardwareSoC.vulClassTester
import besspin.cwesEvaluation.injection.vulClassTester
from besspin.cwesEvaluation.multitasking.multitasking import hasMultitaskingException, multitaskingRunner, logMultitaskingTable

cweTests = {
    "bufferErrors" :
        besspin.cwesEvaluation.bufferErrors.vulClassTester.vulClassTester,
    "PPAC" :
        besspin.cwesEvaluation.PPAC.vulClassTester.vulClassTester,
    "resourceManagement" :
        besspin.cwesEvaluation.resourceManagement.vulClassTester.vulClassTester,
    "informationLeakage" :
        besspin.cwesEvaluation.informationLeakage.vulClassTester.vulClassTester,
    "numericErrors" :
        besspin.cwesEvaluation.numericErrors.vulClassTester.vulClassTester,
    "hardwareSoC" :
        besspin.cwesEvaluation.hardwareSoC.vulClassTester.vulClassTester,
    "injection" :
        besspin.cwesEvaluation.injection.vulClassTester.vulClassTester,
}

@decorate.debugWrap
@decorate.timeWrap
def executeTest(target, vulClass, binTest, logDir):
    """
    Run a CWE test on a Unix OS.

    ARGUMENTS:
    ----------
    target : commonTarget
        Target to run the test on.

    vulClass : String
        Vulnerability class that the test belongs to.

    binTest : String
        Binary test file to execute.

    logDir : String
        Directory to write test output log tile to.

    SIDE-EFFECTS:
    -------------
        - Writes test output to <{logDir}/{testName}.log>, where <testName> is
          <binTest> with the ".riscv" extension removed.
        - Executes <binTest> on <target>.
    """
    testName = binTest.split('.')[0]
    printAndLog(f"Executing {testName}...", doPrint=(not isEnabledDict(vulClass,'useSelfAssessment')))
    outLog = cweTests[vulClass](target).executeTest(binTest)
    if ('\x1b' in outLog): #Something bad has happened
        warnAndLog("Encountered <ESC>. Will send a keyboard interrupt to be safe.",doPrint=False)
        outLog += target.keyboardInterrupt() #To re-adjust pexpect order
    logFileName = os.path.join(logDir, f'{testName}.log')
    logFile = ftOpenFile(logFileName, 'w')
    logFile.write(outLog)
    logFile.close()

@decorate.debugWrap
@decorate.timeWrap
def checkMultitaskingScores(vulClass, multitaskingScores, instance, multitaskingPasses):
    """
    Check whether multitasking CWE scores match scores from the sequential test
    run.

    ARGUMENTS:
    ----------
        vulClass : String
            The vulnerability class to check scores for.

        multitaskingScores : Dict of String to SCORES enum
            A mapping from CWE number to scores to check against the sequential
            test run.

        instance: Int
            The instance number of the multitasking test run the scores in
            <multitaskingScores> correspond to.

        multitaskingPasses : Dict of String to Int
            A mapping from test name to the number of instances of that test in
            multitasking runs that matched the score from the sequential run.
            Callers should pass the same <multitaskingPasses> dictionary in for
            each call to <checkMultitaskingScores>.

    SIDE-EFFECTS:
    -------------
        - Modifies <multitaskingPasses> with additional score results by
          either incrementing existing values, or inserting new dictionary
          entries.

    RETURNS:
    --------
        A list of tuples of (String, String, String, SCORES, SCORES, String).
        Each element of this list represents a multitasking score for an
        instance of a CWE test. In order, the elements of each tuple are:
            0. Pretty formatted vulnerability class name.
            1. Test name.
            2. Instance number (as a String).
            3. Sequential score.
            4. Multitasking score.
            5. Score text (either "PASS" or "FAIL").
    """
    results = []
    for cwe, score in getSettingDict("cweScores", vulClass).items():
        if hasMultitaskingException(vulClass, ["testsInfo", f"test_{cwe}"]):
            # Test doesn't run in multitasking mode
            continue
        try:
            multitaskingScore = multitaskingScores[cwe]
            if vulClass in ['bufferErrors', 'informationLeakage']:
                testName = f"CWE-{cwe}"
            else:
                testName = f"TEST-{cwe}"
            if multitaskingScore == score:
                multitaskingPasses[testName] = multitaskingPasses.get(testName, 0) + 1
                scoreText = "PASS"
            else:
                if testName not in multitaskingPasses:
                    # Record that the test ran but did not pass.
                    multitaskingPasses[testName] = 0
                scoreText = "FAIL"
            results.append((prettyVulClass(vulClass),
                            testName,
                            str(instance),
                            score,
                            multitaskingScore,
                            scoreText))
        except Exception as exc:
            logAndExit("<checkMultitaskingScores> Failed to check "
                       f"multitasking score for CWE <{cwe}>.",
                       exc=exc,
                       exitCode=EXIT.Dev_Bug)
    return results

@decorate.debugWrap
def appendMultitaskingColumn(vulClass, rows, multitaskingPasses):
    """
    Append a column containing multitasking scores to a table.

    ARGUMENTS:
    ----------
        vulClass : String
            The vulnerability class this table contains scores for.

        rows : List of List of String
            The rows of the table to modify.  Each element represents a row,
            and each element of each row represents a cell in that row.  The
            only requirement is that element 0 of each row be a CWE test name.

        multitaskingPasses : Dict of String to Int
            A mapping from test name to the number of instances of that test in
            multitasking runs that matched the score from the sequential run.
            Can be obtained from <checkMultitaskingScores>.

    SIDE-EFFECTS:
    -------------
        - Appends an additional String representing the percentage of
          multitasking tests that passed to the end of each element of <rows>.
          If the test  does not run under multitasking, this function appends
          "N/A" to the row.
    """
    for row in rows:
        testNameParts = row[0].split("-")
        testName = f"test_{'_'.join(testNameParts[1:])}"
        if (supportsMultitasking(vulClass) and
            not hasMultitaskingException(vulClass, ["testsInfo", testName])):
            try:
                percentPassed = (multitaskingPasses[row[0]] / getSetting("instancesPerTestPart")) * 100
            except Exception as exc:
                logAndExit("<appendMultitaskingColumn> Failed to find "
                           f"multitasking score for <{row[0]}>.",
                           exc=exc,
                           exitCode=EXIT.Dev_Bug)
            row.append(f"{percentPassed:.1f}%")
        else:
            row.append("N/A")

@decorate.debugWrap
def printTable(vulClass, table):
    """
    Print a score table to the screen, and also log it to disk.

    ARGUMENTS:
    ----------
        vulClass : String
            The vulnerability class this table contains scores for.

        table : List of List of String
            The table to print and log.  Each element represents a row,
            and each element of each row represents a cell in that row.

    SIDE-EFFECTS:
    -------------
        - Pretty prints <table> to the screen.
        - Appends pretty printed <table> to <${workDir}/scoreReport.log>.
    """
    rows = tabulate(table,
                    vulClass,
                    prettyVulClass(vulClass),
                    getSetting("runningMultitaskingTests"))
    reportFilePath = os.path.join(getSetting("workDir"), "scoreReport.log")
    fScoresReport = ftOpenFile(reportFilePath, 'a')
    for row in rows:
        printAndLog(row, tee=fScoresReport)
    fScoresReport.close()

@decorate.debugWrap
@decorate.timeWrap
def supportsMultitasking(vulClass):
    """
    Return whether or not <vulClass> supports multitasking tests.

    ARGUMENTS:
    ----------
        vulClass : String
            The vulnerability class to check multitasking support for.

    RETURNS:
    --------
        A boolean representing whether <vulClass> supports multitasking tests.
    """
    return (isEnabled('runUnixMultitaskingTests') and
            doesSettingExistDict(vulClass, 'supportsMultitasking') and
            isEnabledDict(vulClass, 'supportsMultitasking') and
            not isEnabledDict(vulClass, 'useSelfAssessment'))

def runTests(target, sendFiles=False, timeout=30): #executes the app
    """
    Run and score the CWE tests.  Also runs multitasking tests if
    ${runUnixMultitaskingTests} is enabled.

    ARGUMENTS:
    ----------
        target : commonTarget
            Target to run the tests on.

        sendFiles : Bool
            Whether to send ${tarballName} to <target> before executing tests.

        timeout : Int
            Timeout to use when sending ${tarballName}.  Ignored if <sendFiles>
            is <False>.

    SIDE-EFFECTS:
    -------------
        - Executes CWE test binaries on <target>.
        - If <sendFiles> is <True>, sends ${tarballName} to <target>.
        - Writes test output logs and score CSVs to ${logDir}.
        - Prints score tables to terminal.
        - Writes score report to <${workDir}/scoreReport.log>.
        - Writes multitasking score report to
          <${workDir}/multitaskingScoreReport.log>.
    """
    if isEqSetting('osImage', 'FreeRTOS'):
        test, vulClass, _, logFile = getSetting("currentTest")
        if (isEnabledDict(vulClass,'useSelfAssessment')):
            outLog = cweTests[vulClass](target).executeTest(test.replace('.c','.riscv'))
        else:
            # Extract test output
            textBack, wasTimeout, idxReturn = target.expectFromTarget(
                    [">>>End of Besspin<<<", pexpect.EOF],
                    "runCweTest",
                    exitOnError=False,
                    timeout=getSetting('FreeRTOStimeout'),
                    suppressWarnings=True)

            if idxReturn == 1:
                if isEqSetting('target', 'qemu'):
                    # No ">>> End Of Besspin <<<", but qemu aborted without a
                    # timeout
                    logFile.write(target.readFromTarget())
                    logFile.write("\n<QEMU ABORTED>\n")
                    return
                else:
                    target.terminateAndExit("<runTests> Unexpected EOF during "
                                           "test run.",
                                           exitCode=EXIT.Dev_Bug)
            if wasTimeout:
                logFile.write(target.readFromTarget())
                logFile.write("\n<TIMEOUT>\n")
                warnAndLog(f"{test} timed out.  Skipping.",doPrint=False)
                return
            outLog = textBack
        
        logFile.write(outLog)

    elif getSetting('osImage') in ['debian', 'FreeBSD']:
        # Create directory for logs
        baseLogDir = os.path.join(getSetting('workDir'), 'cwesEvaluationLogs')
        mkdir(baseLogDir, addToSettings="cwesEvaluationLogs")

        if sendFiles:
            target.sendTar(timeout=timeout)

        # Batch tests by vulnerability class
        sequentialTables = {}
        multitaskingTests = []
        for vulClass, tests in getSetting("enabledCwesEvaluations").items():
            logsDir = os.path.join(baseLogDir, vulClass)
            mkdir(logsDir)
            for test in tests:
                executeTest(target, vulClass, test, logsDir)
                if (supportsMultitasking(vulClass)):
                    multitaskingTest = cweTests[vulClass](target).testToMultitaskingObj(test)
                    if multitaskingTest:
                        multitaskingTests.append(multitaskingTest)
            _, table = scoreTests(vulClass, logsDir, prettyVulClass(vulClass), doPrint=False)
            sequentialTables[vulClass] = table

        if multitaskingTests:
            setSetting("runningMultitaskingTests", True)
            logsDir = os.path.join(baseLogDir, "multitasking")
            mkdir(logsDir)
            multitaskingRunner(target).runMultitaskingTests(multitaskingTests, logsDir)

            table = [("Vul. Class", "TEST", "Instance", "Seq. Score", "Multi. Score", "Result")]
            numMultitaskingScores = 0
            multitaskingPasses = {}
            for vulClass in getSetting("enabledCwesEvaluations").keys():
                if supportsMultitasking(vulClass):
                    for instance in range(1, getSetting('instancesPerTestPart')+1):
                        multitaskingScores, _ = scoreTests(
                                vulClass,
                                os.path.join(logsDir,
                                             vulClass,
                                             f"instance-{instance}"),
                                f'{prettyVulClass(vulClass)} multitasking '
                                f'instance {instance}',
                                doPrint=False,
                                reportFileName="multitaskingScoreReport.log")
                        table += checkMultitaskingScores(vulClass,
                                                         multitaskingScores,
                                                         instance,
                                                         multitaskingPasses)
                        numMultitaskingScores += len(multitaskingScores)
            logMultitaskingTable(table)

            for vulClass, table in sequentialTables.items():
                appendMultitaskingColumn(vulClass, table, multitaskingPasses)
                printTable(vulClass, table)

            numPassed = sum(multitaskingPasses.values())
            percentPassed = (numPassed / numMultitaskingScores) * 100
            printAndLog(f"{numPassed}/{numMultitaskingScores} multitasking "
                        f"tests scored as expected ({percentPassed:.1f}%).")
            setSetting("runningMultitaskingTests", False)
        else:
            for vulClass, table in sequentialTables.items():
                printTable(vulClass, table)

    else:
        target.terminateAndExit(f"<runTests> not implemented for <{getSetting('osImage')}>",
                   exitCode=EXIT.Implementation)

@decorate.debugWrap
def isTestEnabled(vulClass, testName):
    """
    Return whether or not a test is enabled.

    ARGUMENTS:
    ----------
        vulClass : String
            Vulnerability class the test belongs to.

        testName : String
            Name of the test.

    RETURNS:
    --------
        A boolean representing whether <testName> from <vulClass> is enabled.
    """
    if (getSettingDict(vulClass,'runAllTests')):
        return True
    else:
        return getSettingDict(vulClass,['enabledTests',testName])

