import boto3
import re
import csv
import os.path

regions = ['us-east-1', 'us-east-2']
filename = 'ec2_snapshots.csv'
fieldnames_glbl = ['Instance Name', 'Backup', 'Volume Size (GiB)', 'Total (GB)', 'Snapshot Started', 'Snapshot Ended', 'region', 'instance_id', 'Snapshot ID', 'VolumeId', 'PrevVolumeId', 'Changed Size (GB)', 'State']
#PrevVolumeId column is just created/reserved.  This will have to be figured out separately and pushed back into csv file.  It is also mislabled.  It is a snapshot id of the prior snapshot

def get_instance_name(ec2, instance_id):
    try:
        if instance_id != 'N/A':
            response = ec2.describe_instances(InstanceIds=[instance_id])
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            return tag['Value']
        return 'N/A'
    except:
        return 'N/F'
		
def extract_instance_id(description):
    match = re.search(r'i-[a-f0-9]+', description)
    if match:
        return match.group(0)
    return 'N/A'

def get_volume_instanceid(ec2, vol_id):
	try:
		response = ec2.describe_volumes(VolumeIds=[vol_id])
		for volumes in response['Volumes']:
			for attachment in volumes['Attachments']:
				if 'InstanceId' in attachment:
					return attachment['InstanceId']
		return 'N/A'
	except:
		return 'N/F'
		
def get_backup_tag(snap):
	for tag in snap.get('Tags', []):
		if tag['Key'] == 'Backup':
			return tag['Value']
	return 'N/A'

def getFullSize(snapshot_id, region):
    try:
        #print(f"{snapshot_id}: working ...")
        client = boto3.client('ebs', region_name=region)
        num_blocks = 0
        blocksize = 524288
		
        response = client.list_snapshot_blocks(
            SnapshotId=snapshot_id
        )
        blocksize = response['BlockSize']
        num_blocks += len(response['Blocks'])
        #print(f"{snapshot_id}: {blocksize} blocksize")
		
        while 'NextToken' in response:
            response = client.list_snapshot_blocks(
                SnapshotId=snapshot_id,
                NextToken=response['NextToken']
            )
            num_blocks += len(response['Blocks'])

        block_size_kib = blocksize / 1024
        total_size_kib = num_blocks * block_size_kib
        total_size_gb = total_size_kib / (1024 * 1024)
        #print(f"{snapshot_id}: {total_size_gb} GB")
        return total_size_gb
    except:
        return '-1'

def list_changed_blocks(orig_sid, new_sid, region):
    if not orig_sid or not new_sid:
        return -1
		
    try:
        client = boto3.client('ebs', region_name=region)
        num_blocks = 0
        blocksize = 524288
        response = client.list_changed_blocks(
            FirstSnapshotId=orig_sid,
            SecondSnapshotId=new_sid
        )  
        #print(response)
        blocksize = response['BlockSize']
        num_blocks += len(response['ChangedBlocks'])
    
        while 'NextToken' in response:
            response = client.list_changed_blocks(
                FirstSnapshotId=orig_sid,
                SecondSnapshotId=new_sid,
                NextToken=response['NextToken']
            )
            num_blocks += len(response['ChangedBlocks'])

        #print(f"Total size of snapshot {snapshot_id}: {total_size_gb:.2f} GB")
        #print(f"Total blocks counted: {num_blocks} block size {blocksize}")
	
        block_size_kib = blocksize / 1024
        total_size_kib = num_blocks * block_size_kib
        total_size_gb = total_size_kib / (1024 * 1024)
        return total_size_gb
    except:
        return -1

def load_dict():
	if os.path.isfile(filename):
		with open(filename, newline='') as csvfile:
			fieldnames = fieldnames_glbl
			reader = csv.DictReader(csvfile)
			return [row for row in reader]
	return []

def write_dict(data):
	with open(filename, mode='w', newline='') as csv_file:
		fieldnames = fieldnames_glbl
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()

		for line in data:
			#print(f"Writing data for {line['Instance Name']} {line['Backup']} {line['Snapshot ID']} from original csv")
			
			#get full size if needed
			fullSize = line['Total (GB)']
			if fullSize == '-1':
				fullSize = getFullSize(line['Snapshot ID'], line['region'])
			
			#check on state
			state = line['State']
			
			#if prevVol id (snaphot) is known, get changed size
			changedSize = line['Changed Size (GB)']
			if changedSize == '-1' and len(line['PrevVolumeId']) > 5 and state == 'completed':
				changedSize = list_changed_blocks(line['PrevVolumeId'],line['Snapshot ID'], line['region'])
						
			writer.writerow({
				'instance_id': line['instance_id'],
				'Instance Name': line['Instance Name'],
				'Snapshot ID': line['Snapshot ID'],
				'VolumeId': line['VolumeId'],
				'Volume Size (GiB)': line['Volume Size (GiB)'],
				'Total (GB)': fullSize,
				'Snapshot Started': line['Snapshot Started'],
				'Snapshot Ended': line['Snapshot Ended'],
				'Backup': line['Backup'],
				'region': line['region'],
				'PrevVolumeId': line['PrevVolumeId'],
				'Changed Size (GB)': changedSize,
				'State': state
			})
			
def is_snap_in_dict(snapshot_id, d_reader):
	for row in d_reader:
		if snapshot_id in row.values():
			return True
	return False

def export_snapshots_info_to_csv():
	cur_data = load_dict()
	write_dict(cur_data)
	
	for region in regions:
		ec2 = boto3.client('ec2', region_name=region)		
		snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

		with open(filename, mode='a', newline='') as csv_file:
			fieldnames = fieldnames_glbl
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)			

			for snapshot in snapshots:
				snapshot_id = snapshot['SnapshotId']
				backup_tag = get_backup_tag(snapshot)
				if backup_tag != 'N/A' and not is_snap_in_dict(snapshot_id, cur_data):
					volId = snapshot['VolumeId']
					desc = snapshot['Description']
					
					instance_id = extract_instance_id(desc)
					if instance_id[:2] == 'N/':
						instance_id = instance_id + 'XX'
						instance_id = get_volume_instanceid(ec2, volId)
					
					instance_name = get_instance_name(ec2, instance_id)					
					
					print(f"Writing data for {instance_name} {backup_tag} {snapshot_id} from API")
					
					volume_size = snapshot['VolumeSize']					
					snapshot_date = snapshot['StartTime'].strftime("%Y-%m-%d %H:%M:%S")
					
					cmpltTm = ''
					full_backup_size = -1;
					if snapshot['State'] == 'completed':
						full_backup_size = getFullSize(snapshot_id, region)
						cmpltTm = snapshot['CompletionTime'].strftime("%Y-%m-%d %H:%M:%S")

					writer.writerow({
						'instance_id': instance_id,
						'Instance Name': instance_name,
						'Snapshot ID': snapshot_id,
						'VolumeId': volId,
						'Volume Size (GiB)': volume_size,
						'Total (GB)': full_backup_size,
						'Snapshot Started': snapshot_date,
						'Snapshot Ended': cmpltTm,
						'Backup': backup_tag,
						'region': region, 
						'Changed Size (GB)': -1,
						'State': snapshot['State']
					})

	print(f"Snapshot information has been written to {filename}.")
	
export_snapshots_info_to_csv()