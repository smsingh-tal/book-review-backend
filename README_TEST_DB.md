# Setting Up the Test Database

This guide explains how to set up the test database for both your local environment and on AWS EC2.

## Local Environment Setup

### 1. Create the Test Database

Run the following command from the project root directory:

```bash
# Create the test database
poetry run python scripts/create_test_database.py
```

### 2. Run Migrations

After creating the database, apply the migrations:

```bash
# Apply migrations to the test database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review_test poetry run alembic upgrade head
```

### 3. Run Tests

Now you can run tests:

```bash
# Run all tests
poetry run pytest tests/
# Run specific test
poetry run pytest tests/test_auth.py -v
```

## AWS EC2 Setup

### 1. Connect to your EC2 instance

```bash
ssh -i ~/.ssh/my-aws-key.pem ec2-user@<your-server-ip>
```

### 2. Create the Test Database

Navigate to your project directory and run:

```bash
cd ~/book-review-backend
source ~/app_venv/bin/activate
python scripts/create_test_database.py
```

### 3. Run Migrations

Apply migrations to create schema:

```bash
# Apply migrations to the test database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review_test alembic upgrade head
```

### 4. Run Tests

Now you can run the tests:

```bash
# Run all tests
python -m pytest tests/
# Run specific test
python -m pytest tests/test_auth.py -v
```

## Troubleshooting

If you encounter authentication issues with PostgreSQL:

1. Check PostgreSQL authentication settings:
   ```bash
   sudo nano /var/lib/pgsql/data/pg_hba.conf
   ```

2. Ensure PostgreSQL is using md5 authentication:
   ```
   # TYPE  DATABASE        USER            ADDRESS                 METHOD
   host    all             all             0.0.0.0/0               md5
   ```

3. Restart PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```

4. Set a password for the PostgreSQL user:
   ```bash
   sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
   ```
