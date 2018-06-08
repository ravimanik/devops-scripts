"""
Script to find out the ALB/ELB utilization.
Useful to detect underutilized and unutilized load balancers
"""
import boto3
import datetime
session = boto3.Session(profile_name="YOUR_AWS_CONFIG_PROFILE")
client = session.client("cloudwatch")



# list all ELBs
elb_client = session.client('elb')
elbv2_client = session.client('elbv2')

paginator = elb_client.get_paginator('describe_load_balancers')
response_iterator = paginator.paginate(
    PaginationConfig={
        'MaxItems': 123,
        'PageSize': 123
    }
)




for ele in response_iterator:
	for lb in ele['LoadBalancerDescriptions']:
		
		response = client.get_metric_statistics(
		    Namespace='AWS/ELB',
		    MetricName='RequestCount',
		    Dimensions=[
		        {
		            'Name': 'LoadBalancerName',
		            'Value': lb['LoadBalancerName']
		        },
		    ],
		    StartTime=datetime.datetime.now() - datetime.timedelta(seconds=604800),
		    EndTime=datetime.datetime.now(),
		    Period=600,
		    Statistics=[
		        'Sum'
		    ]
		)
		z = 0
		for j in response['Datapoints']:
			z = z + j.values()[1]
		if z <= 500:
			print lb['LoadBalancerName'],lb['DNSName'],z

paginator = elbv2_client.get_paginator('describe_load_balancers')
response_iterator = paginator.paginate(
    PaginationConfig={
        'MaxItems': 123,
        'PageSize': 123
    }
)

print "ALB"
for ele in response_iterator:
	for lb in ele['LoadBalancers']:
		
		response = client.get_metric_statistics(
		    Namespace='AWS/ApplicationELB',
		    MetricName='RequestCount',
		    Dimensions=[
		        {
		            'Name': 'LoadBalancer',
		            'Value': lb['LoadBalancerArn'].split(":")[-1].replace("loadbalancer/","")
		        },
		    ],
		    StartTime=datetime.datetime.now() - datetime.timedelta(seconds=604800),
		    EndTime=datetime.datetime.now(),
		    Period=600,
		    Statistics=[
		        'Sum'
		    ]
		)
		z = 0
		for j in response['Datapoints']:
			z = z + j.values()[1]
		if z <= 500:
			print lb['LoadBalancerName'],lb['DNSName'],z




