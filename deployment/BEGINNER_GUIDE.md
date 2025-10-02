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
aws ec2 create-key-pair --key-name my-aws-key --query 'KeyMaterial' --output text > ~/.ssh/my-aws-key.pem

# Set correct permissions
chmod 400 ~/.ssh/my-aws-key.pem
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
key_pair_name = "my-aws-key"
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


## Part 4: Setting Up Your EC2 Environment (Linux)

After your EC2 instance is running, connect to it:
```bash
ssh -i ~/.ssh/my-aws-key.pem ec2-user@<your-server-ip>
```


### 1. Install System Dependencies
```bash
sudo yum update -y
sudo yum install -y git gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make postgresql postgresql-server postgresql-devel postgresql-contrib
```

### 2. Install Python 3.11 from Source
```bash
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
sudo tar xzf Python-3.11.7.tgz
cd Python-3.11.7
sudo ./configure --enable-optimizations
sudo make altinstall
```

### 3. Set Up PostgreSQL (local database)
```bash
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Allow password authentication and remote/local connections
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/'" /var/lib/pgsql/data/postgresql.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
sudo systemctl restart postgresql
```

### 4. Create and Activate Python 3.11 Virtual Environment
```bash
python3.11 -m venv ~/app_venv
source ~/app_venv/bin/activate
```

### 5. Install Poetry
```bash
pip install --upgrade pip
pip install poetry
```

### 6. Clone Your Application Repository
```bash
cd ~
git clone https://github.com/smsingh-tal/book-review-backend.git
cd book-review-backend
```

### 7. Install Application Dependencies
```bash
poetry env use ~/app_venv/bin/python
poetry install --no-dev
```

### 8. Set Up Environment File
```bash
if [ ! -f .env ]; then
   cp .env.example .env
   echo "Created .env file from example"
fi
```

### 9. Set Up Databases and Apply Migrations

```bash
# Set postgres user password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Create main application database
sudo -u postgres psql -c "CREATE DATABASE book_review;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE book_review TO postgres;"

# Create test database
sudo -u postgres psql -c "CREATE DATABASE book_review_test;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE book_review_test TO postgres;"

# Apply migrations safely with a modified approach for the second migration
# Create a backup of the original migration script
cp alembic/versions/005019b6ed22_add_book_description.py alembic/versions/005019b6ed22_add_book_description.py.bak

# Edit the migration file to safely handle index operations
cat > alembic/versions/005019b6ed22_add_book_description.py << 'EOF'
"""add_book_description

Revision ID: 005019b6ed22
Revises: 12edb603d2ec
Create Date: 2025-09-25 00:26:43.480499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005019b6ed22'
down_revision = '12edb603d2ec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the description column first
    op.add_column('books', sa.Column('description', sa.Text(), nullable=True))
    
    # Make the ISBN column not nullable
    op.alter_column('books', 'isbn',
               existing_type=sa.VARCHAR(length=13),
               nullable=False)
    
    # Handle indexes safely - check if they exist before dropping
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indices = inspector.get_indexes('books')
    index_names = [index['name'] for index in indices]
    
    # Only drop indexes if they exist
    if 'ix_books_average_rating' in index_names:
        op.drop_index(op.f('ix_books_average_rating'), table_name='books')
    
    if 'ix_books_genres' in index_names:
        op.drop_index(op.f('ix_books_genres'), table_name='books', postgresql_using='gin')
    
    if 'ix_books_publication_date' in index_names:
        op.drop_index(op.f('ix_books_publication_date'), table_name='books')


def downgrade() -> None:
    # Always create indexes on downgrade
    op.create_index(op.f('ix_books_publication_date'), 'books', ['publication_date'], unique=False)
    
    # Create gin index carefully
    try:
        op.create_index(op.f('ix_books_genres'), 'books', ['genres'], unique=False, postgresql_using='gin')
    except Exception:
        # Fallback to standard index if gin not supported
        op.create_index(op.f('ix_books_genres'), 'books', ['genres'], unique=False)
        
    op.create_index(op.f('ix_books_average_rating'), 'books', ['average_rating'], unique=False)
    
    # Revert other changes
    op.alter_column('books', 'isbn',
               existing_type=sa.VARCHAR(length=13),
               nullable=True)
    op.drop_column('books', 'description')
EOF

# Now run the migrations
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review poetry run alembic upgrade head

# Set up test database too
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review_test poetry run alembic upgrade head

# Load sample data if available
if [ -f "init_books.sql" ]; then
    psql -U postgres -d book_review -f init_books.sql
fi
```

### 10. Start the Application
```bash
poetry run python app/main.py
```

Your application will now run with Python 3.11 and dependencies matching your local machine. PostgreSQL will be available on the same EC2 instance.

### 11. Run Tests (Optional)
```bash
# Run all tests
poetry run pytest tests/

# Or run a specific test file
poetry run pytest tests/test_db_connection.py -v
```

### 3. Create and Activate Python Virtual Environment
```bash
python3 -m venv ~/app_venv
source ~/app_venv/bin/activate
```

### 4. Install Poetry
```bash
pip install --upgrade pip
pip install poetry
```

### 5. Clone Your Application Repository
```bash
cd ~
git clone https://github.com/smsingh-tal/book-review-backend.git
cd book-review-backend
```

### 6. Install Application Dependencies
```bash
poetry env use ~/app_venv/bin/python
poetry install --no-dev
```

### 7. Set Up Environment File
```bash
if [ ! -f .env ]; then
   cp .env.example .env
   echo "Created .env file from example"
fi
```

### 8. Start the Application
```bash
poetry run python app/main.py
```

Your application will now run with the same Python environment and dependencies as your local machine. PostgreSQL will be available on the same EC2 instance.

---
### Test Your Application
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
ssh -i ~/.ssh/my-aws-key.pem ec2-user@<your-server-ip>

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
   - Keep your SSH key (`my-aws-key.pem`) secure

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
