import os, sys, resource

ALLOWED = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.getcwd()
target = sys.argv[1]

STDLIB = tuple(os.path.abspath(p) for p in (sys.base_prefix, sys.prefix, '/usr/lib', '/lib', '/usr/local/lib'))

resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024, 768 * 1024 * 1024))
resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))

BLOCK = ('socket.', 'subprocess.', 'os.system', 'os.exec', 'os.spawn', 'os.fork',
         'os.posix_spawn', 'pty.spawn', 'shutil.', 'os.remove', 'os.rename',
         'os.rmdir', 'os.mkdir', 'os.chmod', 'os.chown', 'os.link', 'os.symlink')

def hook(event, args):
    if event == 'open':
        path, mode, flags = args
        ap = os.path.abspath(str(path))
        writing = mode and any(c in str(mode) for c in 'wax+')
        inside = ap.startswith(ALLOWED)
        stdlib = ap.startswith(STDLIB)
        if writing and not inside:
            raise PermissionError('ecriture hors sandbox refusee')
        if not writing and not (inside or stdlib):
            raise PermissionError('lecture hors sandbox refusee')
        return
    if event.startswith(BLOCK):
        raise PermissionError('operation interdite: ' + event)

sys.addaudithook(hook)
code = compile(open(target).read(), target, 'exec')
g = {'__name__': '__main__', '__file__': target}
exec(code, g)
