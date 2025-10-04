# EC2 Application Commands

Here are the commands you can run on your EC2 box to manage the application:

## One-Line Installation (If Not Already Set Up)

```bash
# First time setup - install dependencies, PostgreSQL, and prepare environment
curl -sSL https://raw.githubusercontent.com/smsingh-tal/book-review-backend/main/deployment/amazon_linux_2023_setup.sh | bash
```

## Application Management Commands

```bash
# 1. Start the application (run this from your project directory)
chmod +x deployment/fixes/run_application_with_poetry.sh
./deployment/fixes/run_application_with_poetry.sh

# 2. Stop the application
pkill -f 'uvicorn app.main:app'

# 3. Check if application is running
ps aux | grep 'uvicorn app.main:app' | grep -v grep

# 4. View application logs
tail -f logs/server.log

# 5. Restart the application
pkill -f 'uvicorn app.main:app' && ./deployment/fixes/run_application_with_poetry.sh
```

## Database Management Commands

```bash
# 1. Start PostgreSQL if it's not running
sudo systemctl start postgresql

# 2. Check PostgreSQL status
sudo systemctl status postgresql

# 3. Create database and user (if not already created)
sudo -u postgres psql -c "CREATE DATABASE book_reviews; CREATE USER book_user WITH PASSWORD 'book_password'; GRANT ALL PRIVILEGES ON DATABASE book_reviews TO book_user;"

# 4. Run database migrations
cd /path/to/your/project && poetry run alembic upgrade head

# 5. Backup database
sudo -u postgres pg_dump book_reviews > book_reviews_backup_$(date +%Y%m%d).sql
```

## Troubleshooting Commands

```bash
# 1. Check if port 8000 is in use
sudo netstat -tuln | grep 8000

# 2. Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# 3. Check database connection
cd /path/to/your/project && poetry run python -c "import psycopg2; conn = psycopg2.connect(dbname='book_reviews', user='book_user', password='book_password', host='localhost', port=5432); print('Connection successful!'); conn.close()"

# 4. Test API endpoints
curl http://localhost:8000/api/v1/health
```

To check the server's public IP address (to access your API):
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

Then access your API at: `http://<EC2-PUBLIC-IP>:8000/docs`
