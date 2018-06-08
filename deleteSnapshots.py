"""
Script to delete old snapshots and deregister any older AMI
"""

import boto3
import sys
from datetime import datetime, timedelta
import pytz


OWNER_ID=['owner_aws_id']
utc=pytz.UTC
session = boto3.Session(profile_name='your_profile')
client = session.client('ec2')
days = 60
delete_time = datetime.utcnow() - timedelta(days=days)
delete_time = utc.localize(delete_time)


def delete_snapshots(ami_id):
	snapshotList = []
	desc_image_snapshots = client.describe_images(ImageIds=[ami_id],Owners=OWNER_ID)['Images'][0]['BlockDeviceMappings']
	try:
	    for desc_image_snapshot in desc_image_snapshots:
	        snapshot = client.describe_snapshots(SnapshotIds=[desc_image_snapshot['Ebs']['SnapshotId'],], OwnerIds=OWNER_ID)['Snapshots'][0]
	        snapshotList.append(snapshot['SnapshotId'])
	    
	except Exception as e:
	    print "Ignore Index Error:%s" % e.message

	print "Deregistering image %s" % ami_id
	try:
	    amiResponse = client.deregister_image(
	    DryRun=False,
	    ImageId=ami_id,
	)    
		print "------------- DREREGISTERING IMAGE ------- ",ami_id
	    print "The timer is started for 5 seconds to wait for images to deregister before deleting the snapshots associated to it"    
	    time.sleep(5)# This should be set to higher value if the image in the imagesList takes more time to deregister
	    for snapshot in snapshotList:
	        try:
	            snap = client.delete_snapshot(SnapshotId=snapshot)
	            print "Deleted snapshot " + snapshot
	
	        except Exception as e:
	            print "%s" % e.message
	    print "-------------"
	except Exception as e:
	    print "%s" % e.message



paginator = client.get_paginator('describe_snapshots')
response_iterator = paginator.paginate(
    OwnerIds=OWNER_ID,
    PaginationConfig={
        'MaxItems': 10000,
        'PageSize': 200,
    }
)
deletion_counter  = 0
total = 0

for ele in response_iterator:
	for snapshot in ele['Snapshots']:
		total += 1
		# print snapshot.get('StartTime')	
		start_time = snapshot.get('StartTime').replace(tzinfo=utc)

		
		count += 1
		if start_time < delete_time:
			print 'Deleting {id}'.format(id=snapshot.id)
			deletion_counter = deletion_counter + 1
			size_counter = size_counter + snapshot.volume_size
			# Don't forget to change the dry run
			snapshot.delete(dry_run=True)
print 'Deleted {count} from {total} snapshots'.format(count=count,total=total)

