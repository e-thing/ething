import traceback

def import_all():
    import pkgutil

    for loader, module_name, is_pkg in  pkgutil.iter_modules(__path__):
        try:
            module = loader.find_module(module_name).load_module(module_name)
        except Exception as e:
            print('plugin "%s" import failed: %s' % (module_name, str(e)))
            traceback.print_exc()
        else:
            print('plugin "%s" imported' % module_name)
            globals()[module_name] = module