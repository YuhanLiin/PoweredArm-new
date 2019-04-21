import glob
import sys
import os
import subprocess

if __name__ == '__main__':
    if not os.path.exists('out'):
        os.mkdir('out')

    output = os.path.join('out', 'tests')
    flags = ['-Wall']
    src = glob.glob(os.path.join('src', '*.c'))
    inc = os.path.join('-I..', 'host', 'out')

    cmd = ['gcc'] + flags + [inc] + src + ['-o', output]
    subprocess.call(cmd)
