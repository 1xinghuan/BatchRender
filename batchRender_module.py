# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 10/23/2017


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S'
                    )

                    

                    

inNuke = False
try:
    import nuke
    import nukescripts
    inNuke = True
    if int(nuke.env ["NukeVersionMajor"]) < 11:
        from PySide.QtCore import *
        from PySide.QtGui import *
        print "using pyside"
    else:
        from PySide2.QtCore import *
        from PySide2.QtGui import *
        from PySide2.QtWidgets import *
        print "using pyside2"
except ImportError:
    print "not in nuke" # pycharm
    try:
        from PySide.QtCore import *
        from PySide.QtGui import *
        print "using pyside"
    except ImportError:
        from PyQt4.QtCore import *
        from PyQt4.QtGui import *
        Signal = pyqtSignal
        print "using pyqt4"
    pass

    



forUser = 0    # 0:single ; 1:multi
