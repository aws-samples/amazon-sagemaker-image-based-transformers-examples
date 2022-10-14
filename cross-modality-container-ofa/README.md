# Text2Image, Visual Grounding, Image Caption, and Visual Question and Answer using OFA
## Based on the [OFA model](https://huggingface.co/OFA-Sys/OFA-large)

From [OFA GitHub](https://github.com/OFA-Sys/OFA):
OFA is a unified sequence-to-sequence pretrained model (support English and Chinese) that unifies modalities (i.e., cross-modality, vision, language) and tasks (finetuning and prompt tuning are supported): image captioning (1st at the MSCOCO Leaderboard), VQA , visual grounding, text-to-image generation, text classification, text generation, image classification, etc. We provide step-by-step instructions for pretraining and fine tuning and corresponding checkpoints (check official ckpt [EN|CN] or huggingface ckpt).

This notebook will walk through the process of deploying the OFA model to an AWS SageMaker endpoint.  We'll start by downloading the model locally to test it out, but note this will only work if you have access to a GPU.  Next, we create a custom docker container which contains the model.  In this use case, we will have the endpoint put the generated images directly in an S3 bucket, and return the location of the image.

Note that this model is large.  You'll want to make sure to use an instance type with at least 15GB of storage in order to have space to download the model and package up the container.  This notebook was tested on a ml.g4dn.4xlarge with 25GB of EBS storage.

The notebook follows these basic steps:
1. Install Dependencies (for local testing)
2. Test the model locally
3. Create a custom inference script
4. Create a unit test file to test inference script
5. Create a custom Docker container for the model and inference script
6. Test the Docker container locally
7. Define and Deploy the model
8. Test the new endpoint
9. Clean up resources

References:
  * [OFA Model on Hugging Face](https://huggingface.co/OFA-Sys/OFA-large)

Container Structure:  This should be the directory structure locally, in order to pack everything correctly into your container. ([reference](https://sagemaker-workshop.com/custom/containers.html))  You will already have this structure if you cloned the git repo, if not, following the directions in this notebook will rebuild this structure and all required files.
- This Notebook
- container
    - OFA
        - predictor.py: Flask app for inference, our custom inference code
        - wsgi.py: Wrapper around predictor
        - nginx.conf: Config for nginx front-end
        - serve: Launches gunicorn server
        - OFA model downloaded from git
        - test_predictor.py: test methods to test predictor
    - Dockerfile
