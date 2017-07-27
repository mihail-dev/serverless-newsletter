from troposphere import Template, Join, Ref
from troposphere.s3 import Bucket, PublicRead, WebsiteConfiguration
from troposphere.dynamodb import Table, KeySchema, AttributeDefinition, ProvisionedThroughput, StreamSpecification
from troposphere.awslambda import Environment
from troposphere.serverless import Function, ApiEvent

class Stack(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.template.add_transform("AWS::Serverless-2016-10-31")
        self.sceptre_user_data = sceptre_user_data
        self.add_s3()
        self.add_dynamo_db()
        self.add_to_ddb_lambda()

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

    def add_dynamo_db(self):
        self.dynamo_db = self.template.add_resource(Table(
            "dynamoDBTable",
            AttributeDefinitions=[
                AttributeDefinition(
                    AttributeName=self.sceptre_user_data["HashKeyElementName"],
                    AttributeType=self.sceptre_user_data["HashKeyElementType"]
                )
            ],
            KeySchema=[
                KeySchema(
                    AttributeName=self.sceptre_user_data["HashKeyElementName"],
                    KeyType="HASH"
                )
            ],
            ProvisionedThroughput=ProvisionedThroughput(
                ReadCapacityUnits=self.sceptre_user_data["ReadCapacityUnits"],
                WriteCapacityUnits=self.sceptre_user_data["WriteCapacityUnits"]
            )
        ))

    def add_to_ddb_lambda(self):
        self.add_to_ddb_lambda_function = self.template.add_resource(Function(
        "AddToDDBFunction",
        Code=Code(
            ZipFile=Join("", [
                "import cfnresponse, boto3\n",
                "def add(event, context): \n",
                "  return null",
            ])
        ),
        Handler="index.add",
        Runtime="python3.6",
        Environment=Environment(
            Variables={
                "TABLE_NAME": Ref(self.dynamo_db)
            }
        ),
        Events={
            "AddEntry": ApiEvent(
                "AddEntry",
                Path="/entry/{entryId}",
                Method="put"
            )
        }
    )
)


def sceptre_handler(sceptre_user_data):
    stack = Stack(sceptre_user_data)
    return stack.template.to_json()