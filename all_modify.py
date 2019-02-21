#coding: utf-8
from tkinter import *
import tkinter.filedialog
import os
import stat
import re
import io
import sys

#可配置区 1 工程的Assets目录
path = '../../Client201215/Assets/'
insertStr = 'Sat'
headStr = 'MyGirl'


modifyList = []

#存储所有的cs文件的内容，键值是文件名，值为文件的内容。
all_filecontent={}

#存储所有的cs文件对应的meta文件中的guid，键值是文件名，值为文件的guid
all_class_guid={}

#存储所有的unity文件的内容，键值是文件名，值为文件的内容。
#因为unity文件中会包含对类的引用，当类的文件随类名改变后，guid需要替换成新的 如：
#m_Script: {fileID: 11500000, guid: f9ac8d30c6a0d9642a11e5be4c440740, type: 3}
all_unity_filecontent={}

#存储所有的prefab文件的内容，键值是文件名，值为文件的内容。
#因为prefab文件中会包含对类的引用，当类的文件随类名改变后，guid需要替换成新的 如：
#m_Script: {fileID: 11500000, guid: f9ac8d30c6a0d9642a11e5be4c440740, type: 3}
all_prefab_filecontent={}

#所有的类的字符串
all_class = []

#所有函数的字符串列表
all_function = []

#所有的类的字符串的原始文件
all_class_file = []

#所有的读取报错的文件
all_error_file_decs = []

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #改变标准输出的默认编码

#缓存文件，并且缓存类名    
#从一行数据中取得class的字符串，如果这行中有class的标识符
#如：public class DynamicBoneA : MonoBehaviour 则返回： DynamicBoneA
def findClassInCs(fileName):
    if '.meta' in fileName:
        findGUIDInMeta(fileName)
    else:
        file_data = ""
        className = ""
        hasChanged = False
        file_object = open(fileName,"r",encoding='utf8')
        #print('文件: %s'%effFile)
        hasError = 0
        lineIter = 0
        try:
            for line in file_object:
                file_data += line
                lineIter = lineIter + 1
                resultes = re.findall( r'.*public\s+class\s(.*?) .*', line)
                for result in resultes:
                    print(result)
                    all_class.append(result)
                    all_class_file.append(fileName)
           
        except UnicodeDecodeError as e:
            print('捕获了一个错误：{}'.format(e))
            errorStr = '捕获了一个错误：{}'.format(e) + ' ' + fileName + ' line num is :' + str(lineIter)
            all_error_file_decs.append(errorStr)
            hasError = 1
        else:
            if hasError == 0:
                all_filecontent[fileName] = file_data   
        finally:
            file_object.close( )

        
def findGUIDInMeta(fileName):
    file_object = open(fileName,"r",encoding='utf8')
    #print('文件: %s'%effFile)
    hasError = 0
    lineIter = 0
    for line in file_object:
        lineIter = lineIter + 1
        if 'guid' in line:
            guidStr  = line.split(":")[1]
            guidStr = guidStr.strip()
            all_class_guid[fileName] = guidStr
            print(guidStr)
        
# 见all_unity_filecontent
def cacheUnityFileContent(fileName):
    file_data = ""
    #找到*.unity 文件，不用理会*.unity.meta文件
    if ('.meta' in fileName) == 0:
        #print('unity文件: %s'%fileName)
        file_object = open(fileName,"r",encoding='utf8')
        hasError = 0
        lineIter = 0
        try:
            for line in file_object:
                lineIter = lineIter + 1
                file_data += line
                
        except UnicodeDecodeError as e:
            print('捕获了一个错误：{}'.format(e))
            errorStr = '捕获了一个错误：{}'.format(e) + ' ' + fileName + ' line num is :' + str(lineIter)
            all_error_file_decs.append(errorStr)
            hasError = 1
        else:
            if hasError == 0:
                all_unity_filecontent[fileName] = file_data
        finally:
            file_object.close()
   
#见all_prefab_filecontent
def cachePrefabFileContent(fileName):
    file_data = ""
    if ('.meta' in fileName)== 0:
        #print('prefab文件: %s'%fileName)
        file_object = open(fileName,"r",encoding='utf8')
        hasError = 0
        lineIter = 0
        try:
            for line in file_object:
                lineIter = lineIter + 1
                file_data+= line
                
        except UnicodeDecodeError as e:
                print('捕获了一个错误：{}'.format(e))
                errorStr = '捕获了一个错误：{}'.format(e) + ' ' + fileName + ' line num is :' + str(lineIter)
                all_error_file_decs.append(errorStr)
                hasError = 1
        else:      
            if hasError == 0:
                all_prefab_filecontent[fileName] = file_data
            
        finally:
            file_object.close()   
            
def traverse(f):
    fs = os.listdir(f)
    for f1 in fs:
        tmp_path = os.path.join(f,f1)
        if not os.path.isdir(tmp_path):
            if '.cs' in tmp_path:
                findClassInCs(tmp_path)
            elif '.unity' in tmp_path:
                cacheUnityFileContent(tmp_path)
            elif '.prefab' in tmp_path:
                cachePrefabFileContent(tmp_path)
        else:
            #print('文件夹：%s'%tmp_path)
            traverse(tmp_path)
            
def fetchNewString(oldStr):
    str_list = list(oldStr)
    nPos = int(len(oldStr) /2)
    str_list.insert(nPos,insertStr)
    str2 = "".join(str_list)
    newStr = headStr + str2
    return newStr

def saveModifyFileList():
    fileObject = open('modifyList.xml', 'w')  
    for modifyOne in modifyList:
        print(modifyOne)
        fileObject.write(modifyOne)  
        fileObject.write('\n') 
    fileObject.close()
    
root = Tk()


#path = tkinter.filedialog.askdirectory()

#遍历所有文件，缓存起类和文件
traverse(path)

print('搜索结束')

for error_file in all_error_file_decs:
    print('error file is ' +  error_file)

"""
#处理替换所有的类字符串
for className in all_class:
    print('beging process class:%s'% className)
    newClassName = fetchNewString(className)
    print('beging process newClass:%s'% newClassName)
    for fileKey in all_filecontent.keys():
        fileContent = all_filecontent[fileKey]
        if className in fileContent:
            f = open(fileKey,'w') # 写模式
            try:
                newFileContent = fileContent.replace(className,newClassName)
                all_filecontent[fileKey] = newFileContent
                f.write(newFileContent)
                print('修改了文件 %s'%fileKey)
            finally:
                f.close()
            

#先去重
all_class_file = list(set(all_class_file))

all_class_modify_guid={}
#修改修改了类名的文件名
for classFile in all_class_file:
    print('old classFile is :%s'%classFile)
    endIter  = classFile.find('.cs')
    beginIter  = classFile.rfind('\\')
    fileName = classFile[beginIter+1:endIter]
    fileNamePath = classFile[0 : beginIter+1]
    newFileName = fetchNewString(fileName)
    newClassFile = fileNamePath + newFileName + ".cs"
    print('new classFile is :%s'%newClassFile)
    os.rename(classFile,newClassFile)
    newclassFileKey = classFile+'.meta'
    all_class_modify_guid[newclassFileKey] = all_class_guid[newclassFileKey]
    
#将旧的guid保存到文件中,文件格式如下： 旧的文件的名称（由旧的文件名可以推出新的文件名），旧的guid,
fileObject = open('classModifyList.xml', 'w')  
for classmodifyKey in all_class_modify_guid.keys():
    modifyOne = classmodifyKey + '######,######'+all_class_modify_guid[classmodifyKey]
    print(modifyOne)
    fileObject.write(modifyOne)  
    fileObject.write('\n') 
fileObject.close()

#让unity解析完生成新的meta文件....

#根据新生成的guid替换unity文件和prefab文件中的guid



#print('所有被修改的文件列表可在modifyList.xml中查看')
#saveModifyFileList()
"""


