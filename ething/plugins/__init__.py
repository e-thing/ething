from ething.core.plugin import import_from_path

def import_all():
    import_from_path(__path__)
