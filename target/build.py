import glob
import sys
import os
import subprocess

def print_help(retcode):
    print('Usage: python build.py [command]')
    print('')
    print('COMMAND test')
    print('Builds and runs tests locally.')
    print('')
    print('COMMAND target')
    print('Builds and runs code on target. Does not work yet.')
    print('')
    sys.exit(retcode)

if __name__ == '__main__':
    try:
        target = sys.argv[1]
    except IndexError:
        print_help(1)

    if not os.path.exists('out'):
        os.mkdir('out')

    output = os.path.join('out', 'tests')
    flags = ['-Wall']
    src = glob.glob(os.path.join('src', '*.c'))
    inc = ['src']

    if target == 'test':
        src += glob.glob(os.path.join('tests', '*.c'))
        inc += ['tests']
    elif target == 'target':
        inc += [os.path.join('..', 'host', 'out')]
    else:
        print_help(1)

    inc = ['-I'+path for path in inc]

    cmd = ['gcc'] + flags + inc + src + ['-o', output]
    print(' '.join(cmd))
    subprocess.check_call(cmd)
    subprocess.call([output])
