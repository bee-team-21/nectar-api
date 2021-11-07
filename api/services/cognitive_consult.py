from typing import List
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
import sys
import time
import requests
from api.models.analysis_result import DetectedObjects, Tag,Captions,Risk,AnalysisResult

from api.configuration import COGNITIVE_KEY, COGNITIVE_URL
from api.services.token_service import get
from googletrans import Translator, constants


KEY = COGNITIVE_KEY
ENDPOINT = COGNITIVE_URL
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def send_taxonomy(name:str):
    to_send = name.split(' ')
    for name in to_send:
        dafult_words = ['animal','bird','mamal']
        if name in dafult_words:
            return  True
        url = "https://rest.ensembl.org/taxonomy/classification/{}".format(name)
        
        headers = {'Content-type': 'application/json'}
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            return True
    return False

    

def check_animal(object:dict):
    
    dafult_words = ['animal','bird','mamal']
    if object.object_property in dafult_words:
        return  True
    elif send_taxonomy(object.object_property):
        return True
    
    elif object.parent:
        level_1 = object.parent
        if level_1.object_property in dafult_words:
            return  True
        if send_taxonomy(level_1.object_property):
            return  True
        elif level_1.parent:
            level_2 = level_1.parent
            if level_2.object_property in dafult_words:
                return  True
            if send_taxonomy(level_2.object_property):
                return True
    
    return  False

        



def check_cage(name: str):
    dafult_words = ['cage', 'crate', 'enclosure', 'jail', 'pen',
                    'coop', 'corral', 'fold', 'mew', 'pinfold', 'pound']
    if name in dafult_words:
        return True
    
    return False

def get_tags(url:str):
    tag_list = []
    tags_result_remote = computervision_client.tag_image(url)
    if (len(tags_result_remote.tags) == 0):
        return tag_list
    else:
        
        for tag in tags_result_remote.tags:
            flg_cage = check_cage(tag.name)
            flg_animal = send_taxonomy(tag.name)
            t = Tag(name=tag.name,score=tag.confidence, flg_cage=flg_cage, flg_animal=flg_animal)
            tag_list.append(t)
    return tag_list

def get_detect_objects(url:str):
    object_list = []
    detect_objects_results_remote = computervision_client.detect_objects(url)
    if len(detect_objects_results_remote.objects) == 0:
        t = DetectedObjects(name='empty',confidence=0.5,flg_animal=False)
        object_list.append(t)
    else:
        for object in detect_objects_results_remote.objects:
            name  = object.object_property
            confidence = object.confidence 
            flg_animal = check_animal(object)
            
            t = DetectedObjects(name=name,confidence=confidence,flg_animal=flg_animal)
            object_list.append(t)
    return object_list

def get_captions(url:str):
    caption_list= []
    description_results = computervision_client.describe_image(url)
    if (len(description_results.captions) == 0):
        c = Captions(text= 'Not able to describe', confidence=0.5)
        caption_list.append(c)
    else:
        for caption in description_results.captions:
            #print(caption.text)
            c = Captions(text= caption.text, confidence=caption.confidence)
            caption_list.append(c)
    return caption_list

def get_risk(tags:List[Tag], detected_objects:List[DetectedObjects],captions:List[Captions]):
    risk_list= []
    count_animals=0
    count_cage = 0
    for tag in tags:
        if tag.flg_cage:
            count_cage+=1
    for text in captions:
        if 'cage' in text.text and count_cage == 0:
            count_cage+=1
        if 'cages' in text.text and count_cage == 0:
            count_cage+=1
    if len(detected_objects) == 1 and detected_objects[0].name == 'empty':
        for tag in tags:
            if tag.flg_animal:
                count_animals+=1
    else:
        for detected in detected_objects:
            if detected.flg_animal:
                count_animals+=1
    print(count_animals)
    print(count_cage)
    if count_animals >2 and count_cage==1:
        risk = Risk(grade = 'High',confidence='0.95')
        risk_list.append(risk)
    elif count_animals <=2 and count_cage==1:
        risk = Risk(grade = 'High',confidence='0.90')
        risk_list.append(risk)
    elif count_animals ==1 and count_cage==1:
        risk = Risk(grade = 'Mid',confidence='0.60')
        risk_list.append(risk)
    elif count_animals ==1 and count_cage>1:
        risk = Risk(grade = 'Mid',confidence='0.75')
        risk_list.append(risk)
    else: 
        risk = Risk(grade='Low',confidence='0.50')
        risk_list.append(risk)
    return risk_list

def create_message(tags: List[Tag], detected_objects:List[DetectedObjects], captions:List[Captions],risk:List[Risk]):
    text = 'Your analisys is done.'
    for caption in captions:
        text+= 'The image shows {caption}'.format(caption=caption.text)
    count_animal=0
    count_cage = 0
    for tag in tags:
        if tag.flg_cage:
            count_cage+=1
    if 'cage' in text and count_cage == 0:
        count_cage+=1
    if len(detected_objects) == 1 and detected_objects[0].name == 'empty':
        for tag in tags:
            if tag.flg_animal:
                count_animal+=1
    else:
        for detected in detected_objects:
            if detected.flg_animal:
                count_animal+=1
        
    text+='The image contanins {animals} objects identified as animals, {cages} objects identified as cages.'.format(animals=count_animal, cages=count_cage)
    for r in risk:
        text +="The place is {risk} risk with {confidence}% of confidence.".format(risk= r.grade,confidence=r.confidence*100)

    return text

def tranlate_to_es(text:str):
    translator = Translator()
    translation = translator.translate(text, src="en", dest="es")
    text_es = translation.text 
    return  text_es 

def get_analyze(url:str, usr_id:str):
    user_id = usr_id
    image_url=url
    tags = get_tags(url=url)
    detected_objects = get_detect_objects(url=url)
    captions=get_captions(url=url)
    risk=get_risk(tags=tags,detected_objects=detected_objects,captions=captions)
    text_en = create_message(tags,detected_objects,captions,risk)
    text = tranlate_to_es(text_en)
    analysis= AnalysisResult(user_id = user_id, image_url= image_url,tags= tags,detected_objects=detected_objects, captions = captions,risk=risk, text = text, text_en= text_en)
    return analysis




    
    

