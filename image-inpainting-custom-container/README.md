# Image Inpainting using Stable Diffusion
## Based on the [Stable Diffusion model](https://huggingface.co/CompVis/stable-diffusion-v1-4)


From [Wikipedia](https://en.wikipedia.org/wiki/Stable_Diffusion): "Stable Diffusion is a machine learning, text-to-image model developed by StabilityAI, in collaboration with EleutherAI and LAION, to generate digital images from natural language descriptions. The model can be used for other tasks too, like generating image-to-image translations guided by a text prompt.  Stable Diffusion was trained on a subset of the LAION-Aesthetics V2 dataset. It was trained using 256 Nvidia A100 GPUs at a cost of $600,000."

Inpainting is the process of using a mask to focus Stable Diffusion on a specific part of an image. This allows you to keep parts of an image that you like, while allowing the algorithm to change other parts of the image according to a promt. The mask is an image the same size as the image you want to change. However, the mask is limited to either black or white pixels. Black is used to indicate regions where the subject image should not be changed, and white indicates regions that will be allowed to change.

The notebook in this repo, Image Inpainting Container Build.ipynb, will walk through the process of deploying the Stable Diffusion model to an AWS SageMaker endpoint, using an Inpainting pipeline. We'll start by downloading the model locally to test it out, but note this will only work if you have access to a GPU. Next, we create a custom docker container which contains the model. In this use case, we will have the endpoint pull the starting image and mask from S3, and put the generated images directly in an S3 bucket, then return the location of the image.

### How to make a mask image?
In order to use inpainting, you need to generate a mask. The mask should be an image the same size as the image that you want to process. It should be black where you don't want the image to change, and white wherever you want the inpainting to occur. It is easy to make a mask image in many commertial software applications, but if you want a free, simple mask generator, one is included in this repo. It is a web application, so you need to open a terminal, navigate to the "simple mask app" directory, then run "python3 -m http.server 8000". Finally, open a browser to "http://localhost:8000/mask.html"

While the Stable Diffusion model is free and open source, it does require agreeing to the terms and conditions on Hugging Face.  In order to download this model, you will need to create a free HuggingFace account, and then visit the [stable diffusion model card](https://huggingface.co/CompVis/stable-diffusion-v1-4) and agree to the terms and conditions.  Once that is done, visit your [Hugging Face Access Tokens page](https://huggingface.co/settings/tokens) and create a token for use in this notebook.

The notebook follows these basic steps:
1. Install Dependencies (for local testing)
2. Test the model locally
3. Create a custom inference script
4. Create a custom Docker container for the model and inference script
4. Define and Deploy the model
5. Test the new endpoint

References:
  * [Stable Diffusion Model on Hugging Face](https://huggingface.co/CompVis/stable-diffusion-v1-4)
  * [Custom container packaging code example](https://github.com/RamVegiraju/SageMaker-Deployment/tree/master/RealTime/BYOC/PreTrained-Examples/SpacyNER)

[Container Structure](https://sagemaker-workshop.com/custom/containers.html)
- TTI
    - predictor.py: Flask app for inference, our custom inference code
    - wsgi.py: Wrapper around predictor
    - nginx.conf: Config for nginx front-end
    - serve: Launches gunicorn server
- Dockerfile
