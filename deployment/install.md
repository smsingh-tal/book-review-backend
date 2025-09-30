# AWS Deployment Instructions

This guide provides step-by-step instructions for deploying the Book Review application on AWS using Terraform.

## Prerequisites

1. AWS CLI installed and configured with your credentials
2. Terraform installed on your local machine
3. An AWS account with free tier eligibility
4. An SSH key pair created in your AWS account

### Installing Prerequisites

#### On macOS:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install AWS CLI
brew install awscli

# Install Terraform
brew install terraform
```

#### On Ubuntu/Debian:
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt update
sudo apt install -y unzip
unzip awscliv2.zip
sudo ./aws/install

# Install Terraform
sudo apt update
sudo apt install -y software-properties-common gnupg
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install terraform
```

### Configure AWS CLI

After installing the AWS CLI, configure it with your AWS credentials:

```bash
aws configure
```

You'll need to provide:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### Create AWS Key Pair

Create an SSH key pair in your AWS account:

```bash
# Replace 'your-key-pair-name' with your desired name
aws ec2 create-key-pair --key-name your-key-pair-name --query 'KeyMaterial' --output text > ~/.ssh/your-key-pair-name.pem

# Set correct permissions for the key file
chmod 400 ~/.ssh/your-key-pair-name.pem
```

## Setup Steps

### 1. Initialize Terraform

```bash
cd deployment
terraform init
```

### 2. Create a terraform.tfvars file

Create a file named `terraform.tfvars` with your AWS key pair name:

```hcl
key_pair_name = "your-key-pair-name"
aws_region    = "us-east-1"  # Change if needed
```

### 3. Review and Apply Terraform Configuration

```bash
# Review the changes that will be made
terraform plan

# Apply the configuration
terraform apply
```

When prompted, type `yes` to confirm the creation of resources.

### 4. Connect to the EC2 Instance

After the deployment is complete, Terraform will output the public IP address of the EC2 instance. Use this IP to connect via SSH:

```bash
ssh -i /path/to/your-key-pair.pem ec2-user@<public-ip>
```

### 5. Monitor Application Deployment

The application should be automatically deployed by the installation script. You can check the status with:

```bash
sudo systemctl status bookreview
```

To view application logs:

```bash
journalctl -u bookreview -f
```

### 6. Access the Application

The application will be available at:
```
http://<public-ip>:8000
```

## Cost Control

### Stopping the EC2 Instance

To stop the EC2 instance when not in use (to save costs):

1. Via AWS Console:
   - Go to EC2 Dashboard
   - Select the instance
   - Click Actions > Instance State > Stop

2. Via AWS CLI:
```bash
aws ec2 stop-instances --instance-ids <your-instance-id>
```

### Starting the EC2 Instance

When you need to use the application again:

1. Via AWS Console:
   - Go to EC2 Dashboard
   - Select the instance
   - Click Actions > Instance State > Start

2. Via AWS CLI:
```bash
aws ec2 start-instances --instance-ids <your-instance-id>
```

### Destroying Resources

When you're completely done with testing and want to avoid any costs:

```bash
cd deployment
terraform destroy
```

When prompted, type `yes` to confirm the deletion of all resources.

## Important Notes

1. The setup uses a t2.micro instance which is free-tier eligible.
2. PostgreSQL is installed locally on the EC2 instance to avoid RDS costs.
3. Security group is configured to allow only necessary ports (22 for SSH, 8000 for the application).
4. All resources are created in a single availability zone to minimize costs.

## Troubleshooting

1. If the application is not accessible:
   - Check the security group rules
   - Verify the application service is running: `sudo systemctl status bookreview`
   - Check application logs: `journalctl -u bookreview -f`

2. If you can't connect via SSH:
   - Verify your key pair
   - Check the instance's security group rules
   - Ensure the instance is running

3. Database issues:
   - Check PostgreSQL status: `sudo systemctl status postgresql`
   - Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
