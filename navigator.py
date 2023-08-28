# encoding=utf-8
from cmath import cos, sin, tan
import torch
import numpy as np
import pickle
import h5py

import os

import time
import math
import random

from model import model1000

def distance(embeddings1, embeddings2):
    # print(type(embeddings1),type(embeddings2))
    diff = np.subtract(embeddings1, embeddings2)
    # print(diff)
    dist = np.sum(np.square(diff))
    # print(dist)
    return dist

class Navigator:
    def __init__(self) -> None:
        # config
        self.EEGDATA = "EEGDATA/"
        self.EEGDB = "EEGDB/"
        self.threshold = 350
        # 加载脑电识别模型
        self.model = model1000()
        self.model = self.model.eval()
        self.model.load_state_dict(torch.load("./model1000.pth", map_location=torch.device('cpu')))
        # 特征库
        self.feature_library = []
        # Faster Search
        self.name_library = []

        self.hit = {}
        self.userStatus = {}

        self.reload()

    def userStatusToggle(self,Name):
        if Name not in self.userStatus.keys():
            self.userStatus[Name] = "Disabled"
        else:
            if self.userStatus[Name] == "Disabled":
                self.userStatus[Name] = "Enabled"
            else:
                self.userStatus[Name] = "Disabled"
        return self.userStatus[Name]
    
    def eegList(self,Name="",Status="")->list:
        eegList = []
        for eeg in self.feature_library:

            if Name != "":
                if Name not in eeg['name']:
                    continue
            
            if Status!="":
                if eeg['status']!=Status:
                    continue

            item = {}
            item['Name'] = eeg['name']
            try:
                item['Hit'] = self.hit[eeg['name']]
            except KeyError:
                self.hit[eeg['name']] = 0
                item['Hit'] = 0
            try:
                item['Status'] = self.userStatus[eeg['name']]
            except KeyError:
                self.userStatus[eeg['name']] = "Enabled"
                item['Status'] = "Enabled"
            item['Extro'] = eeg['extro']
            # item['Operation'] = "DEM"
            eegList.append(item)
        if len(eegList)==0:
            item = {}
            # item['nothing'] = "*"

            eegList.append(item)
        return eegList

    def reg(self,eegData,name:str, extro:str):
        if name in self.name_library:
            return 201, "Add user failed.\nUser existed"
        print(eegData.shape)
        # eegData = eegData.transpose(1,0)
        eegData = eegData.reshape(1,64,-1)
        feature = self.model(eegData)
        feature = feature[0].detach().numpy()
        info, dist = self.find_most_similar(feature)
        # print(dist,self.threshold)
        # print(dist > self.threshold)
        # print(info)
        if dist < self.threshold:
            return 201, "Add user failed.\nHave much similarity with User "+info['name']+"\nDist: "+str(dist)+"\nThreshold: "+str(self.threshold)

        name = name.split(".")[0]
        data = {
            "name": name,
            "feature": feature,
            "extro":extro
        }
        self.feature_library.append(data)
        self.name_library.append(name)

        file = open(self.EEGDB+name+'.pkl','wb' )
        pickle.dump(data,file)
        file.close()
        return 200, "success"

    def rec(self,eegData)->dict:
        # eegData = eegData.transpose(1,0)
        eegData = eegData.reshape(1,64,-1)
        # print('shape: ',eegData.shape)
        feature = self.model(eegData)
        # print(feature)
        feature = feature[0].detach().numpy()
        # print(feature.shape)
        result, dist = self.find_most_similar(feature)
        print("Min Distance: ",dist)
        if dist > self.threshold:
            return {}
        if result['name'] not in self.hit.keys():
            self.hit[result['name']] = 1
        else:
            self.hit[result['name']] += 1
        try:
            if self.userStatus[result['name']] == "Disabled":
                return {}
        except KeyError:
            pass
        
        return result

    def update(self,eegData,name:str):
        eegData = eegData.transpose(1,0)
        eegData = eegData.resize(1,64,-1)
        if name not in self.name_library:
            return 201, "查无此人"
        feature = self.model(eegData)
        feature = feature[0]
        name = name.split(".")[0]
        data = {
            "name": name,
            "feature": feature
        }
        for i in range(len(self.name_library)):
            if self.name_library[i] == name:
                del self.feature_library[i]
                del self.name_library[i]
                break
        self.feature_library.append(data)
        self.name_library.append(name)

        file = open(self.EEGDB+name+'.pkl','wb' )
        pickle.dump(data,file)
        file.close()
        return 200, "success"

    def delete(self,name):
        for i in range(len(self.name_library)):
            if self.name_library[i] == name:
                del self.feature_library[i]
                del self.name_library[i]
                os.remove("EEGDB/"+name+".pkl")
                return 200, "success"
        return 201, "Not Found"

    def reload(self):
        self.feature_library = []
        if not os.path.exists(self.EEGDB):
            os.makedirs(self.EEGDB)
        for root, dirs, files in os.walk(self.EEGDB):
            if files:
                for file in files:
                    # print(root)
                    user_info_file = open(root + file, 'rb')
                    user_info = pickle.load(user_info_file)
                    # print(user_info)
                    self.feature_library.append(user_info)
                    self.name_library.append(user_info['name'])
        print(self.name_library)
    def find_most_similar(self, feature):
        dist_index = list()
        result = dict()
        if len(self.feature_library) == 0:
            return result, 9999
        for feature_existed in self.feature_library:
            dist = distance(feature, feature_existed["feature"])
            dist_index.append(dist)
            # print(sim)

        most_similar_index = np.argmin(dist_index)

        result = self.feature_library[most_similar_index]
        return result, dist_index[most_similar_index]

    def distMap(self,Name:str)->list:
        thePerson = None
        for person in self.feature_library:
            if person['name'] == Name:
                thePerson = person
                break
        if not thePerson:
            return []
        dist_list = []
        dist_list.append({
            'dist':self.threshold,
            'name':'threshold',
            'color':"rgb(%s,%s,%s)" % (255,0,0)
        })
        for feature_existed in self.feature_library:
            person = {}
            dist = distance(thePerson['feature'], feature_existed["feature"])
            name = feature_existed['name']
            randomFactor = random.random()
            person['dist'] = dist
            person['name'] = name
            person['rd'] = randomFactor
            person['color'] = "rgb(%s,%s,%s)" % (int(randomFactor*255),int((math.sin(dist)+1)*255),int((math.cos(time.time())+1)*255))
            dist_list.append(person)
        return dist_list