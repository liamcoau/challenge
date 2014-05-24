CELERY_MONGODB_BACKEND_SETTINGS = {
    "database": "files"
}

CELERY_ACCEPT_CONTENT = [
    "pickle",
    "json",
    "msgpack",
    "yaml"
]

if __name__ == "__main__":
    print("This file is only for use by celery in config_from_object, do not attempt to run it.")
