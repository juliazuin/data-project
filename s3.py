import boto3

# Initialize S3 client
s3 = boto3.client('s3')

# Upload file
s3.upload_file('local_file.txt', 'your-bucket-name', 's3_object_key.txt')