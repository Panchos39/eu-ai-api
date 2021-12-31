import numpy as np
import pandas as pd
import json
import re
import os
import sklearn
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.impute import SimpleImputer
from datetime import timezone, datetime
import time
from time import strftime, gmtime
from pprint import pprint
import io
#from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
#from sklearn.model_selection import train_test_split
#from tqdm.notebook import tqdm
#import matplotlib.pyplot as plt
#%matplotlib inline


def unixtime_from_vr(string, copy=False) :
    if copy :
        name = string.split('(')[0]
        ext = string.split(')')[1]
        string = name + ext
    base = string.split('.')[0]
    time = base.split('_')
    #dt = datetime(int(time[0]), int(time[1]), int(time[2]))
    dt = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    return int(timestamp) - 3600
    

def unixtime_from_bio(string, copy=False) :
    if copy :
        name = string.split('(')[0]
        ext = string.split(')')[1]
        string = name + ext
    base = '.'.join(string.split('.')[:-1])
    #print(base)
    tmp = string.split('-')
    year = 2020
    month = tmp[1]
    tmp1 = tmp[2].split('_')
    day = tmp1[0]
    tmp2 = tmp1[1].split('.')
    hour = tmp2[0]
    minutes = tmp2[1]
    secs = tmp2[2]
    dt = datetime(int(year), int(month), int(day), int(hour), int(minutes), int(secs))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    return int(timestamp)

def clock2seconds(clock) :
    pt = datetime.strptime(clock,'%H:%M:%S')
    total_seconds = pt.second + pt.minute*60 + pt.hour*3600
    return total_seconds

def seconds2clock(seconds) :
    return strftime('%H:%M:%S', gmtime(seconds))


competence_map = ["Self-confidence", "Self-control", "Openness to change", "Responsibility", "Communicability"]

def get_vr_evals(file, from_memory=False, init_time=None):
    
    competences = {
        "Self-confidence" : 
        {
            'scenarios' : []
        },

        "Self-control" : 
        {
            'scenarios' : []
        },
        "Openness to change" : 
        {
            'scenarios' : []
        },
        "Responsibility" : 
        {
            'scenarios' : []
        },
        "Communicability" : 
        {
            'scenarios' : []
        },
    }
    
    if not from_memory :
        file1 = open(file, 'r') 
        Lines = file1.readlines()
    else :
        file1 = io.StringIO(file)
        Lines = file1.readlines()
    Lines = list(map(lambda x : x.replace('\n', ''), Lines))
    scenario_counter = -1
    scene_counter = -1
    respondent_id = 0
    '''
    if from_memory :
        #print(os.path.basename(init_time))
        unix_time_start = unixtime_from_vr(os.path.basename(init_time))
    else :
        #print(os.path.basename(file))
        unix_time_start = unixtime_from_vr(os.path.basename(file))
    '''
    for line in Lines :
        line = line.replace('\r', '')
        if 'Respondent' in line :
            respondent_id =  line.split(':')[-1].strip(' ')
        if 'Timestamp' in line :
            timestamp = line.split(':')[-1].strip(' ')
            unix_time_start = unixtime_from_vr(timestamp + '.csv')
        if 'Scenario' in line :
            if 'Scenario ID' in line :
                scenario_counter += 1
                scene_counter = -1
                for key in list(competences.keys()) :
                    competences[key]['scenarios'].append({'scenes' : []})
            if (('Scenario Start' in line) or ('Scenario End' in line)) :
                time = ':'.join(line.split(':')[1:]).strip(' ')
                suffix = 'start' if 'Start' in line else 'end'
                for key in list(competences.keys()) :
                    competences[key]['scenarios'][scenario_counter]['scenario_time_' + suffix] = time
                    competences[key]['scenarios'][scenario_counter]['scenario_time_unix_' + suffix] = \
                                                                                unix_time_start + clock2seconds(time)
        if 'Scene' in line :
            if line.split(':')[-1].strip(' ') == '' :
                continue
            if line.split(':')[0].strip(' ') == 'Scene' :
                scene_counter += 1
                scene_id = '.'.join(line.split(':')[-1].strip(' ').split('.')[:-1])
                #print(scene_id)
                for key in list(competences.keys()) :
                    competences[key]['scenarios'][scenario_counter]['scenes'].append({'id' : scene_id, 'vr_evals' : []})
            if (('SceneStart' in line) or ('SceneEnd' in line)):
                time = ':'.join(line.split(':')[1:]).strip(' ')
                suffix = 'start' if 'Start' in line else 'end'
                for key in list(competences.keys()) :
                    competences[key]['scenarios'][scenario_counter]['scenes'][scene_counter]['scene_time_'+suffix] = \
                                                                                                                time
                    competences[key]['scenarios'][scenario_counter]['scenes'][scene_counter]['scene_time_unix_'+suffix] = \
                                                                                unix_time_start + clock2seconds(time)

        if re.match(r'.*\..', line.split(':')[0].strip(' ')) and len(line.split(':')[0].strip(' ')) == 3 :
            #print(line)
            key = competence_map[int(line.split(':')[0].strip(' ').split('.')[0]) - 1]
            value = int(line.split(':')[1].strip(' '))
            competences[key]['scenarios'][scenario_counter]['scenes'][scene_counter]['vr_evals'].append(value)
        #else :
            #print(line)
        
    return competences
                

def is_overlapping(x1,x2,y1,y2):
    return max(x1,y1) <= min(x2,y2)



def get_intermediate_biometry(start, end, biometry) :
    length = len(biometry['timestamps'])
    
    evals = []
    for idx in range(length) :
        left = biometry['timestamps'][idx]
        if idx == length - 1 :
            right = left + 60
        else :
            right = biometry['timestamps'][idx + 1]
        
        if ((left in range(start, end)) and (right in range(start, end))) :
            evals.append(biometry['Pulse'][0][idx])
        elif ((left in range(start, end)) and not (right in range(start, end))) :
            if idx == length - 1 :
                evals.append(biometry['Pulse'][0][idx])
            else :
                evals.append((biometry['Pulse'][0][idx] + biometry['Pulse'][0][idx + 1]) / 2)
        elif is_overlapping(start, end, left, right) :
            evals.append(biometry['Pulse'][0][idx])
        elif (not (left in range(start, end)) and not (right in range(start, end))) :
            #print(start, end, left, right)
            continue
        
    return evals


def get_biometry_evals(file, from_memory=False, init_time=None) :
    if from_memory :
        biometry = file
    else :
        with open(file, 'r') as fi :
            biometry = json.load(fi)
    if from_memory :
        unix_time_start = unixtime_from_bio(os.path.basename(init_time))
    else :
        unix_time_start = unixtime_from_bio(os.path.basename(file))
    biometry['timestamps'] = list(map(lambda x : x * 60 + unix_time_start, biometry['Minutes'][0]))
    return biometry


def get_fusion_evals(vr_file, bio_file, from_memory=False, init_vr_time=None, init_bio_time=None) :
    
    competences = get_vr_evals(vr_file, from_memory, init_vr_time)
    #print(competences)
    biometry = get_biometry_evals(bio_file, from_memory, init_bio_time)
    #print(biometry)
    for key in list(competences.keys()) :
        for scenario_idx in range(len(competences[key]['scenarios'])) :
            for scene_idx in range(len(competences[key]['scenarios'][scenario_idx]['scenes'])) :
                if len(competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['vr_evals']) > 0 :
                    time_start = competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['scene_time_unix_start']
                    time_end = competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['scene_time_unix_end']
                    bio_evals = get_intermediate_biometry(time_start, time_end, biometry)
                    #print(bio_evals)
                    competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['bio_evals'] = bio_evals
    return competences


def gen_template(template, suffixes) :
    extended_template = []
    for scene in template :
        for suffix in suffixes :
            if suffix == '' :
                extended_template.append(scene)
            else :
                extended_template.append(scene + '_' + suffix)
    return extended_template


def respondents_to_df(respondents, template, only_vr=False) :
    evals = [{ key : dict.fromkeys(template) for key in respondents[0].keys()} for i in range(len(respondents))] 
    reduntant = []
    for idx, respondent in enumerate(respondents) :
        competences = respondent
        for key in list(competences.keys()) :
            for scenario_idx in range(len(competences[key]['scenarios'])) :
                cur_scenario_id = str(scenario_idx)
                for scene_idx in range(len(competences[key]['scenarios'][scenario_idx]['scenes'])) :
                    #print(competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx])
                    if len(competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['vr_evals']) > 0 :
                        cur_scene_id = competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['id'] 
                        vr_value = np.mean(competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['vr_evals'])
                        if not only_vr :
                            if len(competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['bio_evals']) == 0 :
                                bio_value = np.nan
                            else :
                                bio_value = np.mean(competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['bio_evals'])
                            time_start = competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['scene_time_unix_start']
                            time_end = competences[key]['scenarios'][scenario_idx]['scenes'][scene_idx]['scene_time_unix_end']
                            time_diff = time_end - time_start
                        #evals[idx][key][cur_scenario_id + '_' + cur_scene_id] = vr_value
                        if (cur_scenario_id + '_' + cur_scene_id + '_vr') in list(evals[idx][key].keys()) :
                            if only_vr :
                                evals[idx][key][cur_scenario_id + '_' + cur_scene_id + '_vr'] = vr_value
                            else :
                                evals[idx][key][cur_scenario_id + '_' + cur_scene_id + '_vr'] = vr_value
                                evals[idx][key][cur_scenario_id + '_' + cur_scene_id + '_bio'] = bio_value
                                evals[idx][key][cur_scenario_id + '_' + cur_scene_id + '_time'] = time_diff
                        else :
                            reduntant.append(cur_scenario_id + '_' + cur_scene_id + '_vr')
    #print(list(set(reduntant)))
    return evals
        
