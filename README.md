# BatchRender
Batch background render in nuke

This script can render more than one node at same time, no matter if the nodes are in one nk file.

You can set how many nodes can be rendered at same time. The number of process of nuke for rendering depend on this number. For example, my computer has 8 CPUs so if I render 2 nodes at same time, there will be 4 processes for every render node. If you render a mov or mp4 file, it will use 1 process by default.

Install:
Put the “BatchRender_v1.3” folder in plugin path of nuke(For example, on my computer I put it in “C:\Users\john\.nuke”) and add the following line into the “init.py”:

nuke.pluginAddPath('BatchRender_v1.3')


IMPORTENT: When first using this tool, press the 'apply' button to set the default setting.

