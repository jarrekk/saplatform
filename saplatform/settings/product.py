
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autoops',
        'USER': 'auto',
        'PASSWORD': 'asdf123',
        'HOST': 'managezabbix.mysql.rds.aliyuncs.com',
        'PORT': '3306',
    }
}

SALT_MASTER = '10.47.94.54'

SALTAPI_URL = 'https://127.0.0.1:8000'

SALTAPI_USER = 'sasalt'

SALTAPI_PASSWORD = 'zjddsa'

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'