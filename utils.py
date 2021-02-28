def clean_exit(func):
    def clean(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            exit(1)

    return clean
