import maya.cmds as cmds
import os
def ui():
    windowID='PlayblastM'
    if cmds.window(windowID, ex=True):
        cmds.deleteUI(windowID)

    window= cmds.window(windowID,t='PlayblastM',  rtf=0, s=1, mnb=0, mxb=0)
    master=cmds.columnLayout()

    cmds.rowColumnLayout(nc = 1)
    cmds.button( l = 'Render Setting', w= 400, c = 'RenderSettingButtonCommand()')
    
    cmds.rowColumnLayout(nr = 1)
    cmds.textField('camTextBox', w = 300, tx = 'please select a camera', ed = 0)
    cmds.button(l = 'Pick',w = 100 , c = 'pickButtonCommand()')
    cmds.setParent('..')

    cmds.text(l = 'OutPut File Path',h=25)
    cmds.rowColumnLayout(nr = 1)
    cmds.textField('pathTextBox' , w = 400 , text= 'G:\Praxis_Temp\Praxis_CFX\To CFX Team\To Seongil\Temp')
    cmds.setParent('..')

    cmds.rowColumnLayout(nr = 1)
    cmds.text(l = 'StartFrame',w = 70)
    cmds.textField('startIntFil',w = 130)
    cmds.text(l = 'EndFrame',w = 70)
    cmds.textField('endIntFil',w = 130)
    cmds.setParent('..')




    cmds.button(l = 'Blast' , c = 'blastCommand()')
    
    cmds.setParent(master)
    
    cmds.showWindow(windowID)
    
def RenderSettingButtonCommand():
    cmds.RenderGlobalsWindow()



def camSplitName(camObject):
    cam = camObject
    
    splitCamName = cam.split('_')
    resultDic = {}
    resultDic['startValue'] = splitCamName[2]
    resultDic['endValue'] = splitCamName[3]
    
    return resultDic

def pickButtonCommand():
    sels = cmds.ls(sl = 1)
    cmds.textField('camTextBox', e = True , text = sels[0])
    camState=camSplitName(sels[0])
    
    cmds.textField('startIntFil',e = True , text = camState['startValue'])
    cmds.textField('endIntFil',e = True , text = camState['endValue'])


def getFileName():
    """
    해당 마야 씬파일의 이름을 구한다
    """
    getFull = cmds.file(q = 1 , sceneName = 1)
    firSplit = getFull.split('/')
    secSplit = firSplit[-1].split('.')
    
    return secSplit[0]

def blastCommand():
    startValueGet = cmds.textField('startIntFil',text = True , q = True)
    endValueGet = cmds.textField('endIntFil',text = True , q = True)
    pathStringGet = r'{}'.format(cmds.textField('pathTextBox' , text= True , q = 1))
    camStringGet = cmds.textField('camTextBox',text = True , q = True)
    mayaFileNameGet = getFileName()
    pathRe = pathStringGet.split('\\')
    joinPath = '//'.join(pathRe)
    outputFullPath =joinPath + '//' + mayaFileNameGet +'.mov'
  

    
    cmds.select(cl=True)
    res_width = cmds.getAttr("defaultResolution.width")
    res_height = cmds.getAttr("defaultResolution.height")
    cmds.lookThru(camStringGet)
    
    cmds.playblast(startTime=int(startValueGet), endTime=int(endValueGet), f=outputFullPath, fmt='qt', forceOverwrite=True,compression="PNG", quality=100,v=True, p=100, w = res_width, h = res_height)

ui()




