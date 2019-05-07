import pymel.core as pm
import pymel.core.datatypes as dt
import loadXMLUI as LUI

root = pm.ls( sl=True )[0]

animLength = (pm.keyframe(q=True, kc=True)) / 10
fastAnim = 40
getBindPose = 0
firstPass = 0

jointRotationSource = []
jointOrientationSource = []
jointRotationTarget = []

isolatedRotation = []
worldRotation = []
translatedRotation = []

def printHierarchy(node, typeOfList):
    for child in node.getChildren():
        printHierarchy(child, typeOfList)
        if typeOfList == "source":
            LUI.sourceHierarchy.append(child)
        else:
            LUI.targetHierarchy.append(child)

def getHierarchySource(node, keys, jointNumber = 0):
    for child in node.getChildren():
        if child.numChildren() > 0:
            jointNumber = getHierarchySource(child, keys, jointNumber)
        # -Get Rotation and orientation from source-

        if getBindPose == 0:
            jointRotationSource.append(child.getRotation().asMatrix())
            jointOrientationSource.append(child.getOrientation().asMatrix())

        keyframeRotationSource = child.getRotation().asMatrix()
        keyframeOrientationSource = child.getOrientation().asMatrix()

        # -IsolatedRotation-
        matrixSource = jointRotationSource[jointNumber]

        isolatedRotation.append(matrixSource.inverse() * keyframeRotationSource)

        # -WorldRotation-
        #pm.currentTime(0) # Set keyframe to 0 to get bindPose
        parentMatrix = 1
        sParents = getParentMatrix(child, parentMatrix)

        #pm.currentTime(keys) # Set the keyframe back to the current keyframe
        sOrientation = keyframeOrientationSource

        worldRotation.append(sOrientation.inverse() * sParents.inverse() * isolatedRotation[jointNumber] * sParents * sOrientation)
        jointNumber += 1

    return jointNumber

def getHierarchyTarget(node, keys, jointNumber = 0, targetNumber = 0):
    for child in node.getChildren():
        if child.numChildren() > 0:
            jointNumber, targetNumber = getHierarchyTarget(child, keys, jointNumber, targetNumber)
        # -Get Rotation and orientation from target-
        if LUI.targetIndex[targetNumber] > -1:
            if getBindPose == 0:
                jointRotationTarget.append(child.getRotation().asMatrix())

            keyframeRotationTarget = child.getRotation().asMatrix()
            keyframeOrientationTarget = child.getOrientation().asMatrix()

            # -TranslatedRotation-
            tOrientation = keyframeOrientationTarget

            #pm.currentTime(0) # Set keyframe to 0 to get bindPose
            parentMatrix = 1
            tParents = getParentMatrix(child, parentMatrix)
            #pm.currentTime(keys)
            translatedRotation.append(tOrientation * tParents * worldRotation[jointNumber] * tParents.inverse() * tOrientation.inverse())
            translatedRotation[jointNumber] = jointRotationTarget[jointNumber] * translatedRotation[jointNumber]
            jointNumber += 1

        targetNumber += 1

    return jointNumber, targetNumber

def setHierarchyTarget(node, jointNumber = 0, targetNumber = 0):
    for child in node.getChildren():
        if child.numChildren() > 0:
            jointNumber, targetNumber = setHierarchyTarget(child, jointNumber, targetNumber)
        # -Set Rotation-
        if LUI.targetIndex[targetNumber] < len(LUI.targetHierarchy) + 1:
            if LUI.targetIndex[targetNumber] > -1:
                child.setRotation(dt.degrees(dt.EulerRotation(translatedRotation[LUI.targetIndex[targetNumber]])))
                pm.setKeyframe(child)
                #print child
                #print LUI.targetHierarchy[jointNumber], "\n"
                jointNumber += 1
        else:
            jointNumber += 1

        targetNumber += 1

    return jointNumber, targetNumber

# Get the parents Matrix (recursive function)
def getParentMatrix(child, parentMatrix):
    parent = child.getParent()
    if type(parent) == pm.nodetypes.Joint:
        parentMatrix = getParentMatrix(parent, parentMatrix)
        parentMatrix = dt.EulerRotation(parent.rotate.get(t = 0)).asMatrix()* dt.EulerRotation(parent.jointOrient.get(t = 0)).asMatrix()* parentMatrix

    return parentMatrix

#-----------MAIN--------------
# for joint in root.getChildren():

