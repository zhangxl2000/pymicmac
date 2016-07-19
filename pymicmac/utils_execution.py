 #!/usr/bin/python
import os,time,stat,subprocess,shutil,glob
from pymicmac.monitor import monitor_cpu_mem_disk
from lxml import etree

def readGCPXMLFile(xmlFile):
    gcpsXYZ = {}
    cpsXYZ = {}

    if not os.path.isfile(xmlFile):
        raise Exception('ERROR: ' + xmlFile + ' not found')

    e = etree.parse(xmlFile).getroot()
    for p in e.getchildren():
        gcp = p.find('NamePt').text
        fields = p.find('Pt').text.split()
        incertitude = p.find('Incertitude').text

        x = float(fields[0])
        y = float(fields[1])
        z = float(fields[2])
        if incertitude.count('-1'):
            cpsXYZ[gcp] = (x, y, z)
        else:
            gcpsXYZ[gcp] = (x, y, z)
    return (gcpsXYZ, cpsXYZ)

def executeCommandMonitor(commandId, command, diskPath, onlyPrint=False):
    if onlyPrint:
        print(command)
        return

    # Define the names of the script that executes the command, the log file and the monitor file
    # eFileName = commandId.replace(' ', '_') + '.sh'
    logFileName = commandId.replace(' ', '_') + '.log'
    monitorLogFileName = commandId.replace(' ', '_') + '.mon'

    #Remove log file if already exists
    if os.path.isfile(logFileName):
        os.system('rm ' + logFileName)

    # Create script for command execution
    # eFile = open(eFileName, 'w')
    # eFile.write('#!/bin/bash\n')
    # eFile.write(command)
    # eFile.close()

    #Give execution rights
    # os.chmod(eFileName, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    # Run the tool that executes the command with the monitoring of CPU and MEM
    # monitor_cpu_mem_disk.run('./' + eFileName, logFileName, monitorLogFileName, diskPath)
    monitor_cpu_mem_disk.run(command, logFileName, monitorLogFileName, diskPath)
    # TODO: if execution folder is in different file system that source data, right now we only monitor raw data usage

def getSize(absPath):
    (out,err) = subprocess.Popen('du -sb ' + absPath, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    try:
        return int(out.split()[0])
    except:
        return -1

def initExecutionFolder(imagesAbsPaths, executionFolder, mmComponents):
    cwd = os.getcwd()
    # Create directory for this execution
    executionFolderAbsPath = os.path.abspath(executionFolder)
    if os.path.exists(executionFolderAbsPath):
        raise Exception(executionFolder + ' already exists!')
    os.makedirs(executionFolderAbsPath)

    # Create links for the images (existance of images has already being checked)
    for imageAbsPath in imagesAbsPaths:
        os.symlink(imageAbsPath, os.path.join(executionFolderAbsPath, os.path.basename(imageAbsPath)))

    # Create links for the rest of files/folder specifed in mmComponents/required XML
    for mmComponent in mmComponents:
        typeToLinkComponent = mmComponent.find("require")
        if typeToLinkComponent != None:
            elements = typeToLinkComponent.text.strip().split()
            for element in elements:
                if element.endswith('/'):
                    element = element[:-1]
                if element.startswith('/'):
                    elementAbsPath = element
                else:
                    elementAbsPath = cwd + '/' + element
                if os.path.isfile(elementAbsPath) or os.path.isdir(elementAbsPath):
                    os.symlink(elementAbsPath , os.path.join(executionFolderAbsPath, os.path.basename(elementAbsPath)))
                else:
                    raise Exception(element + ' does not exist!')

def getImages(imagesListFile):
    cwd = os.getcwd()
    images = []
    if not os.path.isfile(imagesListFile):
        raise Exception(imagesListFile + ' does not exist!')
    for line in open(imagesListFile, 'r').read().split('\n'):
        if line != '':
            if line.startswith('/'):
                imageAbsPath = line
            else:
                imageAbsPath = cwd + '/' + line
            if not os.path.isfile(imageAbsPath):
                raise Exception(imageAbsPath + ' does not exist!')
            images.append(imageAbsPath)
    return images

def apply_argument_parser(argumentsParser, options=None):
    """ Apply the argument parser. """
    if options is not None:
        args = argumentsParser.parse_args(options)
    else:
        args = argumentsParser.parse_args()
    return args
