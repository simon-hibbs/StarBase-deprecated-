# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

import sys, os, shutil, imp
from PySide.QtCore import *
from PySide.QtGui import *
from log import *
#import qrc_resources
from ConfigParser import SafeConfigParser
from model import Models
from model import Foundation
from NewProject import NewProjectDialog, ProjectInfo, RulesInfo

# Plan:
# Single 'Projects' directory. All projects in here are listed.
# Buttons: 'Open', 'New', 'Archive', 'Import', 'Delete', 'Make Default', 'Close'
# All directories containing a starbase.ini file listed as projects


class ProjectManager(QDialog):
    
    def __init__(self, model, parent=None):
        super(ProjectManager, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle("StarBase Project Manager")
        info_log("Initialising Project Manager")
        self.model = model

        self.projects = []
        self.rulesList = []
        self.projectsDir = os.getcwd()
        self.defaultProjectIndex = 0
        self.config = SafeConfigParser()

        dialogLayout = QGridLayout()

        projectListlabel = QLabel('Project List')
        self.projectListWidget = QListWidget()
        self.pathTextLine = QLineEdit()
        
        dialogLayout.addWidget(projectListlabel,0,0)
        dialogLayout.addWidget(self.projectListWidget,1,0,8,1)
        dialogLayout.addWidget(self.pathTextLine,9,0)

        self.openProjectButton = QPushButton('Open Project')
        self.newProjectButton = QPushButton('New Project')
        self.setDefaultButton = QPushButton('Make Default')
        #self.removeProjectButton = QPushButton('Remove Project')
        self.closeButton = QPushButton('Close')
        self.pathButton = QPushButton('Change Project Directory')

##        self.connect(openProjectButton, SIGNAL("clicked()"), self.openProject)
##        self.connect(newProjectButton, SIGNAL("clicked()"), self.newProject)
##        #newProjectButton.setDisabled(True)
##        self.connect(makeDefaultButton, SIGNAL("clicked()"), self.setDefaultProject)
##        self.connect(removeProjectButton, SIGNAL("clicked()"), self.removeProject)
##        self.connect(closeButton, SIGNAL("clicked()"), self.close)
##        self.projectListWidget.currentRowChanged[int].connect(self.projectSelected)
##        self.connect(self.pathButton, SIGNAL("clicked()"), self.changePath)

        self.openProjectButton.clicked.connect(self.openProject)
        self.newProjectButton.clicked.connect(self.newProject)
        self.setDefaultButton.clicked.connect(self.setDefaultProject)
        #self.removeProjectButton.clicked.connect(self.removeProject)
        self.closeButton.clicked.connect(self.close)
        self.pathButton.clicked.connect(self.changePath)
        self.projectListWidget.currentRowChanged[int].connect(self.projectSelected)

        dialogLayout.addWidget(self.openProjectButton,1,1)
        dialogLayout.addWidget(self.newProjectButton,2,1)
        dialogLayout.addWidget(self.setDefaultButton,3,1)
        #dialogLayout.addWidget(self.removeProjectButton,4,1)
        dialogLayout.addWidget(self.closeButton,8,1)
        dialogLayout.addWidget(self.pathButton,9,1)

        self.setLayout(dialogLayout)
        self.setMinimumWidth(500)

        self.default_project = 0
        self.readProjectsFile()
        self.projectListWidget.setCurrentRow(self.default_project)



    def openProject(self):
        # Tells the model to load the project data
        try:
            project_path = os.path.join(self.projectsDir,
                                        self.projects[self.projectListWidget.currentRow()].name)
            self.model.loadProjectData(project_path)
            QDialog.done(self, 1)
        except Exception, e:
            debug_log(str(e))
            debug_log('Current Row: ' + str(self.projects[self.projectListWidget.currentRow()].name))
            debug_log('Projects list ' + str(self.projectsDir))


    def newProject(self):
        new_project_dialog = NewProjectDialog(self.model, self.rulesList)
        if new_project_dialog.exec_() == QDialog.Accepted:
            info_log('Executing new project dialog.')
            project_info = new_project_dialog.getProjectInfo()
            info_log('New project info object retrieved. Project name:' + project_info.name)
            #new_project_dialog.deleteLater()

            if project_info is not None:
                info_log('Project manager is creating the project directory.')
                project_path = os.path.join(self.projectsDir, project_info.name)

                if os.path.exists(project_path):
                    info_log('Project directory already exists:' + project_path)
                    if not os.path.isdir(project_path):
                        info_log('WARNING! target is not a directory!')
                        return False
                else:
                    os.mkdir(project_path)

                info_log('Project manager is creating the rules directory.')
                rules_template = project_info.rules_info.rules_template
                project_rules_directory = os.path.join(project_path, 'Rules')
                shutil.copytree(rules_template, project_rules_directory)
                
                debug_log('Initialising new project in directory ' + project_path)
                project_name = self.model.createNewProject(project_info.width,
                                                           project_info.height,
                                                           project_path)

                self.addProject(project_info)
        

    def setDefaultProject(self):
        #config = SafeConfigParser()
        #config.read('projects.ini')
        self.defaultProjectIndex = self.projectListWidget.currentRow()
        self.config.set('Projects', 'default_project',
                   str(self.defaultProjectIndex))
        with open('projects.ini', 'wb') as projects_file:
            self.config.write(projects_file)

    def addProject(self, project_info):
        self.projects.append(project_info)
        self.projectListWidget.addItem(project_info.name)

# deprecated as the project manager should never delete projects
##    def removeProject(self):
##        rownum = self.projectListWidget.currentRow()
##        item = self.projectListWidget.takeItem(rownum)
##        del item
##        self.projects = self.projects[0:rownum] + self.projects[(rownum + 1):]
##        if self.defaultProjectIndex > len(self.projects):
##            self.defaultProjectIndex = 0
##        self.writeProjectsFile()


    def close(self, result=0):
        #self.model.loadProjectData("starbase.ini")
        QDialog.done(self, result)

    # Checks the Rules directory for saubdirectories containing a Rules.py file
    # and put into about them into self.rulesList
    def loadRulesList(self, rules_template):
        if not os.path.isdir(rules_template):
            info_log('ProjectManager: Error accessing the Rules directory: ' + rules_template)
            sys.exit(0)
        else:
            self.rulesDir = rules_template
            dir_list = os.listdir(self.rulesDir)

            for entry in dir_list:
                check_path = os.path.join(self.rulesDir, entry)
                if os.path.isdir(check_path):
                    info_log('Found directory: ' + entry)
                    rules_file = os.path.join(check_path, 'Rules.py')
                    if os.path.exists(rules_file):
                        info_log("Directory " + entry + " contains a rules file")

                        description_file = os.path.join(check_path, 'RulesInfo.txt')
                        if os.path.exists(description_file):
                            with open(description_file, 'r') as f:
                                description = f.read()
                        else:
                            info_log(description_file + "Does not exist, rules description will be blank.")
                            description = ""
                        
                        rules_info = RulesInfo()
                        rules_info.name = entry
                        rules_info.description = description
                        rules_info.rules_template = check_path
                        self.rulesList.append(rules_info)

                    else:
                        info_log("Directory " + entry + " does NOT contain a rules file")


    # Checks the directory for subdirectories containing a starbase.ini file
    def setProjectsDirectory(self, new_path):
        if not os.path.isdir(new_path):
            info_log('ProjectManager: Error accessing the project directory: ' + new_path)
            info_log('setting to default path: ' + os.getcwd())
            new_path = os.getcwd()
        else:
            self.projectsDir = new_path
            self.pathTextLine.setText(self.projectsDir)
            dir_list = os.listdir(self.projectsDir)

            self.projects = []
            self.projectListWidget.clear()
            
            for entry in dir_list:
                check_path = os.path.join(self.projectsDir, entry)
                if os.path.isdir(check_path):
                    info_log('Found directory: ' + entry)
                    project_info = ProjectInfo()
                    project_info.name = entry
                    
                    check_ini = os.path.join(check_path, 'starbase.ini')
                    if os.path.exists(check_ini):
                        info_log("Directory " + entry + " contains a project")
                        project_info.has_ini = True
                        self.addProject(project_info)
                        
                    else:
                        info_log("Directory " + entry + " does NOT contain a project")


    def changePath(self):
        dir_name = QFileDialog.getExistingDirectory(self,
                                                    'Select Project Directory',
                                                    self.projectsDir,
                                                    QFileDialog.ShowDirsOnly)
        if dir_name == '':
            info_log('No project directory specified.')
            
        elif dir_name == self.projectsDir:
            info_log('Project directory not changed.')

        self.setProjectsDirectory(dir_name)
        self.writeProjectsFile()
        

    def projectSelected(self, row):
        self.default_project = row


    def readProjectsFile(self):
        self.config.read('projects.ini')

        #number_of_projects = self.config.getint('Projects', 'number_of_projects')
        project_directory_path = self.config.get('Projects', 'project_directory_path')
        self.default_project = int(self.config.get('Projects', 'default_project'))
        #default_project_name = self.config.get('Projects', 'default_project_name')
        #info_log('Number of projects: ' + str(number_of_projects))
        info_log('Project directory: ' + str(project_directory_path))
        #info_log('Default project: ' + str(default_project_name))

        self.setProjectsDirectory(project_directory_path)

        self.rules_templates_path = self.config.get('Rules', 'rules_templates_path')
        if not os.path.isdir(self.rules_templates_path):
            info_log('Rules directory: ' + self.rules_templates_path + ' Does not exist. Setting to default.')
            
            self.rules_templates_path = os.path.join(os.getcwd(), 'rules_templates')
            info_log('Setting rules directory to ' + self.rules_templates_path)
            
            if not os.path.isdir(self.rules_templates_path):
                info_log('Rules directory: ' + self.rules_templates_path + ' Does not exist')
                info_log('ERROR: A rules directory could not be found. Creating a new project will fail!')
        
        info_log('Rules directory: ' + str(self.rules_templates_path))
        self.loadRulesList(self.rules_templates_path)


    def writeProjectsFile(self):
        debug_log('Updating application projects file.')
        self.config = SafeConfigParser()
        
        self.config.add_section('Projects')
        self.config.set('Projects', 'project_directory_path', self.projectsDir)
        self.config.set('Projects', 'default_project', str(self.default_project))

        self.config.add_section('Rules')
        self.config.set('Rules', 'rules_templates_path', self.rules_templates_path)

        with open('projects.ini', 'wb') as projects_file:
            self.config.write(projects_file)
        
