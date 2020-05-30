from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from module import func,todatabase,authorize

import math
import sys
import datetime
from datetime import date,timedelta
import time
import calendar
import mysql.connector

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    mtext = event.message.text
                    if mtext == "使用方法":
                        func.manual(event)
                    #體溫登陸
                    if mtext[0]=="體" and mtext[1]=="溫":
                        destclass="lssh"+mtext[3]+mtext[4]+mtext[5]
                        lssh1 = mysql.connector.connect(
                        host = todatabase.host(),
                        port = "3306",
                        user = "liaojason2",
                        password = "Liaojason123!",
                        database = destclass)
                        try:
                            gcpsql= lssh1.cursor()
                            output=""
                            sql_select_Query = "select * from body_temperture"
                            gcpsql.execute(sql_select_Query)
                            records = gcpsql.fetchall()
                            output+=destclass[4]+destclass[5]+destclass[6]+" 體溫總表：\n\n"
                            for row in records:
                                output+=str(row[1])+". "+str(row[3])+" "+str(row[4])+"\n"
                            output+="\n輸出結束"
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=output))
                        except:
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="本班級不存在"))
                    if mtext[0]=="s" and mtext[1]=="e" and mtext[2]=="t":#設定座號
                        lssh1 = mysql.connector.connect(
                        host = todatabase.host(),
                        port = "3306",
                        user = todatabase.username(),
                        password = todatabase.password(),
                        database = todatabase.database(),)
                        gcpsql= lssh1.cursor()
                        user_id=event.source.user_id
                        profile=line_bot_api.get_profile(user_id)
                        name=profile.display_name
                        expt=""
                        for j in range (4,len(mtext)):
                            expt+=mtext[j]
                        check=int(expt)
                        target="""select rw FROM user_id"""
                        gcpsql.execute(target)
                        records = gcpsql.fetchall()
                        if(records[check-1][0]==1):
                            target="""UPDATE user_id SET line_id=%s, nickname=%s WHERE stu_id=%s"""
                            record=(user_id,name,expt)
                            gcpsql.execute(target,(record))
                            lssh1.commit()
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="新增座號成功"))
                        else: line_bot_api.reply_message(event.reply_token,TextSendMessage(text="本座號已設定並由管理員確認，若需更改請填寫錯誤回報表單"))
                        if (lssh1.is_connected()):
                            gcpsql.close()
                            lssh1.close()
                    if mtext=="推播通知":
                        lssh1 = mysql.connector.connect(
                        host = todatabase.host(),
                        port = "3306",
                        user = todatabase.username(),
                        password = todatabase.password(),
                        database = todatabase.database(),)
                        gcpsql= lssh1.cursor()
                        id=event.source.user_id
                        sql_select_Query = "select line_id,notify from user_id"
                        gcpsql.execute(sql_select_Query)
                        records = gcpsql.fetchall()
                        notify=0
                        i=1
                        for row in records:
                            if(row[0]==id):
                                notify=row[1]
                                break 
                            i+=1
                        if (notify==0): notify=1
                        elif (notify==1): notify=0
                        update="""UPDATE user_id SET notify=%s WHERE stu_id=%s"""
                        value=(notify,i)
                        gcpsql.execute(update,(value))
                        lssh1.commit()
                        if (notify==0): func.notifyoff(event)
                        elif (notify==1): func.notifyon(event)
                    '''# user_id
                    if mtext!= "":
                        auth_json_path='linebotlssh-a0cc46d0d13a.json'
                        gss_scopes=['https://www.googleapis.com/auth/spreadsheets']
                        credentials= ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)
                        gss_client =gspread.authorize(credentials)
                        spreadsheets_key='1pe5azLF0piRgd00QSLZBDiiqXPAhOXmIo9kBMTtYaE0'
                        sheet=gss_client.open_by_key(spreadsheets_key).sheet1
                        user_id = event.source.user_id
                        profile=line_bot_api.get_profile(user_id)
                        a=str(user_id)
                        flag=0
                        for i in range (2,30):
                            if (sheet.cell(i,3).value) == a:
                                if (sheet.cell(i,2).value) == "":
                                    sheet.update_cell(i,2,profile.display_name)
                                    flag=1
                                else:
                                    flag=1    
                        if(flag==0):
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            a=len(mtext)
                            output=""
                            for i in range(1,a): output+=mtext[i] 
                            output=[timestamp,profile.display_name,user_id]
                            sheet.insert_row(output,2)'''
        return HttpResponse()
    else:
        return HttpResponseBadRequest()