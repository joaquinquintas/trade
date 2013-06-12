from settings_default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',     
        'NAME': 'trade',                               
        'USER': 'root',                                       
        'PASSWORD': '',                              
        'HOST': '/tmp/mysql.sock',                                            
        'PORT': '',                                            
    }
}

THUMBNAIL_DEBUG = True
