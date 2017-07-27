from troposphere import Template
from troposphere.s3 import Bucket, PublicRead, WebsiteConfiguration

class Stack(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.add_s3()

    def add_s3(self):
        self.s3 = self.template.add_resource(Bucket(
            "S3Bucket",
            BucketName=self.sceptre_user_data["bucket_name"],
            AccessControl=PublicRead,
            WebsiteConfiguration=WebsiteConfiguration(
                IndexDocument="index.html",
                ErrorDocument="error.html"
            )
        ))

def sceptre_handler(sceptre_user_data):
    stack = Stack(sceptre_user_data)
    return stack.template.to_json()