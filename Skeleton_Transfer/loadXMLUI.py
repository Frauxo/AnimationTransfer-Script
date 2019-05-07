from maya import OpenMayaUI as omui
import pymel.core as pm
import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
import SkeletonT_PyMel as st
reload(st)

sourceRoot = pm.ls(sl=True)[0]
targetRoot = pm.ls(sl=True)[1]
sourceHierarchy = []
targetHierarchy = []
targetIndex = []

def getMayaWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    mayaWin = wrapInstance(long(mayaWinPtr), QWidget)


def loadUI(path):
    loader = QUiLoader()
    uiFile = QFile(path)

    dirIconShapes = ""
    buff = None

    if uiFile.exists():
        dirIconShapes = path
        uiFile.open(QFile.ReadOnly)

        buff = QByteArray(uiFile.readAll())
        uiFile.close()
    else:
        print "UI file missing! Exiting..."
        exit(-1)

    fixXML(path, buff)
    qbuff = QBuffer()
    qbuff.open(QBuffer.ReadOnly | QBuffer.WriteOnly)
    qbuff.write(buff)
    qbuff.seek(0)
    ui = loader.load(qbuff, parentWidget=getMayaWin())
    ui.path = path

    return ui


def fixXML(path, qbyteArray):
    # first replace forward slashes for backslashes
    if path[-1] != '/':
        path += '/'
    path = path.replace("/", "\\")

    # construct whole new path with <pixmap> at the begining
    tempArr = QByteArray("<pixmap>" + path + "\\")

    # search for the word <pixmap>
    lastPos = qbyteArray.indexOf("<pixmap>", 0)
    while lastPos != -1:
        qbyteArray.replace(lastPos, len("<pixmap>"), tempArr)
        lastPos = qbyteArray.indexOf("<pixmap>", lastPos + 1)
    return


class UIController:
	def __init__(self, ui):
		# Connect each signal to it's slot one by one

		ui.Transfer.clicked.connect(self.TransferAnimation)
		ui.L_Up.clicked.connect(lambda: self.L_Up(ui))
		ui.R_Up.clicked.connect(lambda: self.R_Up(ui))
		ui.L_Delete.clicked.connect(lambda: self.L_Delete(ui))
		ui.R_Delete.clicked.connect(lambda: self.R_Delete(ui))
		ui.L_Down.clicked.connect(lambda: self.L_Down(ui))
		ui.R_Down.clicked.connect(lambda: self.R_Down(ui))

		self.getLists(ui)
		self.ui = ui

		ui.setWindowFlags(Qt.WindowStaysOnTopHint)
		ui.show()


	def TransferAnimation(self):
		for st.keys in range(st.fastAnim):
			pm.currentTime(st.keys)

			del st.isolatedRotation[:]
			del st.worldRotation[:]
			del st.translatedRotation[:]

			root = pm.ls(sl=True)[0]

			rootTranslation = root.getTranslation()
			rootOrientation = root.getOrientation()
			rootRotation = root.getRotation()

			st.getHierarchySource(root, st.keys)

			root = pm.ls(sl=True)[1]

			st.getHierarchyTarget(root, st.keys)
			st.setHierarchyTarget(root)
			st.getBindPose = 1

			# Set Rotation
			root.setOrientation(rootOrientation)
			root.setRotation(rootRotation)
			root.setTranslation(rootTranslation)
			pm.setKeyframe(root)

	def getLists(self, ui):
		ui.SourceRoot.setText(str(sourceRoot))
		del sourceHierarchy[:]
		st.printHierarchy(sourceRoot, "source")

		self.updateSourceList(ui, sourceHierarchy)

		ui.TargetRoot.setText(str(targetRoot))
		del targetHierarchy[:]
		st.printHierarchy(targetRoot, "target")

		self.updateTargetList(ui, targetHierarchy)

		if st.firstPass == 0:
			for nrOfJoints in range(len(targetHierarchy)):
				targetIndex.append(nrOfJoints)
			st.firstPass = 1

	def updateSourceList(self, ui, sourceHierarchy):
		sourceModel = QStandardItemModel(ui.SourceList)

		for joint in sourceHierarchy:
			item = QStandardItem(str(joint))
			sourceModel.appendRow(item)

		ui.SourceList.setModel(sourceModel)

	def updateTargetList(self, ui, targetHierarchy):
		targetModel = QStandardItemModel(ui.TargetList)
		for joint in targetHierarchy:
			item = QStandardItem(str(joint))
			targetModel.appendRow(item)

		ui.TargetList.setModel(targetModel)

	def L_Up(self, ui):
		index = ui.SourceList.currentIndex()
		itemText = str(index.data())

		selected = pm.select(itemText)
		selectedJoint = pm.ls(sl=True)[0]
		pm.undo()

		temp = sourceHierarchy[index.row()]
		sourceHierarchy[index.row()] = sourceHierarchy[index.row() -1]
		sourceHierarchy[index.row() - 1] = temp

		self.updateSourceList(ui, sourceHierarchy)

	def R_Up(self, ui):
		index = ui.TargetList.currentIndex()
		itemText = str(index.data())

		selected = pm.select(itemText)
		selectedJoint = pm.ls(sl=True)[0]
		pm.undo()

		temp = targetHierarchy[index.row()]
		targetHierarchy[index.row()] = targetHierarchy[index.row() -1]
		targetHierarchy[index.row() - 1] = temp

		tempIndex = targetIndex[index.row()]
		targetIndex[index.row()] = targetIndex[index.row() - 1]
		targetIndex[index.row() - 1] = tempIndex

		self.updateTargetList(ui, targetHierarchy)

	def L_Delete(self, ui):
		index = ui.SourceList.currentIndex()

		del sourceHierarchy[index.row()]
		print sourceHierarchy

		self.updateSourceList(ui, sourceHierarchy)

	def R_Delete(self, ui):
		index = ui.TargetList.currentIndex()

		if len(targetHierarchy) > len(sourceHierarchy):
			targetIndex[index.row()] = -1
			for targets in range(len(targetIndex)):
				if targets > index.row():
					targetIndex[targets] -= 1
		else:
			targetIndex[index.row()] = len(targetIndex) + 1

		del targetHierarchy[index.row()]
		print targetIndex
		self.updateTargetList(ui, targetHierarchy)

	def L_Down(self, ui):
		index = ui.SourceList.currentIndex()
		itemText = str(index.data())

		selected = pm.select(itemText)
		selectedJoint = pm.ls(sl=True)[0]
		pm.undo()

		temp = sourceHierarchy[index.row()]
		sourceHierarchy[index.row()] = sourceHierarchy[index.row() + 1]
		sourceHierarchy[index.row() + 1] = temp

		self.updateSourceList(ui, sourceHierarchy)

	def R_Down(self, ui):
		index = ui.TargetList.currentIndex()
		itemText = str(index.data())

		selected = pm.select(itemText)
		selectedJoint = pm.ls(sl=True)[0]
		pm.undo()

		temp = targetHierarchy[index.row()]
		targetHierarchy[index.row()] = targetHierarchy[index.row() + 1]
		targetHierarchy[index.row() + 1] = temp

		tempIndex = targetIndex[index.row()]
		targetIndex[index.row()] = targetIndex[index.row() + 1]
		targetIndex[index.row() + 1] = tempIndex

		self.updateTargetList(ui, targetHierarchy)