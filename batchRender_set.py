# -*- coding: utf-8 -*-
# __author__ = 'XingHuan-PC'
# 2017/1/14

import sys
import os
import shutil
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom



# -----------------------------------------
# xml
# -----------------------------------------

def fixed_writexml(self, writer, indent="", addindent="", newl=""):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort(reverse=True)

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 \
          and self.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
            writer.write(">")
            self.childNodes[0].writexml(writer, "", "", "")
            writer.write("</%s>%s" % (self.tagName, newl))
            return
        writer.write(">%s"%(newl))
        for node in self.childNodes:
            if node.nodeType is not minidom.Node.TEXT_NODE:
                node.writexml(writer,indent+addindent,addindent,newl)
        writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))
minidom.Element.writexml = fixed_writexml

def read_xml(path):
    tree = ET.ElementTree()
    tree.parse(path)
    return tree

def write_xml(tree, out_path):
    if not os.path.exists(out_path):
        f = open(out_path, 'w')
        f.close()
    filePath = os.path.split(out_path)[0]
    fileName = os.path.split(out_path)[1]
    # print filePath
    # print fileName
    backupPath = "%s/backup" % filePath
    if not os.path.exists(backupPath):
        os.makedirs(backupPath)
    # shutil.copy(out_path, backupPath)
    # print "%s/%s" % (backupPath, fileName)
    # print time.strftime("%m-%d %H:%M:%S", time.localtime(time.time()))
    newName = "%s/%s_%s.%s" % (backupPath, fileName.split(".")[0], time.strftime("%m_%d_%H_%M_%S", time.localtime(time.time())), fileName.split(".")[1])
    if not os.path.exists(newName):
        shutil.copy(out_path, backupPath)
        os.rename("%s/%s" % (backupPath, fileName), newName)
    tree.write(out_path, encoding="utf-8",xml_declaration=True)
    tree2 = minidom.parse(out_path)
    #print tree2.toprettyxml()
    f = open(out_path, 'w')
    tree2.writexml(f, addindent = '\t', newl = '\n',encoding = 'utf-8')
    f.close()

def is_match(node, kv_map):
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True

#---------------search---------------

def find_nodes(root):
    return root.findall("node")

def find_setting(root):
    return root.findall("setting")[0]

def get_node_by_keyvalue(allNodes, kv_map):
    result_node = None
    for node in allNodes:
        if is_match(node, kv_map):
            result_node = node
    return result_node


#---------------change---------------

def add_node(root, kv_map):
    exist_nodes_number = len(root.findall("node"))
    element = None
    element = ET.SubElement(root, "node")
    element.set("number", "%s" % (exist_nodes_number + 1))
    for key in kv_map:
        element.set(key, kv_map.get(key))
    element.set("frameInterval", "1")
    return element


def del_node(root, number):
    for node in root.findall("node"):
        if node.get("number") == str(number):
            root.remove(node)
    for node in root.findall("node"):
        if int(node.get("number")) > int(number):
            temp = str(int(node.get("number")) - 1)
            node.set("number", temp)

def change_node_properties(node, kv_map):
    for key in kv_map:
        node.set(key, kv_map.get(key))
    return 1

def change_setting(setting, kv_map):
    for key in kv_map:
        setting.set(key, kv_map.get(key))


'''
xml_file = "F:/Temp/pycharm/BatchRender test v1.0/test.xml"
tree = read_xml(xml_file)
root = tree.getroot()

allNodes = find_nodes(root)
print allNodes
node = get_node_by_keyvalue(allNodes, {"number":"1"})
print node.get("name")

setting = find_setting(root)
print setting
change_setting(setting, {"threads":"8"})

newNode = add_node(root, {"name":"Write2", "nkPath":"/job/test.nk", "frameIn":"1", "frameOut":"50"})
change_node_properties(newNode, {"frameInterval":"2"})
#del_node(root, 1)

write_xml(tree, xml_file)
'''









