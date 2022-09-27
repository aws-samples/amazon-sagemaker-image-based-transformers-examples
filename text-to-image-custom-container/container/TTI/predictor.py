from flask import Flask
import flask
import os
import json
import logging

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
import io
import uuid
import boto3

#the model is packaged directly into the container, and is found in this directory just like when we ran locally.
local_model_dir = "./stable-diffusion-v1-4"

#Replace this bucket and folder name with your own location for the images to be delivered to.
BUCKET_NAME = "justin-prototypes"
FOLDER = "botvango/"

#Load model from our local weights
pipe = StableDiffusionPipeline.from_pretrained(local_model_dir)
#move the vectors to the GPU, if avaliable.
if torch.cuda.is_available():
    pipe = pipe.to("cuda")

# The flask app for serving predictions
app = Flask(__name__)
@app.route('/ping', methods=['GET'])
def ping():
    # Check if the classifier was loaded correctly
    # Sagemaker will ping this regularly to check that the endpoint is healthy.
    health = pipe is not None# pipe was loaded
    status = 200 if health else 404
    return flask.Response(response= '\n', status=status, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    
    # Grab the prompt from the HTTP request
    input_json = flask.request.get_json()
    
    #Grab the prompt from the input_json, if any.
    if "prompt" in input_json:
        prompt = input_json['prompt']
    else:
        prompt = ""
    print ("New request:"+prompt)
    
    #Grab the hyperparmeters from the input_json, if any.
    if "guidance_scale" in input_json:
        guidance_scale = input_json['guidance_scale']
    else:
        guidance_scale = 7.5
        
    if "num_inference_steps" in input_json:
        num_inference_steps = input_json['num_inference_steps']
    else:
        num_inference_steps = 50
        
    if "height" in input_json:
        height = input_json['height']
    else:
        height = 512
        
    if "width" in input_json:
        width = input_json['width']
    else:
        width = 512
    
    #create a random name to use for the image to be generated.
    image_name = uuid.uuid4().hex + ".png"
    
    try:
        #Compute image from prompt
        with autocast("cuda"):
            image = pipe(prompt, guidance_scale=guidance_scale,num_inference_steps=num_inference_steps,height=height,width=width)["sample"][0]    

        #save the image to S3
        client_s3 = boto3.client('s3')
        #First, save the image to an in-memory file
        in_mem_file = io.BytesIO()
        image.save(in_mem_file, format="png")
        in_mem_file.seek(0)
        #Then, upload the in-memory file to S3
        client_s3.upload_fileobj(
            in_mem_file,
            BUCKET_NAME,
            FOLDER+image_name
        )

        #send image S3 location as result
        result = {'s3_loc': image_name}
    except Exception as e:
        #send an error message
        result = {'s3_loc': "error","error":str(e)}
        
    resultjson = json.dumps(result)
    return flask.Response(response=resultjson, status=200, mimetype='application/json')
