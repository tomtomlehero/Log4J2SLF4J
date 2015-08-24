from os import walk
from os.path import join, isdir
import re

__author__ = 'mathieu'

projectPath = "/Users/mathieu/Dvpt/workspace/voltage"
# projectPath = "/Users/mathieu/Dvpt/workspace/voltage/voltage-core/voltage-core-business"

singleTestJavaFile =  "/Users/mathieu/Dvpt/workspace/voltage/voltage-commons/voltage-commons-utils/src/main/java/com/francetelecom/voltage/technicalservice/util/XMLUtils.java"

importStatementPattern = re.compile(r'\s*import\s*org\.apache\.log4j\.Logger\s*;\s*')

declareStatementPattern = re.compile(
    r'(?P<indent>\s*)'
    r'(?P<modifiers>((private|protected|public|static|final)\s+)*)'
    r'(Logger)\s*'
    r'(?P<logVariableName>\w+)\s*=\s*'
    r'Logger\s*\.\s*getLogger\s*\(\s*'
    r'(?P<classLogger>\w+)\s*\.\s*class\s*(\.\s*getName\s*\(\s*\)\s*)?\)\s*;\s*')


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
    for i in range(len(lines)):

        # Convert Import statement

        if importStatementPattern.match(lines[i]):
            lines[i] = "import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;\n"

        # Convert Declaration statement

        if lines[i].find("Logger") >= 0:
            declareStatementLineCount, declareStatementMatch = extractMutliLinesStatement(lines, i, declareStatementPattern, 4)

            if declareStatementMatch:
                (indent, modifiers, logVariableName, classLogger) = declareStatementMatch.group('indent', 'modifiers', 'logVariableName', 'classLogger')

                modifiers = extTrim(modifiers)

                lines[i] = "{0}{1} Logger {2} = LoggerFactory.getLogger({3}.class);\n".format(indent, modifiers, logVariableName, classLogger)

                # promote statement's former trailing lines to nothing
                for k in range(declareStatementLineCount - 1):
                    lines[i + k + 1] = ""
                # shift in the lines iteration
                i += declareStatementLineCount - 1



def writeLines(filePath, lines):
    with open(filePath, 'w') as outfile:
        for line in lines:
            outfile.write(line)

def writeLinesLn(filePath, lines):
    with open(filePath, 'w') as outfile:
        for line in lines:
            outfile.write(line + '\n')


def processFile(filePath):
    lines = getLines(filePath)
    processReplacement(lines)
    writeLines(filePath, lines)





if __name__ == '__main__':
    """
    """
    if not isdir(projectPath):
        print "Not a valid directory path {0}".format(projectPath)
        exit()


    # processFile(singleTestJavaFile)
    # exit()


    javaProjectFiles = []

    for dirPath, _, fileNames in walk(projectPath):
        javaProjectFiles.extend([ join(dirPath, fileName) for fileName in fileNames if fileName.endswith(".java") ])

    writeLinesLn("/Users/mathieu/Dvpt/workspace/Log4J2SLF4J/javaFileList.txt", javaProjectFiles)

    print "Starting convertion of {0} files from directory {1}...".format(len(javaProjectFiles), projectPath)

    for javaFile in javaProjectFiles:
        processFile(javaFile)

    pass
