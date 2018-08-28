# -*- coding: utf-8 -*-
# __author__ = 'XingHuan-PC'
# 2017/1/21


import nuke
import os

def getNodes():
    nodesList = []
    nodes = nuke.selectedNodes()
    nodes.reverse()
    for node in nodes:
        if node.Class() == "Write":
            nodeInfo = []
            nodeInfo.append(nuke.root().name())
            nodeInfo.append(node.name())
            file = node.knob("file").getEvaluatedValue()
            nodeInfo.append(file)
            nodeInfo.append(str(int(nuke.root().knob("first_frame").value())))
            nodeInfo.append(str(int(nuke.root().knob("last_frame").value())))
            nodesList.append(nodeInfo)
    print nodesList
    return nodesList

# getNodes()
# [['F:/Temp/test03/temp.nk', 'Write2', 'F:/Temp/test03/test02/test_write2.%04d.jpg', '1', '100'], ['F:/Temp/test03/temp.nk', 'Write1', 'F:/Temp/test03/test02/test_write1.%04d.jpg', '1', '100']]



def getExecutablePath():
    return nuke.env["ExecutablePath"]


def autoSave():
    rootNode = nuke.root()
    if rootNode.proxy():
        rootNode.setProxy(False)
    nuke.scriptSave()

