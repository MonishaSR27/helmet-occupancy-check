# helmet-occupancy-check in AWS
<br>
This project uses Amazon Rekognition to analyze images of vehicles uploaded to an Amazon S3 bucket.It detects the number of people and whether they are wearing helmets, and then stores rule violation information in Amazon DynamoDb using AWS Lambda.
<br>
##TECH STACK
<br>
-AWS Lambda
<br>
-Amazon Rekognition
<br>
-Amazon DynamoDB
<br>
-CloudWatch(for logs)
