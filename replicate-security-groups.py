"""
Script to create and copy security groups from one account/region to another account/region.
"""
import boto3
import json
import ConfigParser
import os
import time
from datetime import datetime
import csv
import botocore


# selected_profile = raw_input("Enter the project name from above : ")
session = boto3.Session(profile_name="SOURCE_PROFILE_NAME",region_name='SOURCE_REGION')
ec2 = session.resource('ec2')
ec2c = session.client('ec2')


session_mum = boto3.Session(profile_name="DESTINATION_PROFILE_NAME",region_name='DESTINATION_REGION')
ec2_dest = session_mum.resource('ec2')
ec2c_dest = session_mum.client('ec2')

# Filter out the security groups based on the VPC ID
sgs = ec2.security_groups.filter(Filters=[
        {
            'Name': 'vpc-id',
            'Values': ['SOURCE_VPC_ID',
            ]
        },
    ]
)

# describe security group and copy ingress rules to new SGS of Destination

sgs = ec2c.describe_security_groups(Filters=[
        {
            'Name': 'vpc-id',
            'Values': ['SOURCE_VPC_ID',
            ]
        },
    ])

# Check for the security group if they don't exist then create the security groups.
for row in sgs:
  if not row.group_name == 'default':
  	# check if group exists, else create one.
  	response = client.describe_security_groups(
  	    GroupNames=[
  	        row.group_name,
  	    ]
  	)
  	if not response['SecurityGroups']:
  		print "Creating security group {group_name}".format(group_name=row.group_name)
	  	response = ec2c_dest.create_security_group(
	        DryRun=False,
	        GroupName=row.group_name,
	        Description=row.description,
	        VpcId='DEST_VPC_ID')
	  	print response

for ele in sgs['SecurityGroups']:
    print "=========="
    print "Applying Chanegs for : ",ele['GroupName'],
    rules = ele['IpPermissions']
    if not ele['GroupName'] == 'default':
        res = ec2_dest.security_groups.filter(Filters=[
                    {
                        'Name': 'group-name',
                        'Values': [ele['GroupName'],
                        ]
                    },
                ]
                )    
        for ele in res:
            target_gid = ele.group_id
            target_vpcid = ele.vpc_id
        print "Updating Rules of Group - {target_gid} , Group Name {group_name} VPC - {target_vpcid}: ".format(target_gid=target_gid,target_vpcid=target_vpcid,group_name=ele.group_name)
        response = ec2c_dest.authorize_security_group_ingress(
            DryRun=False,
            GroupId=target_gid,
            IpPermissions=rules
        )
        print response


