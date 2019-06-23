if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.config.settings')
    django.setup()

    from bot.launch import launcher

    launcher()
