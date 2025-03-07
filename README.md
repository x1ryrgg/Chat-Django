# Chat on Django
Chat Application Example

## Main Features:
- Asynchronous chat using WebSockets.
- Creation of group chats, extensive functionality within the chat.
- Support full-text search on users, adding friends.
- Viewing Friend Notifications.
- Support for executing periodic tasks with Celery and Celery beat.
- Support for Redis message broker.
- Changing profile.

## Installation:
Clone repos
```bash 
git https://github.com/x1ryrgg/Chat-Django.git
```

Go to workdir `cd Chat_Django`

Install via pip: `pip install -r requirements.txt`

### Configuration
Most configurations are in `settings.py`, others are in backend configurations.

I have set a lot of `settings` via environment variables (such as `SECRET_KEY`, `DEBUG` and some parts of the email config) and they are NOT pushed to `GitHub`. You can change their config in `settings.py` or create a `.env` file and set the environment variables yourself.

### Docker-compose up до сюда дошел 
Build and run containers as daemon 
`docker-compose up --build`

## Run

Modify `chat/settings.py` with database settings, as following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'Chat_db',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'db',
        'PORT': 5432,
    }
}
```

### Create database
Run the following command in PostgreSQL shell:
```sql
craetedb `Chat_db`;
```

Run the following commands in Terminal:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
```  

### Create super user

Run command in terminal:
```bash
python manage.py createsuperuser