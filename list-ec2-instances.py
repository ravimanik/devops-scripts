"""
    Script to fetch all the instances for running instances across the regions in a project and write it in a CSV file.
    Customise it to fetch additional details like custom tags etc.
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
            # print region_name,type(region_name)
            self.region_name = region_name
            self.main()
        self.write_to_csv(self.records)

    def main(self):
        session = boto3.Session(profile_name=self.selected_profile,region_name=self.region_name)
        self.ec2 = session.resource(self.service)
        # list only running instances
        ec2s = self.ec2.instances.filter(Filters=[{'Name':'instance-state-name','Values':['running']}])
        for ele in ec2s:
            rec = {}
            id = ele.instance_id
            instance_type = ele.instance_type
            az = ele.placement['AvailabilityZone']

            if filter(lambda lst: lst.get('Key') in ("Name","name"), ele.tags):
                instance_name = filter(lambda lst: lst['Key'] in ("Name","name"), ele.tags)[0]['Value']
            else:
                instance_name = 'NoName'
            rec['id']= id
            rec['Type'] = instance_type
            rec['Name'] = instance_name
            rec['Region'] = self.region_name
            rec['AZ'] = az
            rec['ip'] = ele.private_ip_address
            rec['public_ip'] = ele.public_ip_address
            rec['key_name'] = ele.key_name
            rec['launch_time'] = ele.launch_time
            rec['lifecycle'] = ele.instance_lifecycle
            self.records.append(rec)


    def write_to_csv(self,groups):
            print "Strating to write CSV"
            import csv
            fo = open("Running-ec2-{profile}-{today}.csv".format(profile=self.selected_profile,today=datetime.today().strftime("%Y-%m-%d")), "w")
            fieldnames = ["id","Type","Name","Region","AZ",'ip','public_ip','key_name',,'launch_time','lifecycle']
            csv_writer = csv.DictWriter(fo, fieldnames=fieldnames)
            csv_writer.writeheader()
            for ele in groups:
                # print ele
                csv_writer.writerow(ele)

            fo.close()


if __name__ == "__main__":
    sg_obj = ElasticInstance()
    sg_obj.main()




