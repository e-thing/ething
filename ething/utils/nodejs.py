
import subprocess

def is_nodejs_installed(core = None):
    
    exe = "nodejs"
    res = False
    
    if core:
        exe = core.config.get('nodejs.executable', None)
    
    if exe:
        try:
            res = subprocess.check_output([exe, "--version"]).strip()
        except OSError as e:
            pass
    
    return res




if __name__ == '__main__':
    
    
    print is_nodejs_installed()

