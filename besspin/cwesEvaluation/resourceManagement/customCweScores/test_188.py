from besspin.cwesEvaluation.resourceManagement.customCweScores.helpers import *

def test_188 (logLines):
    testNum = 188

    osImage = getOsImage(logLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 6
        partsLines = regPartitionTest (logLines,nParts,testNum=testNum)
        partsScores = {}

        specialKeywords = { 1: '<PROTOCOL_ONE_BYTE_IN_FRONT>', 2: '<PROTOCOL_ONE_BYTE_PAST>',
                            3: '<PROTOCOL_THREE_BYTES_IN_FRONT>', 4: '<PROTOCOL_THREE_BYTE_PAST>',
                            5:'<EXPECTED_INPUT_PAST>', 6: '<EXPECTED_INPUT_PAST>' }

        for iPart in range(1,nParts+1):
            if (doesKeywordExist(partsLines[iPart],"<INVALID>")):
                partsScores[iPart] = SCORES.CALL_ERR
            elif (doesKeywordExist(partsLines[iPart],"<WRONG_PROTOCOL>")):
                partsScores[iPart] = SCORES.HIGH
            elif (doesKeywordExist(partsLines[iPart],specialKeywords[iPart])):
                partsScores[iPart] = SCORES.NONE
            else:
                partsScores[iPart] = SCORES.FAIL
        
    elif (osImage == 'FreeRTOS'):
        nParts = 4
        partsLines = regPartitionTestFreeRTOS(logLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<PROTOCOL_ONE_BYTE_IN_FRONT>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.HIGH
        if (doesKeywordExist(partsLines[2],"<PROTOCOL_ONE_BYTE_PAST>")):
            partsScores[2] = SCORES.NONE
        else:
            partsScores[2] = SCORES.HIGH

        if (doesKeywordExist(partsLines[3],"<EXPECTED_INPUT_PAST>")):
                partsScores[3] = SCORES.NONE
        else:
            partsScores[3] = SCORES.HIGH

        if (doesKeywordExist(partsLines[4],"<EXPECTED_INPUT_PAST>")):
            partsScores[4] = SCORES.NONE
        else:
            partsScores[4] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)