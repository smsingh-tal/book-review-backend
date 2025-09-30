# Complete Beginner's Guide to AWS Deployment

This guide will walk you through deploying your application on AWS, starting from absolute basics. Follow each step carefully.

## Part 1: Initial Setup (On Your Local Machine)

### 1. Create an AWS Account
1. Go to [AWS Free Tier](https://aws.amazon.com/free)
2. Click "Create a Free Account"
3. Follow the signup process
4. Keep your AWS access credentials safe:
   - Access Key ID
   - Secret Access Key

### 2. Install Required Software (macOS)
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install AWS CLI
brew install awscli

# Install Terraform
brew install terraform
```

For Windows users, download and install:
- AWS CLI from: https://aws.amazon.com/cli/
- Terraform from: https://developer.hashicorp.com/terraform/downloads

### 3. Configure AWS CLI
```bash
aws configure
```
When prompted, enter:
- Your AWS Access Key ID
- Your AWS Secret Access Key
- Default region: `us-east-1` (recommended for free tier)
- Default output format: `json`

### 4. Create SSH Key Pair
```bash
# Create a key pair in AWS (you'll need this to connect to your server)
aws ec2 create-key-pair --key-name my-book-review-key --query 'KeyMaterial' --output text > ~/.ssh/my-book-review-key.pem

# Set correct permissions
chmod 400 ~/.ssh/my-book-review-key.pem
```

## Part 2: Deploying with Terraform

### 1. Prepare Terraform Configuration

1. Navigate to your project's deployment directory:
```bash
cd deployment
```

2. Verify you have these three required Terraform files (they should already be in your deployment directory):
   - `main.tf` - Main configuration file
   - `variables.tf` - Variable definitions
   - `install_dependencies.sh` - EC2 instance setup script

3. Create a file named `terraform.tfvars`:
```bash
# Create and edit terraform.tfvars
cat > terraform.tfvars << EOL
aws_region = "us-east-1"
key_pair_name = "my-book-review-key"
EOL
```

4. Verify your files:
```bash
# You should see these files
ls -la
# Expected output should include:
# - main.tf
# - variables.tf
# - terraform.tfvars
# - install_dependencies.sh
# - setup_app.sh
```

If any of these files are missing, create them as follows:

a. If `main.tf` is missing:
```bash
# Get the main.tf content from your repository
curl -o main.tf https://raw.githubusercontent.com/smsingh-tal/book-review-backend/main/deployment/main.tf
```

b. If `variables.tf` is missing:
```bash
# Get the variables.tf content from your repository
curl -o variables.tf https://raw.githubusercontent.com/smsingh-tal/book-review-backend/main/deployment/variables.tf
```

c. If `install_dependencies.sh` or `setup_app.sh` is missing:
```bash
# Get the script files from your repository
curl -o install_dependencies.sh https://raw.githubusercontent.com/smsingh-tal/book-review-backend/main/deployment/install_dependencies.sh
curl -o setup_app.sh https://raw.githubusercontent.com/smsingh-tal/book-review-backend/main/deployment/setup_app.sh
chmod +x install_dependencies.sh setup_app.sh
```

### 2. Initialize and Apply Terraform
```bash
# Initialize Terraform
terraform init

# See what changes will be made
terraform plan

# Apply the changes (enter 'yes' when prompted)
terraform validate
terraform apply
```

### 3. Note the IP Address
After successful deployment, Terraform will output the public IP address of your EC2 instance. Save this IP address - you'll need it to access your application.

## Part 3: Accessing Your Application

### 1. Wait for Installation
The server will take about 5-10 minutes to complete all installations. You can check the progress by connecting to the server:

```bash
ssh -i ~/.ssh/my-book-review-key.pem ec2-user@<your-server-ip>

# Once connected, check installation progress
sudo journalctl -u bookreview -f
```

### 2. Test Your Application
Once installation is complete, you can access your application at:
- API: `http://<your-server-ip>:8000`
- API Documentation: `http://<your-server-ip>:8000/docs`

## Part 4: Cost Management

### 1. Stop Instance When Not in Use
To avoid charges when not using the application:

```bash
# Get your instance ID
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId]' --output text

# Stop the instance (replace i-1234567890abcdef0 with your instance ID)
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

### 2. Start Instance When Needed
```bash
# Start your instance (replace i-1234567890abcdef0 with your instance ID)
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### 3. Completely Remove Resources
When you're done testing and want to remove all resources:
```bash
cd /path/to/book-review-backend/deployment
terraform destroy  # Enter 'yes' when prompted
```

## Troubleshooting

### 1. Connection Issues
If you can't connect to your instance:
- Wait 5-10 minutes after creation for all services to start
- Verify security group allows port 8000
- Check if the instance is running in AWS Console

### 2. Application Issues
If the application isn't responding:
```bash
# Connect to your instance
ssh -i ~/.ssh/my-book-review-key.pem ec2-user@<your-server-ip>

# Check application logs
sudo journalctl -u bookreview -f

# Check if service is running
sudo systemctl status bookreview

# Restart if needed
sudo systemctl restart bookreview
```

### 3. Database Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## Important Notes

1. Security:
   - Keep your AWS credentials secure
   - Never commit `terraform.tfvars` to git
   - Keep your SSH key (`my-book-review-key.pem`) secure

2. Costs:
   - Always stop instances when not in use
   - Destroy resources when done testing
   - Monitor AWS billing dashboard regularly

3. Maintenance:
   - Regularly check application logs
   - Update your application when needed
   - Keep track of AWS Free Tier usage

## Need Help?

1. AWS Free Tier Info: https://aws.amazon.com/free
2. Terraform Documentation: https://developer.hashicorp.com/terraform/docs
3. AWS CLI Documentation: https://aws.amazon.com/cli/

Remember to ALWAYS destroy your resources when you're done testing to avoid unexpected charges!
