import json
import urllib.parse
import boto3
from io import StringIO, BytesIO
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print('Loading function')

s3 = boto3.client('s3')

out_bucket = '################ YOUR BUCKET NAME ################'

def lambda_handler(event, context):
    # get bucket and key of file that caused trigger
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # open data in CSV
        response = s3.get_object(Bucket=bucket, Key=key)
        
        csv_data = response['Body'].read().decode('utf-8')

        # convert data from string to list then list of lists
        dl = csv_data.split("\n")
        dll = [x.replace(' ', '').replace('\r', '').split(',') for x in dl if len(x) > 0]

        # convert list of lists into dataframe
        data_df = pd.DataFrame(dll[1:], columns = dll[0])
        
        # get name and data of first column
        col_name = data_df.columns[0]
        data = data_df[col_name]
        data = np.array(data.to_list(), dtype=np.float64)

        # generate S3 key for resulting plot
        out_key = key.split('/')[-1].split('.')[0] + '.png'
        
        # verify clean plot
        plt.cla()
        plt.clf()

        # plot data
        img_data = BytesIO()
        plt.plot(data, label=col_name)
        plt.legend(loc="upper left")
        
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        
        # put plot in S3 bucket
        bucket = boto3.resource('s3').Bucket(out_bucket)
        bucket.put_object(Body=img_data, ContentType='image/png', Key=out_key)
        
        # generate presigned url
        url = s3.generate_presigned_url('get_object', 
            Params={'Bucket': out_bucket, 'Key': out_key},
            ExpiresIn=86400)
        
        # log url in CloudWatch
        print(url)
        
        return "DONE"
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e
