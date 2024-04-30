import boto3
import io
from PIL import Image
import openai
import os
import requests

# Set up the S3 client and resource
# Get AWS credentials from environment variables
aws_access_key_id = os.environ.get('AKIASJGWQJV4UVG4VRG5')
aws_secret_access_key = os.environ.get('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')

# Create an S3 client and resource using environment variables
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


# Set up the OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define a function to generate an AI image from an input image
def generate_image(input_image_path):
    # Read the input image from S3
    input_file = s3_resource.Object('s3://aidalle2//input', input_image_path)
    input_image_data = input_file.get()['Body'].read()
    input_image = Image.open(io.BytesIO(input_image_data))

    # Generate the AI image
    response = openai.Image.create_variation(
        image=input_image,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print(f"Generated image URL: {image_url}")

    # Download the image from the URL
    image_data = requests.get(image_url).content

    # Save the image to a file
    output_image_path = f"output/{input_image_path}"
    s3_client.put_object(Body=image_data, Bucket='s3://aidalle2/output', Key=output_image_path)
    print(f"Saved image to s3://aidalle2-output/{output_image_path}")

if __name__ == "__main__":
    # Generate images for all files in the input folder
    for object in s3_client.list_objects(Bucket='aidalle2', Prefix='input')['Contents']:
        input_image_path = object['Key']
        generate_image(input_image_path)