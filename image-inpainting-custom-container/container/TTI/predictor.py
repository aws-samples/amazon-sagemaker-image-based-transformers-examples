from flask import Flask
import flask
import os
import json
import logging

import torch
from torch import autocast
from diffusers import StableDiffusionImg2ImgPipeline
import io
import uuid
import boto3
from PIL import Image

#the model is packaged directly into the container, and is found in this directory just like when we ran locally.
local_model_dir = "./stable-diffusion-v1-4"

#Replace this bucket and folder name with your own location for the images to be delivered to.
BUCKET_NAME = "justin-prototypes"
FOLDER = "botvango/"

#Load model from our local weights
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(local_model_dir)
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

    #Grab the prompt from the input_json, if any.
    if "img" in input_json:
        img = input_json['img']
    else:
        img = ""
    print ("Image Name:"+img)
    
    #Grab the hyperparmeters from the input_json, if any.
    if "guidance_scale" in input_json:
        guidance_scale = input_json['guidance_scale']
    else:
        guidance_scale = 7.5
        
    if "num_inference_steps" in input_json:
        num_inference_steps = input_json['num_inference_steps']
    else:
        num_inference_steps = 75
        
    if "strength" in input_json:
        strength = input_json['strength']
    else:
        strength = 0.75
        
    #create a random name to use for the image to be generated.
    image_name = uuid.uuid4().hex + ".png"
    
    try:
        #start by pulling our initial image from S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(BUCKET_NAME)
        new_image = bucket.Object(FOLDER+img)
        img_data = new_image.get().get('Body').read()
        init_image = Image.open(io.BytesIO(img_data)).convert("RGB")
        init_image = init_image.resize((512, 512))
        
        #Compute image from prompt
        with autocast("cuda"):
            image = pipe(prompt, init_image=init_image, strength=strength, guidance_scale=guidance_scale,num_inference_steps=num_inference_steps).images[0]

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
