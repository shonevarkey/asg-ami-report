import boto3
import datetime
import json
import os
import csv

def get_account_id():
    sts_client = boto3.client('sts')
    response = sts_client.get_caller_identity()
    return response['Account']

def get_instance_details(instance_id):
    
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    
    if 'Reservations' in response and len(response['Reservations']) > 0:
        instance = response['Reservations'][0]['Instances'][0]
        ami_id = instance.get('ImageId', '')
        launch_time = instance.get('LaunchTime', '')
        instance_type = instance.get('InstanceType', '')  
        return ami_id, launch_time, instance_type
    return '', '', ''

def generate_report():
    account_id = get_account_id()
    
    asg_client = boto3.client('autoscaling', region_name='us-east-1')
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    
    paginator = asg_client.get_paginator('describe_auto_scaling_groups')
    asg_iterator = paginator.paginate(MaxRecords=100)
    
    report = []
    
    for asg_page in asg_iterator:
        for asg in asg_page['AutoScalingGroups']:
            asg_name = asg['AutoScalingGroupName']
            desired_capacity = asg['DesiredCapacity']
            min_capacity = asg['MinSize']
            max_capacity = asg['MaxSize']
            
            launch_template_id = None
            ami_id = None
            ami_name = None
            ami_creation_date = None
            platform_details = None
            
            instance_type = asg.get('InstanceType', '') 
            
            if 'LaunchTemplate' in asg:
                launch_template_id = asg['LaunchTemplate']['LaunchTemplateId']
                
                lt_response = ec2_client.describe_launch_templates(LaunchTemplateIds=[launch_template_id])
                if 'LaunchTemplates' in lt_response and len(lt_response['LaunchTemplates']) > 0:
                    launch_template = lt_response['LaunchTemplates'][0]
                    ami_id = launch_template.get('LatestVersion', {}).get('LaunchTemplateData', {}).get('ImageId', '')
            
            if 'Instances' in asg:
                for instance in asg['Instances']:
                    instance_id = instance['InstanceId']
                    ami_id, launch_time, instance_type = get_instance_details(instance_id)
                    
                    if ami_id:
                        ec2_response = ec2_client.describe_images(ImageIds=[ami_id])
                        if 'Images' in ec2_response and len(ec2_response['Images']) > 0:
                            ami = ec2_response['Images'][0]
                            ami_name = ami.get('Name', '')
                            ami_creation_date = ami.get('CreationDate', '')
                            platform_details = ami.get('PlatformDetails', '')
            
            asg_report = {
                'asg_name': asg_name,
                'instance_type': instance_type,
                'desired_capacity': desired_capacity,
                'min_capacity': min_capacity,
                'max_capacity': max_capacity,
                'ami_id': ami_id,
                'launch_template_id': launch_template_id,
                'ami_details': {
                    'ami_name': ami_name,
                    'ami_creation_date': ami_creation_date,
                    'platform_details': platform_details
                }
            }
            
            report.append(asg_report)

    report_directory = os.environ.get('REPORT_DIR', '.')

    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    aws_account_name = os.environ.get('AWS_ACCOUNT', f'UNKNOWN_{current_datetime}')
    json_report_filename = f'{report_directory}/aws_report_{aws_account_name}.json'
    csv_report_filename = f'{report_directory}/aws_report_{aws_account_name}.csv'

    report_with_account = {
        "account_id": account_id,
        "account_name": aws_account_name,
        "asgs": report
    }
    with open(json_report_filename, 'w') as json_report_file:
        json.dump(report_with_account, json_report_file, indent=2)
    
    with open(csv_report_filename, 'w', newline='') as csv_report_file:
        csv_writer = csv.writer(csv_report_file)
        
        csv_writer.writerow(['asg_name', 'instance_type', 'desired_capacity', 'min_capacity', 'max_capacity', 'ami_id', 'launch_template_id', 'ami_name', 'ami_creation_date', 'platform_details'])
        
        for asg_data in report:
            ami_details = asg_data['ami_details']
            csv_writer.writerow([asg_data['asg_name'], asg_data['instance_type'], asg_data['desired_capacity'], asg_data['min_capacity'], asg_data['max_capacity'], asg_data['ami_id'], asg_data['launch_template_id'], ami_details['ami_name'], ami_details['ami_creation_date'], ami_details['platform_details']])
    
    print(f'Report generated and saved as JSON: {json_report_filename}')
    print(f'Report generated and saved as CSV: {csv_report_filename}')

if __name__ == "__main__":
    generate_report()
