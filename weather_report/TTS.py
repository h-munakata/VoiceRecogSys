import subprocess
import os
'import winsound'


# OpenJTalkのオプション読み込み
cmd = 'open_jtalk '
selects = [
    '-x',
    '-m',
    '-s',
    '-p',
    '-a',
    '-b',
    '-r',
    '-fm',
    '-u',
    '-jm',
    '-jf',
    '-g',
    '-z'
]

with open('weather.cfg',mode='r') as f:
    options = f.readlines()
for option in options:
    if option[:2] in selects or option[:3] in selects:
        cmd += option.rstrip() + ' '

cmd += '-ow talking.wav'


def jtalk(t):
    jtalk_process = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    # convert text encoding from utf-8 to shitf-jis
    jtalk_process.stdin.write(t.encode('utf-8'))
    jtalk_process.stdin.close()
    jtalk_process.wait()

    '''with open('talking.wav', 'rb') as f:
        data = f.read()
    winsound.PlaySound(data, winsound.SND_MEMORY)'''

    subprocess.call('sox talking.wav -d -q --buffer 9999999')

if __name__ == '__main__':
    message = 'こんにちは'
    jtalk(message)
    print(cmd)
    os.remove('talking.wav')