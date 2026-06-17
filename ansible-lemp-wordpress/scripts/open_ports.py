import requests
import subprocess
import json

def get_metadata(path):
    token_url = "http://169.254.169.254/latest/api/token"
    token_headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
    token = requests.put(token_url, headers=token_headers).text
    
    metadata_url = f"http://169.254.169.254/latest/meta-data/{path}"
    metadata_headers = {"X-aws-ec2-metadata-token": token}
    return requests.get(metadata_url, headers=metadata_headers).text

try:
    instance_id = get_metadata("instance-id")
    region = get_metadata("placement/region")
    
    # Get Security Group ID
    cmd = ["aws", "ec2", "describe-instances", "--instance-ids", instance_id, "--region", region]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error describing instances: {result.stderr}")
        exit(1)
        
    data = json.loads(result.stdout)
    sg_id = data['Reservations'][0]['Instances'][0]['SecurityGroups'][0]['GroupId']
    print(f"Detected Security Group ID: {sg_id}")
    
    # Authorize port 80
    cmd80 = ["aws", "ec2", "authorize-security-group-ingress", "--group-id", sg_id, "--protocol", "tcp", "--port", "80", "--cidr", "0.0.0.0/0", "--region", region]
    res80 = subprocess.run(cmd80, capture_output=True, text=True)
    if res80.returncode == 0:
        print("Successfully opened port 80")
    else:
        print(f"Failed to open port 80: {res80.stderr}")
        
    # Authorize port 443
    cmd443 = ["aws", "ec2", "authorize-security-group-ingress", "--group-id", sg_id, "--protocol", "tcp", "--port", "443", "--cidr", "0.0.0.0/0", "--region", region]
    res443 = subprocess.run(cmd443, capture_output=True, text=True)
    if res443.returncode == 0:
        print("Successfully opened port 443")
    else:
        print(f"Failed to open port 443: {res443.stderr}")

except Exception as e:
    print(f"An error occurred: {e}")
