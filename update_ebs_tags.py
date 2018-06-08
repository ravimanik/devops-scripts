"""

Script to update tags of EBS Volumes from the instances which they are attached to

"""

import boto3
import json
import ConfigParser
from datetime import datetime
import os
import time

class ElasticInstance(object):

    def __init__(self):
        HOME_PATH = os.getenv("HOME")
        AWS_CONF = os.path.join(HOME_PATH, ".aws", "config")
        self.config = ConfigParser.RawConfigParser(allow_no_value=True)
        self.config.read(AWS_CONF)
        print "Select a profile : \n{profiles}\n".format(
        profiles="\n".join(ele.strip("profile ") for ele in self.config.sections()))
        self.selected_profile = raw_input("Enter the project name from above : ")
        self.service = "ec2"
        session = boto3.Session()
        regions = session.get_available_regions(self.service)
        self.records = []
        for region_name in regions:
            self.region_name = region_name
            self.update_tag()


    def get_tags(self,instance_id):
        """
        :param instance_id:
        :return tags: list of tags
        """
        instance = self.ec2.Instance(id=instance_id)
        tag = instance.tags

        return tag
        

    def update_tag(self):
        session = boto3.Session(profile_name=self.selected_profile,region_name=self.region_name)
        self.ec2 = session.resource(self.service)
        volumes = self.ec2.volumes.filter()
        for volume in volumes:
            if len(volume.attachments) = 1:

                ins_id = volume.attachments[0]['InstanceId']
                tags = self.get_tags(ins_id)
                # print tags
                tags.append({'Key':'AttachedTo', 'Value': ins_id})
                for index,ele in enumerate(tags):
                    # print ele
                    if 'aws:' in ele['Key']:
                        tags.pop(index)
                tag = volume.create_tags(
                    DryRun=False,
                    Tags=tags
                )
                print "Volume {vol_id} tagged as {tag}".format(vol_id=volume.id,tag=tag)



if __name__ == "__main__":
    sg_obj = ElasticInstance()





