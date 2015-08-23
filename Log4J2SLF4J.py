import re

__author__ = 'mathieu'

fileToProcess = "/Users/mathieu/Dvpt/workspace/voltage/voltage-commons/voltage-commons-utils/src/main/java/com/francetelecom/voltage/technicalservice/util/PieceJointe.java"
#fileToProcess = "/Users/mathieu/Dvpt/workspace/voltage/voltage-core/voltage-core-business/src/main/java/com/francetelecom/voltage/business/demande/requisition/impl/ManageDemandeBusinessImpl.java"


importStatementPattern = re.compile(r'\s*import\s*org\.apache\.log4j\.Logger\s*;\s*')

declareStatementPattern = re.compile(
    r'(?P<indent>\s*)'
    r'(?P<modifiers>((private|protected|public|static|final)\s+)*)'
    r'(Logger)\s*'
    r'(?P<logVariableName>\w+)\s*=\s*'
    r'Logger\s*\.\s*getLogger\s*\(\s*'
    r'(?P<classLogger>\w+)\s*\.\s*class\s*\)\s*;\s*')



def getLines(filePath):
    lines = []
    with open(filePath) as infile:
        for line in infile:
            lines.append(line)
    return lines


def processReplacement(lines):
    for i in range(len(lines)):

        # Import statement

        if importStatementPattern.match(lines[i]):
            lines[i] = "import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;\n"

        # Declaration statement
        declareStatementMatch = declareStatementPattern.match(lines[i])
        if declareStatementMatch:
            (indent, modifiers, logVariableName, classLogger) = declareStatementMatch.group('indent', 'modifiers', 'logVariableName', 'classLogger')
            modifiers = modifiers.strip()
            lines[i] = "{0} {1} Logger {2} = LoggerFactory.getLogger({3}.class);\n".format(indent, modifiers, logVariableName, classLogger)


def writeLines(filePath, lines):
    with open(filePath, 'w') as outfile:
        for line in lines:
            outfile.write(line)


def processFile(filePath):
    lines = getLines(filePath)
    processReplacement(lines)
    writeLines(filePath, lines)





if __name__ == '__main__':
    """
    """
    processFile(fileToProcess)

    pass
