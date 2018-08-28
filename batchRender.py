# -*- coding: utf-8 -*-
# __author__ = 'XingHuan-PC'
# 2017/1/9


import os
import sys
from batchRender_module import *
import shutil
import subprocess
import multiprocessing
import time
import traceback
import platform



import batchRender_path as RP
import batchRender_set as RS

inNuke = inNuke
if inNuke == True:
    import batchRender_nuke as RN
testWriteNodes = [['F:/Temp/test03/temp.nk', 'Write2', 'F:/Temp/test03/test02/test_write2.%04d.jpg', '1', '100'], ['F:/Temp/test03/temp.nk', 'Write1', 'F:/Temp/test03/test02/test_write1.%04d.jpg', '1', '100']]


GLOBAL_Folder = RP.GLOBAL_Folder

GLOBAL_ICON_Path = "%s/icons" % GLOBAL_Folder
if forUser == 0:
    USER_HOME_Path = "%s/render_config" % GLOBAL_Folder
else:
    USER_HOME_Path = "%s/render_config" % RP.Users_Path
if not os.path.exists(USER_HOME_Path):
    os.makedirs(USER_HOME_Path)


video_list = ["mov", "mp4"]
max_threads_number = int(multiprocessing.cpu_count())
nuke_execute_path = "D:/Program Files/Nuke9.0v7/Nuke9.0.exe"
if inNuke == True:
    nuke_execute_path = RN.getExecutablePath()
xml_file = "%s/batch render.xml" % USER_HOME_Path



def getAllFrames(n):
	tree = RS.read_xml(xml_file)
	root = tree.getroot()
	allNodes = RS.find_nodes(root)
	currentNode = None
	for node in allNodes:
		if node.get("number") == str(n):
			currentNode = node
	if currentNode != None:
		inout = [str(i) for i in range(int(currentNode.get("frameIn")), int(currentNode.get("frameOut")) + 1, int(currentNode.get("frameInterval")))]
		#print inout
		return inout

def getFilePath(n):
    tree = RS.read_xml(xml_file)
    root = tree.getroot()
    allNodes = RS.find_nodes(root)
    currentNode = None
    for node in allNodes:
        if node.get("number") == str(n):
            currentNode = node
    if currentNode != None:
        fileName = currentNode.get("fileName")
        filePath = os.path.split(fileName)[0]
        return filePath

def getFrameList(frameIn, frameOut, interval, fileName, multiRenderNum):
    n = max_threads_number / int(multiRenderNum)
    # print n
    if max_threads_number % int(multiRenderNum) > 0:
        if (n + 1) * int(multiRenderNum) - max_threads_number <= max_threads_number / 2:
            n = n + 1
    inout = [str(i) for i in range(int(frameIn), int(frameOut) + 1, int(interval))]
    filePath = os.path.split(fileName)[0]
    if os.path.exists(filePath) == False:
        os.makedirs(filePath)
    if fileName.split(".")[-1] in video_list:
		n = 1
    print inout
    print "frames: %s" % len(inout)
    framesEach = len(inout) / n
    if len(inout) % n > 0:
        framesEach = framesEach + 1
    print "renders: %s" % n
    print "framesEach: %s" % framesEach

    frameList = [[] for i in range(n + 1)]
    for i in range(1, n):
        frameList[i] = inout[((i - 1) * framesEach):(i * framesEach)]
    frameList[n] = inout[((n - 1) * framesEach):]
    frameStr = ["" for i in range(n + 1)]
    for i in range(1, n + 1):
        tempList = []
        if frameList[i] != []:
            tempList.append(frameList[i][0])
            tempList.append(frameList[i][-1])
            frameStr[i] = ",".join(tempList)
    return frameStr

def createCMDList(nukeExecutePath, renderThreads, nodeName, nkPath, frameIn, frameOut, interval, fileName, multiRenderNum):
    frameList = getFrameList(frameIn, frameOut, interval, fileName, multiRenderNum)
    cmdList = []
    for frames in frameList:
        if frames != "":
            if nukeExecutePath.find("/") != -1:
                cmd = '"%s" -x -m %s -X %s -F %s,%s "%s"' % (nukeExecutePath, renderThreads, nodeName, frames, interval, nkPath)
            else:
                cmd = '%s -x -m %s -X %s -F %s,%s "%s"' % (nukeExecutePath, renderThreads, nodeName, frames, interval, nkPath)
            # print cmd
            cmdList.append(cmd)
    print cmdList
    return cmdList

def createCMDFromXml(n):
    tree = RS.read_xml(xml_file)
    root = tree.getroot()
    allNodes = RS.find_nodes(root)
    setting = RS.find_setting(root)
    currentNode = None
    for node in allNodes:
        if node.get("number") == str(n):
            currentNode = node
    if currentNode != None:
        cmdList = createCMDList(setting.get("executePath"), setting.get("threads"), currentNode.get("name"),currentNode.get("nkPath"), currentNode.get("frameIn"), currentNode.get("frameOut"),currentNode.get("frameInterval"), currentNode.get("fileName"), setting.get("multiRenderNum"))
        return cmdList




class BatchRenderWindow(QWidget):
    def __init__(self):
        super(BatchRenderWindow, self).__init__()
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.createFolder()
        self.resize(750, 550)

        self.renderThreads = "8"
        self.executePath = " "
        self.multiRenderNum = "2"
        self.status = "render"    # "render" / "not render"
        self.newList = []
        self.waitingList = []
        self.renderingList = []
        self.killedList = []
        self.finishList = []


        # render tab
        self.renderBox = QGroupBox("render")

        self.renderButtonsLayout = QHBoxLayout()
        self.addNodeButton = QLabelButton("add")
        self.removeNodeButton = QLabelButton("remove")
        self.clearNodeButton = QLabelButton("clear")
        self.renderAllButton = QLabelButton("render all")
        self.killAllButton = QLabelButton("kill all")
        # self.connect(self.addNodeButton, SIGNAL('buttonClicked()'), self.addNodes)
        # self.connect(self.removeNodeButton, SIGNAL('buttonClicked()'), self.removeNode)
        # self.connect(self.clearNodeButton, SIGNAL('buttonClicked()'), self.clearAllNodes)
        # self.connect(self.renderAllButton, SIGNAL('buttonClicked()'), self.renderAllNodes)
        # self.connect(self.killAllButton, SIGNAL('buttonClicked()'), self.killAllNodes)
        self.addNodeButton.buttonClicked.connect(self.addNodes)
        self.removeNodeButton.buttonClicked.connect(self.removeNode)
        self.clearNodeButton.buttonClicked.connect(self.clearAllNodes)
        self.renderAllButton.buttonClicked.connect(self.renderAllNodes)
        self.killAllButton.buttonClicked.connect(self.killAllNodes)
        self.renderButtonsLayout.addWidget(self.addNodeButton)
        self.renderButtonsLayout.addWidget(self.removeNodeButton)
        self.renderButtonsLayout.addWidget(self.clearNodeButton)
        self.renderButtonsLayout.addWidget(self.renderAllButton)
        self.renderButtonsLayout.addWidget(self.killAllButton)
        self.renderButtonsLayout.addStretch()

        self.renderTable = QTableWidget()
        self.renderTable.setMinimumHeight(120)
        self.renderTable.setColumnCount(5)
        self.renderTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.renderTable.horizontalHeader().setStretchLastSection(True)
        self.renderTable.setColumnWidth(3, 70)
        self.renderTable.setColumnWidth(4, 305)
        #self.loadNodesFromXml()
        #self.loadNodesToTable()

        self.renderInfoLayout = QVBoxLayout()
        self.renderInfoLabel = QLabel("Render Info: ")

        self.newListLayout = QHBoxLayout()
        self.newListLabel = QLabel("    new: ")
        self.newListInfo = QLabel(" ".join(self.newList))
        self.newListLayout.addWidget(self.newListLabel)
        self.newListLayout.addSpacing(10)
        self.newListLayout.addWidget(self.newListInfo)
        self.newListLayout.addStretch()

        self.waitingListLayout = QHBoxLayout()
        self.waitingListLabel = QLabel("    waiting: ")
        self.waitingListInfo = QLabel(" ".join(self.waitingList))
        self.waitingListLayout.addWidget(self.waitingListLabel)
        self.waitingListLayout.addSpacing(10)
        self.waitingListLayout.addWidget(self.waitingListInfo)
        self.waitingListLayout.addStretch()

        self.renderingListLayout = QHBoxLayout()
        self.renderingListLabel = QLabel("    rendering: ")
        self.renderingListInfo = QLabel(" ".join(self.renderingList))
        self.renderingListLayout.addWidget(self.renderingListLabel)
        self.renderingListLayout.addSpacing(10)
        self.renderingListLayout.addWidget(self.renderingListInfo)
        self.renderingListLayout.addStretch()

        self.killedListLayout = QHBoxLayout()
        self.killedListLabel = QLabel("    killed: ")
        self.killedListInfo = QLabel(" ".join(self.killedList))
        self.killedListLayout.addWidget(self.killedListLabel)
        self.killedListLayout.addSpacing(10)
        self.killedListLayout.addWidget(self.killedListInfo)
        self.killedListLayout.addStretch()

        self.finishListLayout = QHBoxLayout()
        self.finishListLabel = QLabel("    finish: ")
        self.finishListInfo = QLabel(" ".join(self.finishList))
        self.finishListLayout.addWidget(self.finishListLabel)
        self.finishListLayout.addSpacing(10)
        self.finishListLayout.addWidget(self.finishListInfo)
        self.finishListLayout.addStretch()

        self.renderInfoLayout.addWidget(self.renderInfoLabel)
        self.renderInfoLayout.addLayout(self.newListLayout)
        self.renderInfoLayout.addLayout(self.waitingListLayout)
        self.renderInfoLayout.addLayout(self.renderingListLayout)
        self.renderInfoLayout.addLayout(self.killedListLayout)
        self.renderInfoLayout.addLayout(self.finishListLayout)

        self.renderMasterLayout = QVBoxLayout()
        self.renderMasterLayout.addLayout(self.renderButtonsLayout)
        self.renderMasterLayout.addWidget(self.renderTable)
        #self.renderMasterLayout.addStretch()
        self.renderMasterLayout.addLayout(self.renderInfoLayout)
        #self.renderMasterLayout.addStretch()
        self.renderBox.setLayout(self.renderMasterLayout)


        # setting tab
        self.settingBox = QGroupBox("setting")

        self.renderThreadsLayout = QVBoxLayout()
        self.renderThreadsLabel = QLabel("Threads:")
        self.renderThreadsSliderLayout = QHBoxLayout()
        self.renderThreadsSlider = QSlider(Qt.Horizontal)
        self.renderThreadsSlider.setMaximumWidth(200)
        self.renderThreadsSlider.setMinimum(1)
        self.renderThreadsSlider.setMaximum(max_threads_number)
        self.renderThreadsNumberLabel = QLabel()
        self.renderThreadsSlider.valueChanged.connect(self.changeRenderThreads)
        self.renderThreadsSliderLayout.addWidget(self.renderThreadsSlider)
        self.renderThreadsSliderLayout.addSpacing(20)
        self.renderThreadsSliderLayout.addWidget(self.renderThreadsNumberLabel)
        self.renderThreadsSliderLayout.addStretch()
        self.renderThreadsLayout.addWidget(self.renderThreadsLabel)
        self.renderThreadsLayout.addSpacing(10)
        self.renderThreadsLayout.addLayout(self.renderThreadsSliderLayout)

        self.nukeExecutePathLayout = QVBoxLayout()
        self.nukeExecutePathLabel = QLabel("Nuke Execute Path:")
        self.nukeExecutePathTextLayout = QHBoxLayout()
        self.nukeExecutePathLineEdit = QLineEdit("%s" % self.executePath)
        self.nukeExecutePathLineEdit.textChanged.connect(self.customNukePathEdit)
        self.nukeExecutePathLineEdit.setMinimumWidth(350)
        self.nukeExecutePathLineEdit.setEnabled(False)
        self.nukeExecutePathCustomCheckbox = QCheckBox("Custom")
        self.nukeExecutePathCustomCheckbox.clicked.connect(self.customNukePath)
        self.nukeExecutePathTextLayout.addWidget(self.nukeExecutePathLineEdit)
        self.nukeExecutePathTextLayout.addSpacing(20)
        self.nukeExecutePathTextLayout.addWidget(self.nukeExecutePathCustomCheckbox)
        self.nukeExecutePathTextLayout.addStretch()
        self.nukeExecutePathLayout.addWidget(self.nukeExecutePathLabel)
        self.nukeExecutePathLayout.addSpacing(10)
        self.nukeExecutePathLayout.addLayout(self.nukeExecutePathTextLayout)

        self.multiRenderLayout = QVBoxLayout()
        self.multiRenderLabel = QLabel("Number of MultiRender:")
        self.multiRenderSliderLayout = QHBoxLayout()
        self.multiRenderSlider = QSlider(Qt.Horizontal)
        self.multiRenderSlider.setMaximumWidth(200)
        self.multiRenderSlider.setMinimum(1)
        self.multiRenderSlider.setMaximum(max_threads_number)
        self.multiRenderNumberLabel = QLabel()
        self.multiRenderSlider.valueChanged.connect(self.changeMultiRenderNumbers)
        self.multiRenderSliderLayout.addWidget(self.multiRenderSlider)
        self.multiRenderSliderLayout.addSpacing(20)
        self.multiRenderSliderLayout.addWidget(self.multiRenderNumberLabel)
        self.multiRenderSliderLayout.addStretch()
        self.multiRenderLayout.addWidget(self.multiRenderLabel)
        self.multiRenderLayout.addSpacing(10)
        self.multiRenderLayout.addLayout(self.multiRenderSliderLayout)

        self.settingButtonLayout = QHBoxLayout()
        self.settingButtonLayout.setAlignment(Qt.AlignRight)
        self.applyButton = QPushButton("apply")
        self.applyButton.setEnabled(False)
        self.applyButton.clicked.connect(self.apply_setting_change)
        self.settingButtonLayout.addWidget(self.applyButton)

        self.settingMasterLayout = QVBoxLayout()
        self.settingMasterLayout.addLayout(self.renderThreadsLayout)
        self.settingMasterLayout.addSpacing(25)
        self.settingMasterLayout.addLayout(self.nukeExecutePathLayout)
        self.settingMasterLayout.addSpacing(25)
        self.settingMasterLayout.addLayout(self.multiRenderLayout)
        self.settingMasterLayout.addSpacing(25)
        self.settingMasterLayout.addLayout(self.settingButtonLayout)
        self.settingMasterLayout.addStretch()
        self.settingBox.setLayout(self.settingMasterLayout)

        # self.settingBox.hide()
        self.showHideLayout = QHBoxLayout()
        self.showHideLayout.setAlignment(Qt.AlignLeft)
        self.showHideButton = ShowHideButton()
        # self.connect(self.showHideButton, SIGNAL("buttonClicked()"), self.set_setting_show)
        self.showHideButton.buttonClicked.connect(self.set_setting_show)
        self.showHideLabel = QLabel("setting")
        self.showHideLayout.addWidget(self.showHideButton)
        self.showHideLayout.addWidget(self.showHideLabel)

        # master
        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(self.renderBox)
        self.masterLayout.addLayout(self.showHideLayout)
        self.masterLayout.addWidget(self.settingBox)
        self.setLayout(self.masterLayout)

        self.updateSetting()
        self.reset()
        self.loadNodesFromXml()
        self.loadNodesToTable()

    def set_setting_show(self):
        if self.showHideButton.show:
            self.settingBox.show()
        else:
            self.settingBox.hide()


    def createFolder(self):
        if not os.path.exists(USER_HOME_Path):
            os.makedirs(USER_HOME_Path)
            os.chmod(USER_HOME_Path, 0777)
        if not os.path.exists(xml_file):
            default_xml_tree = RS.read_xml("%s/default.xml" % GLOBAL_Folder)
            #RS.write_xml(default_xml_tree, xml_file)
            #tree = RS.read_xml(xml_file)
            tree = default_xml_tree
            root = tree.getroot()
            setting = RS.find_setting(root)
            RS.change_setting(setting, {"threads":"%s" % (max_threads_number/2), "executePath":"%s" % nuke_execute_path})
            RS.write_xml(tree, xml_file)

    def updateSetting(self):
        tree = RS.read_xml(xml_file)
        root = tree.getroot()
        setting = RS.find_setting(root)
        renderThreads = setting.get("threads")
        self.renderThreadsSlider.setValue(int(renderThreads))
        self.renderThreadsNumberLabel.setText(str(self.renderThreadsSlider.value()))
        if setting.get("customPath") == "1":
            self.nukeExecutePathCustomCheckbox.setChecked(True)
            self.nukeExecutePathLineEdit.setEnabled(True)
            executePath = setting.get("executePath")
            self.nukeExecutePathLineEdit.setText(executePath)
        else:
            self.nukeExecutePathCustomCheckbox.setChecked(False)
            self.nukeExecutePathLineEdit.setEnabled(False)
            executePath = nuke_execute_path
            self.nukeExecutePathLineEdit.setText(executePath)
        multiRenderNum = setting.get("multiRenderNum")
        self.multiRenderSlider.setValue(int(multiRenderNum))
        self.multiRenderNumberLabel.setText(multiRenderNum)
        self.multiRenderNum = str(self.multiRenderSlider.value())

    # --------
    # change setting
    # --------
    def changeRenderThreads(self):
        self.renderThreadsNumberLabel.setText(str(self.renderThreadsSlider.value()))
        self.applyButton.setEnabled(True)

    def customNukePath(self):
        #print "custom Nuke Path"
        self.applyButton.setEnabled(True)
        if self.nukeExecutePathCustomCheckbox.isChecked():
            self.nukeExecutePathLineEdit.setEnabled(True)
        else:
            self.nukeExecutePathLineEdit.setEnabled(False)
            self.nukeExecutePathLineEdit.setText(nuke_execute_path)

    def customNukePathEdit(self):
        self.applyButton.setEnabled(True)


    def changeMultiRenderNumbers(self):
        self.multiRenderNumberLabel.setText(str(self.multiRenderSlider.value()))
        self.multiRenderNum = str(self.multiRenderSlider.value())
        self.applyButton.setEnabled(True)

    def apply_setting_change(self):
        tree = RS.read_xml(xml_file)
        root = tree.getroot()
        setting = RS.find_setting(root)
        RS.change_setting(setting, {"threads": "%s" % str(self.renderThreadsSlider.value())})
        if self.nukeExecutePathCustomCheckbox.isChecked():
            RS.change_setting(setting, {"customPath": "1"})
        else:
            RS.change_setting(setting, {"customPath":"0", "executePath":"%s" % nuke_execute_path})
        RS.change_setting(setting, {"executePath": "%s" % self.nukeExecutePathLineEdit.text()})
        RS.change_setting(setting, {"multiRenderNum": "%s" % str(self.multiRenderSlider.value())})
        RS.write_xml(tree, xml_file)
        self.applyButton.setEnabled(False)




    def reset(self):
        self.nodeList = []
        self.waitingList = []
        self.renderingList = []
        self.killedList = []
        self.finishList = []
        self.newList = []
        self.updateRenderInfo()

    def loadNodesFromXml(self):
        tree = RS.read_xml(xml_file)
        root = tree.getroot()
        allNodes = RS.find_nodes(root)
        #print allNodes
        self.newList = []
        self.nodeList = []
        for node in allNodes:
            renderNode = RenderNode()
            renderNode.changeRenderProperty("number", node.get("number"))
            renderNode.changeRenderProperty("name", node.get("name"))
            renderNode.changeRenderProperty("nkPath", node.get("nkPath"))
            renderNode.changeRenderProperty("fileName", node.get("fileName"))
            renderNode.changeRenderProperty("frameIn", node.get("frameIn"))
            renderNode.changeRenderProperty("frameOut", node.get("frameOut"))
            renderNode.changeRenderProperty("frameInterval", node.get("frameInterval"))
            self.newList.append(renderNode.number)
            self.nodeList.append(renderNode)
        #print self.nodeList
        self.updateRenderInfo()

    def loadNodesToTable(self):
        self.renderTable.clear()
        #self.renderTable.item

        self.renderTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.renderTable.setRowCount(len(self.nodeList))
        self.renderTable.setHorizontalHeaderItem(0, QTableWidgetItem('Name'))
        self.renderTable.setHorizontalHeaderItem(1, QTableWidgetItem('Frame in'))
        self.renderTable.setHorizontalHeaderItem(2, QTableWidgetItem('Frame out'))
        self.renderTable.setHorizontalHeaderItem(3, QTableWidgetItem('Interval'))
        self.renderTable.setHorizontalHeaderItem(4, QTableWidgetItem('Status'))
        self.verticalHeader = self.renderTable.verticalHeader()
        self.verticalHeader.setDefaultSectionSize(45)
        self.renderTable.setShowGrid(False)
        for renderNode in self.nodeList:
            self.populateTable(renderNode)
        # self.connect(self.renderTable, SIGNAL('itemChanged(QTableWidgetItem*)'), self.changeTable)
        self.renderTable.itemChanged.connect(self.changeTable)

    def updateRenderInfo(self):
        self.newListInfo.setText(" ".join(self.newList))
        self.waitingListInfo.setText(" ".join(self.waitingList))
        self.renderingListInfo.setText(" ".join(self.renderingList))
        self.killedListInfo.setText(" ".join(self.killedList))
        self.finishListInfo.setText(" ".join(self.finishList))

    def changeTable(self, item):
        #print item.row()
        #print item.column()
        #print item.text()
        if item.column() == 1:
            #print "change frame in"
            self.changeNodeProperty(str(item.row()+1), "frameIn", item.text())
        if item.column() == 2:
            #print "change frame out"
            self.changeNodeProperty(str(item.row() + 1), "frameOut", item.text())
        if item.column() == 3:
            #print "change frame interval"
            self.changeNodeProperty(str(item.row() + 1), "frameInterval", item.text())

    def changeNodeProperty(self, number, property, value):
        print "change node %s %s to %s" % (number, property, value)
        tree = RS.read_xml(xml_file)
        root = tree.getroot()
        allNodes = RS.find_nodes(root)
        currentNode = RS.get_node_by_keyvalue(allNodes, {"number":"%s" % number})
        RS.change_node_properties(currentNode, {"%s" % property: "%s" % value})
        RS.write_xml(tree, xml_file)

    def populateTable(self, renderNode):
        renderNodeNameItem = QTableWidgetItem(renderNode.name)
        renderNodeNameItem.setToolTip('%s\n%s' % (renderNode.nkPath, renderNode.fileName))
        renderNodeNameItem.setTextAlignment(Qt.AlignCenter)
        self.renderTable.setItem(int(renderNode.number)-1, 0, renderNodeNameItem)

        renderNodeFrameInItem = QTableWidgetItem(renderNode.frameIn)
        renderNodeFrameInItem.setTextAlignment(Qt.AlignCenter)
        self.renderTable.setItem(int(renderNode.number) - 1, 1, renderNodeFrameInItem)

        renderNodeFrameOutItem = QTableWidgetItem(renderNode.frameOut)
        renderNodeFrameOutItem.setTextAlignment(Qt.AlignCenter)
        self.renderTable.setItem(int(renderNode.number) - 1, 2, renderNodeFrameOutItem)

        renderNodeFrameIntervalItem = QTableWidgetItem(renderNode.frameInterval)
        renderNodeFrameIntervalItem.setTextAlignment(Qt.AlignCenter)
        self.renderTable.setColumnWidth(3, 70)
        self.renderTable.setItem(int(renderNode.number) - 1, 3, renderNodeFrameIntervalItem)

        renderNodeProgressItem = RenderWidget(int(renderNode.number))
        renderNodeProgressItem.updateParentStatus(self.renderingList, self.multiRenderNum)
        # self.connect(renderNodeProgressItem, SIGNAL("newTorender(int)"), self.newToRendering)
        # self.connect(renderNodeProgressItem, SIGNAL("newTowait(int)"), self.newToWaiting)
        # self.connect(renderNodeProgressItem, SIGNAL("renderTokill(int)"), self.renderingToKilled)
        # self.connect(renderNodeProgressItem, SIGNAL("waitTorender(int)"), self.waitingToRendering)
        # self.connect(renderNodeProgressItem, SIGNAL("waitTokill(int)"), self.waitingToKilled)
        # self.connect(renderNodeProgressItem, SIGNAL("finish(int)"), self.renderingToFinish)
        renderNodeProgressItem.newTorender.connect(self.newToRendering)
        renderNodeProgressItem.newTowait.connect(self.newToWaiting)
        renderNodeProgressItem.renderTokill.connect(self.renderingToKilled)
        renderNodeProgressItem.waitTorender.connect(self.waitingToRendering)
        renderNodeProgressItem.waitTokill.connect(self.waitingToKilled)
        renderNodeProgressItem.finish.connect(self.renderingToFinish)
        self.renderTable.setColumnWidth(4, 305)
        self.renderTable.setCellWidget(int(renderNode.number) - 1, 4, renderNodeProgressItem)


    def updateParentStatus(self):
        #print "max number: %s" % self.multiRenderNum
        for i in range(self.renderTable.rowCount()):
            self.renderTable.cellWidget(i, 4).updateParentStatus(self.renderingList, self.multiRenderNum)

    def newToRendering(self, n):
        self.newList.remove(str(n))
        self.renderingList.append(str(n))
        self.renderingList.sort()
        self.updateRenderInfo()
        self.updateParentStatus()

    def newToWaiting(self, n):
        self.newList.remove(str(n))
        self.waitingList.append(str(n))
        self.waitingList.sort()
        self.updateRenderInfo()

    def renderingToKilled(self, n):
        self.renderingList.remove(str(n))
        self.killedList.append(str(n))
        self.killedList.sort()
        self.updateRenderInfo()
        self.updateParentStatus()
        for i in self.waitingList:
            self.renderTable.cellWidget(int(i)-1, 4).waitToRender()
            self.updateParentStatus()

    def waitingToRendering(self, n):
        self.waitingList.remove(str(n))
        self.renderingList.append(str(n))
        self.renderingList.sort()
        self.updateRenderInfo()
        self.updateParentStatus()

    def waitingToKilled(self, n):
        self.waitingList.remove(str(n))
        self.killedList.append(str(n))
        self.killedList.sort()
        self.updateRenderInfo()

    def renderingToFinish(self, n):
        self.renderingList.remove(str(n))
        self.finishList.append(str(n))
        self.finishList.sort()
        self.updateRenderInfo()
        self.updateParentStatus()
        self.showTip()
        for i in self.waitingList:
            self.renderTable.cellWidget(int(i)-1, 4).waitToRender()
            self.updateParentStatus()



    def addNodes(self):
        #print "add nodes"
        if inNuke:
            RN.autoSave()
            newNodes = RN.getNodes()
        else:
            newNodes = testWriteNodes
        for node in newNodes:
            self.renderTable.insertRow(self.renderTable.rowCount())
            tree = RS.read_xml(xml_file)
            root = tree.getroot()
            newNode = RS.add_node(root, {"name":"%s" % node[1], "nkPath":"%s" % node[0], "frameIn":"%s" % node[3], "frameOut":"%s" % node[4], "fileName":"%s" % node[2]})
            RS.write_xml(tree, xml_file)
            newRenderNode = RenderNode()
            newRenderNode.changeRenderProperty("number", newNode.get("number"))
            newRenderNode.changeRenderProperty("name", newNode.get("name"))
            newRenderNode.changeRenderProperty("nkPath", newNode.get("nkPath"))
            newRenderNode.changeRenderProperty("fileName", newNode.get("fileName"))
            newRenderNode.changeRenderProperty("frameIn", newNode.get("frameIn"))
            newRenderNode.changeRenderProperty("frameOut", newNode.get("frameOut"))
            newRenderNode.changeRenderProperty("frameInterval", newNode.get("frameInterval"))
            self.newList.append(newRenderNode.number)
            self.nodeList.append(newRenderNode)
            self.populateTable(newRenderNode)
        self.updateRenderInfo()

    def removeNode(self):
        #print "remove node"
        if self.renderingList == [] and self.waitingList == []:
            currentRow = self.renderTable.currentRow()
            if currentRow >= 0:
                currentStatus = self.renderTable.cellWidget(currentRow, 4).status
                self.renderTable.removeRow(currentRow)
                tree = RS.read_xml(xml_file)
                root = tree.getroot()
                RS.del_node(root, currentRow+1)
                RS.write_xml(tree, xml_file)
                for i in range(self.renderTable.rowCount()):
                    if i>= currentRow:
                        self.renderTable.cellWidget(i, 4).n = str(int(self.renderTable.cellWidget(i, 4).n)-1)
                if currentStatus == "new":
                    for i in self.newList:
                        if int(i) == currentRow+1:
                            self.newList.remove(i)
                if currentStatus == "killed":
                    for i in self.killedList:
                        if int(i) == currentRow+1:
                            self.killedList.remove(i)
                if currentStatus == "finish":
                    for i in self.finishList:
                        if int(i) == currentRow+1:
                            self.finishList.remove(i)
                for i in range(len(self.newList)):
                    if int(self.newList[i]) > currentRow + 1:
                        self.newList[i] = str(int(self.newList[i]) - 1)
                for i in range(len(self.killedList)):
                    if int(self.killedList[i]) > currentRow + 1:
                        self.killedList[i] = str(int(self.killedList[i]) - 1)
                for i in range(len(self.finishList)):
                    if int(self.finishList[i]) > currentRow + 1:
                        self.finishList[i] = str(int(self.finishList[i]) - 1)
                self.updateRenderInfo()

    def clearAllNodes(self):
        #print "clear all"
        if self.renderingList == [] and self.waitingList == []:
            row = self.renderTable.rowCount()
            for i in range(row):
                self.renderTable.removeRow(0)
                tree = RS.read_xml(xml_file)
                root = tree.getroot()
                RS.del_node(root, 1)
                RS.write_xml(tree, xml_file)
            self.newList = []
            self.killedList = []
            self.finishList = []
            self.nodeList = []
            self.updateRenderInfo()

    def renderAllNodes(self):
        #print "render all"
        for i in range(self.renderTable.rowCount()):
            self.renderTable.cellWidget(i, 4).startButtonPushed()

    def killAllNodes(self):
        #print "kill all"
        for i in range(self.renderTable.rowCount()):
            self.renderTable.cellWidget(i, 4).stopRender()

    def showTip(self):
        print 1
        self.showNormal()

class RenderNode():
    def __init__(self):
        self.number = ""
        self.name = ""
        self.nkPath = ""
        self.fileName = ""
        self.frameIn = ""
        self.frameOut = ""
        self.frameInterval = "1"
        #self.renderProgress = "0"
        #self.renderStatus = "new"
    def changeRenderProperty(self, property, value):
        if property == "number":
            self.number = value
        if property == "name":
            self.name = value
        if property == "nkPath":
            self.nkPath = value
        if property == "fileName":
            self.fileName = value
        if property == "frameIn":
            self.frameIn = value
        if property == "frameOut":
            self.frameOut = value
        if property == "frameInterval":
            self.frameInterval = value




class AboutDialog(QWidget):
    def __init__(self):
        super(AboutDialog, self).__init__()
        self.setFixedSize(320, 320)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("About")

        self.setStyleSheet("color: white; background-color: rgb(50, 50, 50)")
        aboutToolbox = QLabel()
        aboutToolbox.setPixmap(QPixmap("%s/logo.png" % GLOBAL_ICON_Path).scaled(300, 100, Qt.KeepAspectRatio))
        aboutVer = QLabel(VER)
        aboutVer.setStyleSheet("font:30px Arial")
        aboutAuthor = QLabel("Author:%s" % AUTHOR)
        aboutAuthor.setAlignment(Qt.AlignRight)
        aboutAuthor.setStyleSheet("font:20px Arial")
        aboutDate = QLabel("Date:%s" % DATE)
        aboutDate.setAlignment(Qt.AlignRight)
        aboutDate.setStyleSheet("font:20px Arial")

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(aboutToolbox)
        self.masterLayout.addWidget(aboutVer)
        self.masterLayout.addWidget(aboutAuthor)
        self.masterLayout.addWidget(aboutDate)
        self.setLayout(self.masterLayout)

        self.adjustSize()
        screenRes = QDesktopWidget().screenGeometry()
        self.move(QPoint(screenRes.width()/2,screenRes.height()/2)-QPoint((self.width()/2),(self.height()/2)))

class CustomProgressBar(QProgressBar):
    def __init__(self):
        super(CustomProgressBar, self).__init__()

        self.setValue(0)
        self.setAlignment(Qt.AlignCenter)
        self.setMaximumWidth(200)
        self.setMinimumWidth(120)
        #self.setMinimumHeight(50)
        self.setStyleSheet("QProgressBar{background-color: rgb(50, 50, 50, 0); border:0.1px solid grey; border-radius:0px; text-align: center;}"
                           "QProgressBar::chunk{background-color: #CD96CD;width: 10px;margin: 0.5px;}")

class QStatusLabel(QLabel):
    def __init__(self):
        super(QStatusLabel, self).__init__()

        self.status = "new"
        self.setToolTip('%s' % self.status)
        self.imageFile = '%s/%s.png' % (GLOBAL_ICON_Path, self.status)
        self.setPixmap(QPixmap(self.imageFile).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))


    def updateStatus(self, status):
        self.status = status
        self.setToolTip('%s' % self.status)
        self.imageFile = '%s/%s.png' % (GLOBAL_ICON_Path, self.status)
        self.setPixmap(QPixmap(self.imageFile).scaled(24, 24))

class ShowHideButton(QLabel):
    buttonClicked = Signal()
    def __init__(self):
        super(ShowHideButton, self).__init__()

        self.show = True
        self.setToolTip("hide setting")
        self.imageFile = '%s/%s.png' % (GLOBAL_ICON_Path, "show_setting")
        self.setPixmap(QPixmap(self.imageFile).scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation))


    def mouseReleaseEvent(self, event):
        if self.show:
            self.imageFile = '%s/%s.png' % (GLOBAL_ICON_Path, "hide_setting")
            self.setPixmap(QPixmap(self.imageFile).scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setToolTip("show setting")
            self.show = False
        else:
            self.imageFile = '%s/%s.png' % (GLOBAL_ICON_Path, "show_setting")
            self.setPixmap(QPixmap(self.imageFile).scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setToolTip("hide setting")
            self.show = True

        # self.emit(SIGNAL('buttonClicked()'))
        self.buttonClicked.emit()


class RenderThread(QThread):
    getPid = Signal(int)
    update = Signal(int)
    def __init__(self, cmd):
        super(RenderThread, self).__init__()
        self.cmd = cmd

    def run(self):
        process = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        pid = process.pid
        self.getPid.emit(int(pid))
        a = process.stdout.readline()
        while a:
            print a
            if a.find("Frame") == 0:
                self.update.emit(int(a.split(" ")[1]))
            a = process.stdout.readline()

        e = process.stderr.readline()
        while e:
            print e
            e = process.stderr.readline()

class RenderWidget(QWidget):
    newTorender = Signal(int)
    newTowait = Signal(int)
    waitTorender = Signal(int)
    renderTokill = Signal(int)
    waitTokill = Signal(int)
    finish = Signal(int)
    def __init__(self, n):
        super(RenderWidget, self).__init__()

        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.n = n
        self.allFrame = 0
        self.cmdList = []
        statusList = ["new", "waiting", "rendering", "killed", "finish"]
        self.status = "new"

        self.parentRenderingNum = 0
        self.parentRenderMaxNum = 0

        self.progressBar = CustomProgressBar()
        self.progressBar.setToolTip('0/0')
        self.renderStatusLabel = QStatusLabel()
        self.renderNodeRender = QLabelButton("render")
        # self.connect(self.renderNodeRender, SIGNAL('buttonClicked()'), self.startButtonPushed)
        self.renderNodeKill = QLabelButton("kill")
        # self.connect(self.renderNodeKill, SIGNAL('buttonClicked()'), self.stopRender)
        self.renderNodeOpen = QLabelButton("open")
        # self.connect(self.renderNodeOpen, SIGNAL('buttonClicked()'), self.openFolder)

        self.renderNodeRender.buttonClicked.connect(self.startButtonPushed)
        self.renderNodeKill.buttonClicked.connect(self.stopRender)
        self.renderNodeOpen.buttonClicked.connect(self.openFolder)

        self.masterLayout = QHBoxLayout()
        self.masterLayout2 = QVBoxLayout()
        self.masterLayout.addWidget(self.progressBar)
        self.masterLayout.addSpacing(20)
        self.masterLayout.addWidget(self.renderStatusLabel)
        self.masterLayout.addSpacing(20)
        self.masterLayout.addWidget(self.renderNodeRender)
        self.masterLayout.addWidget(self.renderNodeKill)
        self.masterLayout.addWidget(self.renderNodeOpen)
        self.masterLayout.addStretch()
        self.masterLayout2.addStretch()
        self.masterLayout2.addLayout(self.masterLayout)
        self.masterLayout2.addStretch()
        self.setLayout(self.masterLayout2)

        self.renderedFrames = []
        self.pidList = []

    def updateParentStatus(self, renderingList, maxNum):
        self.parentRenderingNum = len(renderingList)
        self.parentRenderMaxNum = int(maxNum)

    def startButtonPushed(self):
        if self.status == "new":
            if self.parentRenderingNum < self.parentRenderMaxNum:
                # self.emit(SIGNAL('newTorender(int)'), int(self.n))
                self.newTorender.emit(int(self.n))
                self.startRender()
            else:
                # self.emit(SIGNAL('newTowait(int)'), int(self.n))
                self.newTowait.emit(int(self.n))
                self.status = "waiting"
                self.renderStatusLabel.updateStatus(self.status)

    def waitToRender(self):
        if self.parentRenderingNum < self.parentRenderMaxNum:
            # self.emit(SIGNAL('waitTorender(int)'), int(self.n))
            self.waitTorender.emit(int(self.n))
            self.startRender()

    def startRender(self):
        if self.status in ["new", "waiting"]:
            print "render"
            self.cmdList = createCMDFromXml(self.n)
            self.allFrame = len(getAllFrames(self.n))
            self.progressBar.setValue(0)
            self.jobList = []
            for cmd in self.cmdList:
                self.renderThread = RenderThread(cmd)
                # self.connect(self.renderThread, SIGNAL("getPid(int)"), self.getPid)
                # self.connect(self.renderThread, SIGNAL("update(int)"), self.updateProgress)
                self.renderThread.getPid.connect(self.getPid)
                self.renderThread.update.connect(self.updateProgress)
                self.jobList.append(self.renderThread)
            #print self.jobList
            for p in self.jobList:
                p.start()
                time.sleep(0.02)
            self.status = "rendering"
            self.renderStatusLabel.updateStatus(self.status)

    def stopRender(self):
        if self.status == "rendering":
            print "stop"
            # self.emit(SIGNAL('renderTokill(int)'), int(self.n))
            self.renderTokill.emit(int(self.n))
            self.status = "killed"
            print "begin kill"
            print "pid list: %s" % self.pidList
            for pid in self.pidList:
                self.stopPid(pid)
            print "stop process in job"
            for p in self.jobList:
                p.terminate()
            print "kill finish"
            self.renderStatusLabel.updateStatus(self.status)
        elif self.status == "waiting":
            # self.emit(SIGNAL('waitTokill(int)'), int(self.n))
            self.waitTokill.emit(int(self.n))
            self.status = "killed"
            self.renderStatusLabel.updateStatus(self.status)
        else:
            print "not rendering"

    def openFolder(self):
        filePath = getFilePath(self.n)
        print "open folder: %s" % filePath
        operatingSystem = platform.system()
        if os.path.exists(filePath):
            if operatingSystem == "Windows":
                os.startfile(filePath)
            elif operatingSystem == "Darwin":
                subprocess.Popen(["open", filePath])
            else:
                subprocess.Popen(["xdg-open", filePath])

    def stopPid(self, pid):
        operatingSystem = platform.system()
        if operatingSystem == "Windows":
            print "kill parent: " + str(pid)
            subprocess.Popen("taskkill /F /T /PID %s" % pid, shell=True)
        elif operatingSystem == "Linux":
            import psutil
            for pid in self.pidList:
                for p in psutil.process_iter():
                    if p.pid == int(pid):
                        for child in p.children():
                            for childchild in child.children():
                                print "kill childchild: " + str(childchild.pid)
                                os.system("kill -9 %s" % childchild.pid)
                            print "kill child: " + str(child.pid)
                            os.system("kill -9 %s" % child.pid)
                print "kill parent: " + str(pid)
                os.system("kill -9 %s" % pid)

    def updateProgress(self, value):
        self.renderedFrames.append(value)
        #print self.renderedFrames
        self.progress = int(len(self.renderedFrames) / float(self.allFrame) * 100)
        if self.progress == 100:
            self.status = "finish"
            # self.emit(SIGNAL('finish(int)'), int(self.n))
            self.finish.emit(int(self.n))
            print "render finish"
            #for pid in self.pidList:
            #    self.stopPid(pid)
        self.progressBar.setValue(self.progress)
        self.progressBar.setToolTip('%s/%s' % (len(self.renderedFrames), self.allFrame))
        self.renderStatusLabel.updateStatus(self.status)

    def getPid(self, pid):
        if self.status == "killed":
            self.stopPid(pid)
        self.pidList.append(pid)
        print self.pidList


class QLabelButton(QLabel):
    buttonClicked = Signal()
    def __init__(self, name):
        super(QLabelButton, self).__init__()

        self.setToolTip("<font color=#FFFFFF>%s</font>" % name)
        self.imageFile = '%s/%s.png' % (GLOBAL_ICON_Path, name)
        self.setPixmap(QPixmap(self.imageFile).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40)")

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: rgb(40, 40, 40, 0)")

    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: rgb(70, 70, 70)")

    def mouseReleaseEvent(self, event):
        # self.emit(SIGNAL('buttonClicked()'))
        self.buttonClicked.emit()
        self.setStyleSheet("background-color: rgb(40, 40, 40)")


batchRenderWindow = BatchRenderWindow()


def main():
    batchRenderWindow.reset()
    batchRenderWindow.loadNodesFromXml()
    batchRenderWindow.loadNodesToTable()
    batchRenderWindow.show()

       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    batchRenderWindow = BatchRenderWindow()
    batchRenderWindow.show()
    app.exec_()

