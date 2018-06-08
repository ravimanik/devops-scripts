''' 
Lambda script to update all the autoscaling group's launch config with the latest AMI ID of any of the running machine in the Auto Scaling Group.
Useful in case of intra day deployment or any config change which needs to be reflected in all auto launched instances.
'''

import boto3
import collections
import datetime
import time
import base64

#Global objects 
ec = boto3.resource('ec2', 'ap-south-1')
# Mention you aws owner id
OWNER_ID = ["YOUR_OWNER_IDS",]
images = ec.images.filter(Owners=["YOUR_OWNER_ID"])
autoscale = boto3.client('autoscaling', 'ap-south-1')
ec2 = boto3.client('ec2', 'ap-south-1')
today = datetime.datetime.now()



def lambda_handler(event, context):
    
    asg_names_array = event['asg_names']

    print "Recieved array", asg_names_array

    for ASG_NAME in asg_names_array:
        try:
            autoscale_group = autoscale.describe_auto_scaling_groups(
                            AutoScalingGroupNames= [
                                ASG_NAME 
                                ]
                    )
            new_ami_id = []
            try: 
                #Get the instance id and create an ami
                for autoscale_instance in autoscale_group['AutoScalingGroups'][0]['Instances']:
                    if (autoscale_instance['HealthStatus'] == 'Healthy' and autoscale_instance['LifecycleState'] == 'InService'):
                        print ("Healthy Instance is: %s" %autoscale_instance['InstanceId'])
                        print ("Creating AMI for the instance: %s" %autoscale_instance['InstanceId'])
                        ami_today = today - datetime.timedelta(days=0)
                        ami_date  = ami_today.strftime('%d-%m-%Y-%H-%M')
                        AMIid = ec2.create_image(InstanceId=autoscale_instance['InstanceId'], Name=ASG_NAME+"-"+ami_date, Description="Lambda created AMI for ASG " + ASG_NAME, NoReboot=True, DryRun=False)
                        new_ami_id.append(AMIid['ImageId'])
                        break
                new_ami_id = new_ami_id[0]
              
                autoscale_lc_name = asg['LaunchConfigurationName']
                print ("The Autoscaling group is: %s" % ASG_NAME) 
                print ("The current LC being used in autoscaling is: %s" %autoscale_lc_name)
                        
                lc_config = autoscale.describe_launch_configurations(
                        LaunchConfigurationNames=[
                                 autoscale_lc_name],
                    )
                
                #Save the current lc details to variables
                print ("\nThe configurations to create new LC are below......")
                key_pair    = [lck['KeyName'] for lck in lc_config['LaunchConfigurations'] if 'KeyName' in lck][0]
                print ("Current LC key-pair: %s" % key_pair) 
                instance_type = [lcit['InstanceType'] for lcit in lc_config['LaunchConfigurations'] if 'InstanceType' in lcit][0]
                print ("Current LC instance type: %s" % instance_type)
                space_old_launch_config_name = [lcn['LaunchConfigurationName'] for lcn in lc_config['LaunchConfigurations'] if 'LaunchConfigurationName' in lcn][0]
                old_launch_config_name = space_old_launch_config_name.replace(" ", "") # Without white spaces
                print ("Current launch config name: %s" % old_launch_config_name)
                security_group_id = [lcsgi['SecurityGroups'][0] for lcsgi in lc_config['LaunchConfigurations'] if 'SecurityGroups' in lcsgi][0]
                print ("Current LC Security Group Id: %s" %security_group_id)
                old_ami_id = [lcami['ImageId'] for lcami in lc_config['LaunchConfigurations'] if 'ImageId' in lcami][0]
                print ("Current LC ami id: %s" %old_ami_id)
            
                print ("New AMI Id to be updated: %s" %new_ami_id)
                iam_instance_profile = [iamprofile['IamInstanceProfile'] for iamprofile in lc_config['LaunchConfigurations'] if 'IamInstanceProfile' in iamprofile]
                if iam_instance_profile:
                    print ("Current IamInstanceProfile : %s" %iam_instance_profile[0])
                    iam_instance_profile = iam_instance_profile[0]
                else:
                    iam_instance_profile = None
                    print ("No IamInstanceProfile associated.")
                user_data = [lcud['UserData'] for lcud in lc_config['LaunchConfigurations'] if 'UserData' in lcud][0]
                decoded_user_data =  base64.b64decode(user_data)
                print ("-------------------------------------------------------------------------------------------------")
                print ("Current LC encoded User data:\n %s" % user_data)
                print ("\nCurrent LC decoded data is:\n %s" % decoded_user_data)
                print ("-------------------------------------------------------------------------------------------------")
                
                    
                #To extract todays date to append with the new launch configuration name    
                todays = today - datetime.timedelta(days=0)
                today_date = todays.strftime('%d-%m-%Y-%H-%M')
            
                #space_new_launch_config_name = old_launch_config_name.replace(str(days_old_date), str(today_date))
                new_launch_config_name = ASG_NAME.replace(" ", "")+'-'+today_date+'-LC' # Without white spaces
                print ("\nThe new launch configuration name is: %s" %new_launch_config_name)
                
                try:
                    if iam_instance_profile:
                        create_launch_config = autoscale.create_launch_configuration(
                                LaunchConfigurationName=new_launch_config_name,
                                ImageId=new_ami_id,
                                KeyName=key_pair,
                                SecurityGroups=[
                                security_group_id,
                                ],
                                InstanceType=instance_type,
                                AssociatePublicIpAddress=True,
                                UserData =decoded_user_data,
                                IamInstanceProfile=iam_instance_profile
                            )
                    else:
                        create_launch_config = autoscale.create_launch_configuration(
                            LaunchConfigurationName=new_launch_config_name,
                            ImageId=new_ami_id,
                            KeyName=key_pair,
                            SecurityGroups=[
                            security_group_id,
                            ],
                            InstanceType=instance_type,
                            AssociatePublicIpAddress=True,
                            UserData =decoded_user_data
                        )    
                    print ("The new LC being successfully created is %s" % new_launch_config_name)
                except Exception as e:
                        print "Failed to create new LC. %s" % e.message
                    
                try:
                    update_autoscale_group = autoscale.update_auto_scaling_group(
                        AutoScalingGroupName=ASG_NAME,
                            LaunchConfigurationName=new_launch_config_name,
                        )
                    print ("The LC being successfully updated with %s" % ASG_NAME)
                        
                except Exception as e:
                    print "Failed to update ASG with new LC. %s" % e.message
                    
                    
                try:
                    delete_launch_config = autoscale.delete_launch_configuration(
                           LaunchConfigurationName=old_launch_config_name
                        )
                
                except Exception as e:
                    print "%s" % e.message
            
                snapshotList = []
                desc_image_snapshots = ec2.describe_images(ImageIds=[old_ami_id],Owners=OWNER_ID)['Images'][0]['BlockDeviceMappings']
                try:
                    for desc_image_snapshot in desc_image_snapshots:
                        snapshot = ec2.describe_snapshots(SnapshotIds=[desc_image_snapshot['Ebs']['SnapshotId'],], OwnerIds=OWNER_ID)['Snapshots'][0]
                        snapshotList.append(snapshot['SnapshotId'])
                    
                except Exception as e:
                    print "Ignore Index Error:%s" % e.message

                print "Deregistering image %s" % old_ami_id
                try:
                    amiResponse = ec2.deregister_image(
                    DryRun=False,
                    ImageId=old_ami_id,
                )    
                    print "The timer is started for 5 seconds to wait for images to deregister before deleting the snapshots associated to it"    
                    time.sleep(5)
                    # This should be set to higher value if the image in the imagesList takes more time to deregister
                    for snapshot in snapshotList:
                        try:
                            snap = ec2.delete_snapshot(SnapshotId=snapshot)
                            print "Deleted snapshot " + snapshot
            
                        except Exception as e:
                            print "%s" % e.message
                    print "-------------"
                except Exception as e:
                    print "%s" % e.message
                
            except Exception as e:
                print "No instances in asg are healthy, ignore. %s" %e.message
        
        except Exception as e:
            print "Whoppps, something went wrong. %s" %e.message
       

def trunc_at(s, d, n=3):
    "Returns s truncated at the n'th (3rd by default) occurrence of the delimiter, d."
    return d.join(s.split(d)[:n])
