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
from api.models.analysis_result import Tag,Captions,Risk,AnalysisResult

from api.configuration import COGNITIVE_KEY, COGNITIVE_URL
from api.services.token_service import get
from googletrans import Translator, constants


KEY = COGNITIVE_KEY
ENDPOINT = COGNITIVE_URL
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def check_animal(name:str):
    dafult_words = ['animal','bird']
    if name in dafult_words:
        return True
    url = "https://rest.ensembl.org/taxonomy/classification/{}".format(name)
    headers = {'Content-type': 'application/json'}
    response = requests.request("GET", url, headers=headers)
    
    if response.status_code == 200:
        return True
    return False


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
            flg_animal = check_animal(tag.name)
            flg_cage = check_cage(tag.name)
            t = Tag(name=tag.name,score=tag.confidence,flg_animal=flg_animal, flg_cage=flg_cage)
            tag_list.append(t)
    return tag_list

def get_captions(url:str):
    caption_list= []
    description_results = computervision_client.describe_image(url)
    if (len(description_results.captions) == 0):
        return []
    else:
        for caption in description_results.captions:
            print(caption.text)
            c = Captions(text= caption.text, confidence=caption.confidence)
            caption_list.append(c)
    return caption_list

def get_risk(tags:List[Tag]):
    risk_list= []
    count_animals = 0
    count_cage = 0
    for tag in tags:
        if tag.flg_cage:
            count_cage =+1
        if tag.flg_animal:
            count_animals=+1
    if count_animals >=2 and count_cage>0:
        risk = Risk(grade = 'High',confidence='0.90')
        risk_list.append(risk)
    else: 
        risk = Risk(grade='Low',confidence='0.50')
        risk_list.append(risk)
    return risk_list

def create_message(tags: List[Tag], captions:List[Captions],risk:List[Risk]):
    text = 'Your analisys is done.'
    for caption in captions:
        text+= 'The image shows {caption}'.format(caption=caption.text)
    count_animal=0
    count_cage = 0
    count_other = 0
    for tag in tags:
        if tag.flg_animal:
            count_animal+=1
        if tag.flg_cage:
            count_cage+=1
        if not tag.flg_animal and not tag.flg_cage:
            count_other+=1
    text+='The image contanins {animals} objects identified as animals, {cages} objects identified as cages and {other} other objects.'.format(animals=count_animal, cages=count_cage,other=count_other)
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
    captions=get_captions(url=url)
    print(captions)
    risk=get_risk(tags=tags)
    text_en = create_message(tags,captions,risk)
    text = tranlate_to_es(text_en)

    analysis= AnalysisResult(user_id = user_id, image_url= image_url,tags= tags,captions = captions,risk=risk, text = text, text_en= text_en)
    return analysis




    
    

