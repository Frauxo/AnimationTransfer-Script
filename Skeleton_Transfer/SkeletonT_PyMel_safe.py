import pymel.core as pm
import pymel.core.datatypes as dt

root = pm.ls( sl=True )[0]

animLength = (pm.keyframe(q=True, kc=True)) / 10
fastAnim = 100
getBindPose = 0

jointRotationSource = []
jointOrientationSource = []
jointRotationTarget = []

isolatedRotation = []
worldRotation = []
translatedRotation = []

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
        pm.currentTime(0) # Set keyframe to 0 to get bindPose
        parentMatrix = 1
        sParents = getParentMatrix(child, parentMatrix)

        pm.currentTime(keys) # Set the keyframe back to the current keyframe
        sOrientation = keyframeOrientationSource

        worldRotation.append(sOrientation.inverse() * sParents.inverse() * isolatedRotation[jointNumber] * sParents * sOrientation)
        jointNumber += 1

    return jointNumber

def getHierarchyTarget(node, keys, jointNumber = 0):
    for child in node.getChildren():
        if child.numChildren() > 0:
            jointNumber = getHierarchyTarget(child, keys, jointNumber)
        # -Get Rotation and orientation from target-
        if getBindPose == 0:
            jointRotationTarget.append(child.getRotation().asMatrix())

        keyframeRotationTarget = child.getRotation().asMatrix()
        keyframeOrientationTarget = child.getOrientation().asMatrix()

        # -TranslatedRotation-
        tOrientation = keyframeOrientationTarget

        pm.currentTime(0) # Set keyframe to 0 to get bindPose
        parentMatrix = 1
        tParents = getParentMatrix(child, parentMatrix)

        pm.currentTime(keys)
        translatedRotation.append(tOrientation * tParents * worldRotation[jointNumber] * tParents.inverse() * tOrientation.inverse())
        translatedRotation[jointNumber] = jointRotationTarget[jointNumber] * translatedRotation[jointNumber]

        # -Set Rotation-
        child.setRotation(dt.degrees(dt.EulerRotation(translatedRotation[jointNumber])))
        pm.setKeyframe(child)

        jointNumber += 1
    return jointNumber

# Get the parents Matrix (recursive function)
def getParentMatrix(child, parentMatrix):
    parent = child.getParent()
    if type(parent) == pm.nodetypes.Joint:
        parentMatrix = getParentMatrix(parent, parentMatrix)
        parentMatrix = (parent.getRotation().asMatrix() * parent.getOrientation().asMatrix()) * parentMatrix

    return parentMatrix

#-----------MAIN--------------
# for joint in root.getChildren():

for keys in range(fastAnim):
    pm.currentTime(keys)

    del isolatedRotation[:]
    del worldRotation[:]
    del translatedRotation[:]

    root = pm.ls(sl=True)[0]

    rootTranslation = root.getTranslation()
    rootOrientation = root.getOrientation()
    rootRotation = root.getRotation()

    getHierarchySource(root, keys)

    root = pm.ls(sl=True)[1]

    getHierarchyTarget(root, keys)

    getBindPose = 1

    #Set Rotation
    root.setOrientation(rootOrientation)
    root.setRotation(rootRotation)
    root.setTranslation(rootTranslation)
    pm.setKeyframe(root)

pm.currentTime(0)