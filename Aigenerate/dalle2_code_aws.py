import boto3
import os
import requests
import openai
import pandas as pd
from openai import OpenAI

AWS_Access_Key_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID')
AWS_Secret_Access_Key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')

session = boto3.Session(
    aws_access_key_id=AWS_Access_Key_ID,
    aws_secret_access_key=AWS_Secret_Access_Key,
    region_name='us-west-2'
)

s3 = session.client('s3')

openai.api_key = os.getenv('OPENAI_API_KEY')


def generate_image(input_image_path, image_name):
    # Generate the AI images
    client = OpenAI()
    with open(input_image_path, "rb") as f:
        response = client.images.create_variation(
            image=f,
            n=2,
            size="1024x1024"
        )

    image_url = response.data[0].url  # Correct way to access the data
    print(f"Generated image URL: {image_url}")

    # Download the image from the URL
    image_data = requests.get(image_url).content
    with open(f"fake_{input_image_path}", "wb") as f:
        f.write(image_data)

    s3.upload_file(f"fake_{input_image_path}",
                   "archij", f"fake/{image_name}")

    


def main():

    images_df = pd.read_csv('df_final.csv')
    image_names = list(images_df["Name"])
    # Specify the desired local filename (assuming current directory)
    s3 = boto3.client('s3')



# Download the file
    # image_name='00000.png'
    # s3.download_file('archij', f'real/00000-20240410T100931Z-001/00000/{image_name}', image_name)


    for image_name in image_names:
        s3.download_file('archij', f'real/00000-20240410T100931Z-001/00000/{image_name}', image_name)
        generate_image(image_name, image_name)
        if (os.path.exists(image_name)):
            os.remove(image_name)
        if (os.path.exists(f"fake_{image_name}")):
            os.remove(f"fake_{image_name}")
        images_df = images_df.loc[images_df["Name"] != image_name]
        images_df.to_csv("df_final.csv")


if __name__ == "__main__":
    main()
