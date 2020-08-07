from fett.base.utils.misc import *

# TODO: Many functions are still missing here

class testgenTargetCompatabilityLayer:
    """
    This class wraps a FETT target and presents a testgen target interface
    """
    def __init__(self, target):
        self.target = target

        # TODO: What exactly is targetObj in the tests?  It seems they only
        # ever access (or in one case, set) the isSshConn field.  Dig into the
        # testgen code for targetObj
        self.targetObj = target

        # TODO: Populate dicts from config file
        self.testsPars = {"nResourceLimit" : 10}
        self.settings = {"useCustomScoring" : False}
        if doesSettingExist("PPAC"):
            self.testsPars["SPOOFING_IP"] = getSettingDict("PPAC", "spoofingIP")
            self.testsPars["nAllowedInteractions"] = getSettingDict("PPAC", "test_nAllowedInteractions")
            self.testsPars["nAllowedAuthAttempts"] = getSettingDict("PPAC", "test_nAllowedAuthAttempts")


        # TODO: Set this to match target?
        self.filename = "compatability"

        # TODO: Make this configurable?
        self.showExecutionOnScreen = False

        # TODO: Something less hacky
        self.backend = ('fpga' if isEqSetting('target', 'aws')
                               else getSetting('target'))

    @property
    def osImage(self):
        return getSetting("osImage")

    @property
    def isCurrentUserRoot(self):
        return self.target.isCurrentUserRoot

    @isCurrentUserRoot.setter
    def isCurrentUserRoot(self, value):
        self.target.isCurrentUserRoot = value

    @property
    def userName(self):
        return self.target.userName

    @userName.setter
    def userName(self, value):
        self.target.userName = value

    @property
    def userPassword(self):
        return self.target.userPassword

    @userPassword.setter
    def userPassword(self, value):
        self.target.userPassword = value

    @property
    def rootPassword(self):
        return self.target.rootPassword

    def typCommand(self, command):
        # TODO: Better endsWith (will this even work for freebsd?)
        return self.target.runCommand(command)[1]

    def runCommand(self, command, **kwargs):
        # TODO: Are these interfaces compatable enough?
        return self.target.runCommand(command, **kwargs)

    # TODO: The real reportAndExit takes a bunch of optional params that we
    # should support
    def reportAndExit(self, message):
        logAndExit(message)

    def switchUser(self):
        self.target.switchUser()

