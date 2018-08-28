import nuke
import batchRender

toolbox_menu = nuke.menu("Nuke").addMenu("Scripts/batchRender_v1.3")
toolbox_menu.addCommand("batchRender", batchRender.main, "", icon="")
