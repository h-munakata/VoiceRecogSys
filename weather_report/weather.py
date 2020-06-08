import FSM
import JuliusProxy
import subprocess
import weather_get as wg
import sys
import os


options = sys.argv[1:]
option_list = ['-v','-h','-l','-q']

for opt in options:
    if opt in option_list:
        wg.options.append(opt)
    else:
        print('不正なオプションが指定されました。\nオプション一覧\n -v 音声出力\n -h ヘルプ')
        exit()


if '-h' in options:
    print('詳しい使い方は\'00readme.txt\'を確認してください')
    print('\nオプション一覧\n -v 音声出力/n -l ログの生成\n -q 標準出力をオフにする\n -h ヘルプ')
    exit()


# 前回のログファイルの削除
if os.path.exists('log.txt') and '-l' in options:
    os.remove('log.txt')


# Juliusのオプション読み込み、起動
cmd = 'Julius '
selects = ['-C']

with open('weather.cfg') as f:
    configs = f.readlines()
for cfg in configs:
    if cfg[:2] in selects:
        cmd += cfg.rstrip() + ' '

cmd += '-module'

julius_process = subprocess.Popen(cmd,stdout = subprocess.DEVNULL,stderr = subprocess.DEVNULL)


# 応答内容の内、.dictに対応する部分を抽出して返す
def getClassID(inp):
    return inp[1]["CLASSID"]


# プログラムを終了する
def end_sys(proxy):
    global options
    proxy.end()
    julius_process.kill()
    if os.path.exists('talking.wav'):
        os.remove('talking.wav')
    exit()


# 状態を生成
s_greet = FSM.State()
s_location = FSM.State()
s_other_data = FSM.State()
s_exit = FSM.State()
s_help = FSM.State()


# 遷移関数を定義
loc = [0,1,2,3,4,5,6]
date = [7]
detail = [10]
bye = [13]
help = [14]

s_greet.setTransition(getClassID, loc, s_location, wg.today_report)
s_greet.setTransition(getClassID, bye, s_exit, wg.goodbye)
s_greet.setTransition(getClassID, help, s_help, wg.help)

s_location.setTransition(getClassID, loc, s_location, wg.today_report)
s_location.setTransition(getClassID, detail, s_other_data, wg.detail_report)
s_location.setTransition(getClassID, date, s_other_data, wg.other_report)
s_location.setTransition(getClassID, bye, s_exit, wg.goodbye)
s_location.setTransition(getClassID, help, s_help, wg.help)

s_other_data.setTransition(getClassID, loc, s_location, wg.today_report)
s_other_data.setTransition(getClassID, date, s_other_data, wg.other_report)
s_other_data.setTransition(getClassID, detail, s_other_data, wg.detail_report)
s_other_data.setTransition(getClassID, bye, s_exit, wg.goodbye)
s_other_data.setTransition(getClassID, help, s_help, wg.help)

s_help.setTransition(getClassID, loc, s_location, wg.today_report)
s_help.setTransition(getClassID, bye, s_exit, wg.goodbye)
s_help.setTransition(getClassID, help, s_help, wg.help)

# fsmに状態をセット
fsm = FSM.FSM()
fsm.setState(s_greet)
fsm.setState(s_location)
fsm.setState(s_other_data)
fsm.setState(s_exit)
fsm.setState(s_help)


# Juliusとtcpにて通信
proxy = JuliusProxy.JuliusProxy()

proxy.terminate()
wg.greeting()
proxy.resume()

result = []
while 1:
    proxy.getResult() # Juliusからの応答を受け取り、resultへ格納
    result = proxy.parseResult()
    skip = True

    if result == []: continue
    else:
        # 認識結果の表示
        text = ''
        for i in range(1,len(result)-1):
            text += result[i]['WORD']
        
        if '-q' not in options:
                print('\n>>'+text+'\n')
        if '-l' in options:
            with open('log.txt',encoding='utf-8',mode='a') as f:
                f.write('話者 >> '+text+'\n')

    # 状態に入力を与え、遷移させる
    proxy.terminate()
    fsm.feed(result)
    proxy.resume()

    for res in result:
        if res['CLASSID'] in bye:
            end_sys(proxy)



