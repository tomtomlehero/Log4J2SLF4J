from os import walk
from os.path import join, isdir, isfile
import re

__author__ = 'mathieu'

# Max number of lines a statement might be spread across (0 means no limit)
maxStatementLineCount = 4

projectPath = "C:\\MLA\\dvpt\\workspace_SLF4J\\voltage"
# projectPath =  "C:\\MLA\\dvpt\\workspace_SLF4J\\voltage\\voltage-gestion\\voltage-gestion-application\\src\\main\\java\\com\\francetelecom\\voltage\\gestion\\application\\impl\\ManageDemandeImpl.java"


importStatementPattern = re.compile(r'\s*import\s*org\.apache\.log4j\.Logger\s*;\s*')



declareStatementPattern = re.compile(
    r'(?P<indent>\s*)'
    r'(?P<modifiers>((private|protected|public|static|final)\s+)*)'
    r'(Logger)\s*'
    r'(?P<logVariableName>\w+)\s*=\s*'
    r'Logger\s*\.\s*getLogger\s*\(\s*'
    r'((?P<classLoggerAsClass>\w+)\s*\.\s*class\s*(\.\s*getName\s*\(\s*\))?|"(?P<classLoggerAsString>\w+)")\s*\)\s*;\s*')

# Matches log.error(e)
logErrorEPattern = re.compile(
    r'(?P<indent>\s*)'
    r'(?P<logVariableName>\w+)\s*'
    r'\.(error|warn|debug)\s*\(\s*(?P<exceptionVariableName>\w+)\s*\)\s*;\s*')



logStatementPattern = re.compile(
    r'(?P<indent>\s*)'
    r''
    r''
    r'')

testString = 'log.debug("Chargement du fichier de conf (" + System.getProperty("FichierConfigurationPeriode") + ") de l\'application");'


# log.debug("Chargement du fichier de configuration de la periode ("
#         + System.getProperty("FichierConfigurationPeriode")
#         + ") de l'application");




extendedTrimPatter = re.compile(r'\s+')

def getLines(filePath):
    lines = []
    with open(filePath) as infile:
        for line in infile:
            lines.append(line)
    return lines


def extractMutliLinesStatement(lines, start, pattern, maxLinesCount=0):
    """
    """
    oneLineStatement = ""
    statementLineCount = 0
    while (statementLineCount < maxLinesCount) or (maxLinesCount == 0):
        if len(lines) <= start + statementLineCount:
            break
        oneLineStatement += lines[start + statementLineCount]
        if oneLineStatement.endswith('\n'):
            oneLineStatement = oneLineStatement[:-1]
        statementLineCount += 1
        statementMatch = pattern.match(oneLineStatement)
        if statementMatch:
            return statementLineCount, statementMatch

    return None, None


def extTrim(s):
    """
    Remove heading and trailing spaces
    + extra useless inner blanks
    will turn "private  \t\t...  static        final  \t  "
    into a clean "private static final"
    """
    return extendedTrimPatter.sub(' ', s).strip()


def processReplacement(lines):

    modified = 0

    for i in range(len(lines)):

        # Convert Import statement
        if importStatementPattern.match(lines[i]):
            lines[i] = "import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;\n"
            modified = 1

        # Convert Declaration statement
        if lines[i].find("Logger") >= 0:
            declareStatementLineCount, declareStatementMatch = extractMutliLinesStatement(lines, i, declareStatementPattern, maxStatementLineCount)


            if declareStatementMatch:
                (indent, modifiers, logVariableName, classLoggerAsClass, classLoggerAsString) = declareStatementMatch.group('indent', 'modifiers', 'logVariableName', 'classLoggerAsClass', 'classLoggerAsString')

                modifiers = extTrim(modifiers)

                classLogger = classLoggerAsClass if classLoggerAsClass else classLoggerAsString

                lines[i] = "{0}{1} Logger {2} = LoggerFactory.getLogger({3}.class);\n".format(indent, modifiers, logVariableName, classLogger)

                # promote former statement trailing lines to nothing
                for k in range(declareStatementLineCount - 1):
                    lines[i + k + 1] = ""
                # shift in the lines iteration
                i += declareStatementLineCount - 1

                modified = 1


        # Convert log.error(e) to log.error("", e)
        if lines[i].find("error(") >= 0 or lines[i].find("warn(")>= 0 or lines[i].find("debug(")>= 0:
            logErrorEStatementLineCount, logErrorEStatementMatch = extractMutliLinesStatement(lines, i, logErrorEPattern, maxStatementLineCount)

            if logErrorEStatementMatch:
                (indent, logVariableName, exceptionVariableName) = logErrorEStatementMatch.group('indent', 'logVariableName', 'exceptionVariableName')

                lines[i] = "{0}{1}.error(\"\", {2});\n".format(indent, logVariableName, exceptionVariableName)

                # promote statement's former trailing lines to nothing
                for k in range(logErrorEStatementLineCount - 1):
                    lines[i + k + 1] = ""
                # shift in the lines iteration
                i += logErrorEStatementLineCount - 1

                modified = 1

        # Convert log.fatal(...) to log.error(...)
        if lines[i].find("log.fatal(") >= 0:
            lines[i] = lines[i].replace("log.fatal(", "log.error(")
            modified = 1



    return modified



def writeLines(filePath, lines):
    with open(filePath, 'w') as outfile:
        for line in lines:
            outfile.write(line)

def writeLinesLn(filePath, lines):
    with open(filePath, 'w') as outfile:
        for line in lines:
            outfile.write(line + '\n')






def convertFile(filePath):
    lines = getLines(filePath)
    modified = processReplacement(lines)
    if modified == 1:
        writeLines(filePath, lines)

    return modified



def convertProject(projectPath):
    javaProjectFiles = []

    for dirPath, _, fileNames in walk(projectPath):
        javaProjectFiles.extend([ join(dirPath, fileName) for fileName in fileNames if fileName.endswith(".java") ])

    print "Starting convertion of {0} files from directory {1}...".format(len(javaProjectFiles), projectPath)

    count= 0
    for javaFile in javaProjectFiles:
        count += convertFile(javaFile)

    print "Conversion done. {0} files modified".format(count)



if __name__ == '__main__':
    """
    """
    if isdir(projectPath):
        convertProject(projectPath)
        exit()
    else:
        if isfile(projectPath):
            convertFile(projectPath)
            exit()
        else:
            print "Not a valid file or directory {0}".format(projectPath)

