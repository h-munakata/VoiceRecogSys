import requests
import json
import csv
import TTS
import datetime

# オプション用変数
options = []

# 日本時間と標準時間の差
DIFF_JST_FROM_UTC = 9

# データを格納
forecasts = {}
locate_id = {}

with open('locate_id.csv',encoding='utf-8') as f:
    data = csv.reader(f)
    for row in data:
        locate_id[row[0]] = str(row[1].rstrip())


# 出力選択
def output(text,end=None):
    global options

    #テキストモード
    if '-q' not in options:
        print(text)

    #音声モード
    if '-v' in options:
        TTS.jtalk(text.replace('【','').replace('】',''))

    #ログのオプション
    if '-l' in options:
        with open('log.txt',encoding='utf-8',mode='a') as f:
            f.write('システム >> '+text+'\n')


# 起動時
def greeting():
    global DIFF_JST_FROM_UTC
    dt_now = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
    if (5 <= dt_now.hour <= 11):
        output('おはようございます。どこの天気を知りたいですか？')
    elif (12 <= dt_now.hour <= 16):
        output('こんにちは。どこの天気を知りたいですか？')
    elif (17 <= dt_now.hour <= 23):
        output('こんばんは。どこの天気を知りたいですか？')
    else:
        output('遅くまでお疲れ様です。どこの天気を知りたいですか？')
    output('もし使い方がわからなかったら、「ヘルプ」と話してください。')


# 終了時
def goodbye(inp):
    global DIFF_JST_FROM_UTC
    dt_now = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
    if (5 <= dt_now.hour <= 11):
        output('プログラムを終了します。それでは今日も一日頑張っていきましょう。')
    elif (12 <= dt_now.hour <= 16):
        output('プログラムを終了します。それでは午後からも頑張っていきましょう。')
    elif (17 <= dt_now.hour <= 23):
        output('プログラムを終了します。お疲れ様でした。')
    else:
        output('プログラムを終了します。おやすみなさい。')


# ヘルプ
def help(inpu):
    output('まずはじめに、「(都道府県名)の天気を教えて」と話してください。するとその県の天気をお教えいたします。')
    output('次に、「（今日、明日、あさってのいずれか）の天気を教えて」と話してください。するとその日の天気をお教えいたします。')
    output('また、「詳細を教えて」と話すと、その地域の詳しい天気をお教えいたします。')
    output('最後に、「ありがとう」あるいは「もういいよ」と言われると、プログラムを終了します。')
    output('では知りたい場所の天気を教えてください。')

# 別の日の天気を表示
def other_report(inp):
    global forecasts
    if inp[1]['WORD']=='今日':
        print_report(forecasts,1)
    elif inp[1]['WORD']=='明日':
        print_report(forecasts,2)
    elif inp[1]['WORD']=='明後日':
        print_report(forecasts,3)


# 詳細を表示
def detail_report(inp):
    global forecasts
    print_report(forecasts,4)


# 音声データから都道府県名を特定
# その後、県名と今日の天気を表示
def today_report(inp):
    global forecasts
    prefecture = inp[1]['WORD']
    if prefecture=='東京':
        prefecture = prefecture + '都'
    elif prefecture=='大阪' or  prefecture=='京都':
        prefecture = prefecture + '府'
    elif prefecture[-1]!='県':
        prefecture = prefecture + '県'
    
    id = locate_id[prefecture]
    forecasts = get_report(id)
    print_report(forecasts)


# 結果を出力
def print_report(forecasts,option=0,mode='normal'):
    # option
    # 0:場所と今日の天気を表示
    # 1:今日の天気を表示
    # 2:明日の天気を表示
    # 3:明後日の天気を表示
    # 4:詳細を表示
    if option not in [0,1,2,3,4]:
        output('不正なオプションが選択されました。')
        exit()
    if option==0:
        output('{0}{1}の天気です。'.format(forecasts['prefecture'],forecasts['city']))
    if option==0 or option==1:
        output('本日、{0}の天気は'.format(forecasts['date'][0]),end='')
    elif option==2:
        output('明日、{0}の天気は'.format(forecasts['date'][1]),end='')
    elif option==3:
        if len(forecasts['date'])>=3 :
            output('明後日、{0}の天気は'.format(forecasts['date'][2]),end='')
        else:
            output('申し訳ありません。明後日のデータはありません。')
            return
    if 0<=option<=3:
        if option==0:
            i = 0
        else:
            i = option-1
        output('{0}で、'.format(forecasts['condition'][i],),end='')
        if forecasts['min'][i]!='---':
            output('最低気温は{0}で、'.format(forecasts['min'][i]),end='')
        else:
            output('最低気温はデータなしで、',end='')
        if forecasts['max'][i]!='---':
            output('最高気温は{0}です'.format(forecasts['max'][i]))
        elif forecasts['min'][i]!='---' and forecasts['max'][i]!='---':
            output('最高気温もデータなしです。')
        else:
            output('最高気温はデータなしです。')
    if option==4:
        output('詳細についてです。\n')
        description = forecasts['description'].split()
        for line in description:
            output(line)


# .jsonの取得および加工
def get_report(id):
    # 配列の初期化
    # keys = {'prefecture','city',date','condition','min','max','description'}
    forecasts = {}

    # jsonデータの取得、辞書化
    response = requests.get('http://weather.livedoor.com/forecast/webservice/json/v1?city='+id)
    json_data = response.text
    data = json.loads(json_data)

    # データを切り出し
    for key,value in data.items():
        if key=='location':
            for i in range(len(value)):
                forecasts['prefecture'] = value['prefecture']
                forecasts['city'] = value['city']
        
        elif key=='forecasts':
            # 日にちごとに格納
            date,condition,min,max = [],[],[],[]
            for i in range(len(value)):
                ref_date = value[i]['date'].split('-')
                for j in range(len(ref_date)):
                    ref_date[j] = ref_date[j].lstrip('0')

                date.append('{0}月{1}日'.format(ref_date[1],ref_date[2]))
                condition.append(value[i]['telop'])

                if value[i]['temperature']['min']!=None:
                    min.append(value[i]['temperature']['min']['celsius']+'℃')
                else:
                    min.append('---')
                if value[i]['temperature']['max']!=None:
                    max.append(value[i]['temperature']['max']['celsius']+'℃')
                else:
                    max.append('---')
                
                forecasts['date'] = date
                forecasts['condition'] = condition
                forecasts['min'] = min
                forecasts['max'] = max

        elif key=='description':
            forecasts['description'] = value['text'].replace('\n\n','\n')


    return forecasts

