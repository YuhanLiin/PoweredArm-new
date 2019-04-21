import glob
import sys
import os
import subprocess

if __name__ == '__main__':
    target = sys.argv[1]

    if not os.path.exists('out'):
        os.mkdir('out')

    output = os.path.join('out', 'tests')
    flags = ['-Wall']
    src = glob.glob(os.path.join('src', '*.c'))
    inc = ['src']

    if target == 'test':
        src += glob.glob(os.path.join('tests', '*.c'))
        inc += ['tests']
    else:
        inc += [os.path.join('..', 'host', 'out')]
    inc = ['-I'+path for path in inc]

    cmd = ['gcc'] + flags + inc + src + ['-o', output]
    print(cmd)
    subprocess.check_call(cmd)
    subprocess.call([output])
