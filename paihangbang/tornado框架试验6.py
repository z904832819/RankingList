from gevent import monkey;
import pymysql
monkey.patch_all()
import hashlib
import operator
import datetime
import random
import string
import requests
import redis, json
import tornado.escape
import tornado.ioloop
import tornado.web


def ClientConcurrency(acc_max_limit):  # 判断用户并发量是否已经跑满
    if int(acc_max_limit) > 0:
        pass
    else:
        return {'code': 401, 'message': '用户并发量已满'}


# 进行号码绑定
def PhoneBindInter(client_id,appkey, telA, telX, telB, sip, sipgoup, groupXname, bind_type,secret,Xdict,balance):
    # 当前时间时分秒
    ti = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 当前时间时分秒三位数
    ti3f = datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")[:-3].replace(".", "")
    # 随机号码
    num = string.ascii_letters + string.digits
    # 随机32位号码
    id = "".join(random.sample(num, 32))
    # appkey引号平台专用
    headers = {
        "appkey": appkey,
        "ts": ti3f,
    }
    # telA=大号 ，telX=小号，telB=被叫 ，其他参数为平台参数
    body = {
        "requestId": id,
        "telA": telA,
        "telX": telX,
        "telB": telB,
        "subts": ti,
        "anucode": "1,2,3",
        "areacode": "010",
        "expiration": "7200",
        "remark": "derc",
    }
    listh = []
    listb = []
    strex = ""
    ll = []
    # 排序请求头重新排序
    headlist = sorted(headers)
    for key in headlist:
        listh.append("".join(key + headers[key]))
    # 请求体排序
    bodylist = sorted(body)
    for key in bodylist:
        if key == "extra":
            liste = sorted(body["extra"])
            for ex in liste:
                cc = ex + body["extra"][ex]
                ll.append(cc)
                strex = "".join(ll)
            listb.append(strex)
        else:
            listh.append("".join(key + str(body[key])))

    # 整体头体重新拍戏
    listh.sort()
    # 重组新字符串
    sortb = "".join(listh)

    # 根据排序规则生成MD5加密
    msg = secret + sortb
    msgdgt = hashlib.md5(msg.encode(encoding='UTF-8')).hexdigest().upper()

    # 重新更新后的请求参数
    headers = {
        "appkey": appkey,
        "ts": ti3f,
        "msgdgt": msgdgt,
        'Content-Type': 'application/json;charset=utf-8',
        'Accept': 'application/json;charset=utf-8',
    }

    url = "http://121.31.41.91:9101/spn/secure/v2/axb/mode101"
    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(body))
    dictRe = json.loads(response.text)
    if dictRe["code"] == 0:
        # PhoneXCode = dictRe["data"]['telX']
        subId = dictRe["data"]['subid']
        dictRe['data']['sip'] = '{}'.format(sip)  #sip中继的唯一标识
        dictRe['data']['sip_group'] = '{}'.format(sipgoup) #网关群组
        dictRe['data']['Xpool'] = '{}'.format(groupXname) #X号所在池
        dictRe['data']['call_type'] = 0 #呼叫类型
        dictRe['data']['appkey'] = '{}'.format(appkey)  #Appkey
        dictRe['data']['bind_type'] = '{}'.format(bind_type) #绑定类型
        dictRe['data']['Anumber'] = '{}'.format(telA) #A号码
        dictRe['data']['client_id'] = '{}'.format(client_id) #客户唯一标识
        dictRe['data']['secret'] = '{}'.format(secret)
        dictRe['data']['balance'] = '{}'.format(balance)
        print(dictRe)

    else:
        dictRe['code'] = 401
        dictRe.update({'data':{'sip':sip}})
        dictRe['data']['sip_group'] = '{}'.format(sipgoup)  # 网关群组
        dictRe['data']['Xpool'] = '{}'.format(groupXname)  # X号所在池
        dictRe['data']['call_type'] = 0  # 呼叫类型
        dictRe['data']['appkey'] = '{}'.format(appkey)  # Appkey
        dictRe['data']['bind_type'] = '{}'.format(bind_type)  # 绑定类型
        dictRe['data']['Anumber'] = '{}'.format(telA)  # A号码
        dictRe['data']['client_id'] = '{}'.format(client_id)  # 客户唯一标识
        dictRe['data']['telX'] = '{}'.format(telX)
        Xdict[telX] = 0
        Xstr = json.dumps(Xdict)
        try:
            r.set(groupXname,Xstr)
            cur = con.cursor()
            cur.execute('update zb_numX set status=1 where Xnumber="{}"'.format(telX))
            data = {'alarm_level': '次要', 'alarm_types': 'X号码绑定失败', 'alarm_object': telX, 'alarm_value': '',
                    'alarm_threshold': '', 'alarm_info': ''}
            requests.post(url='',data=data)
        except:
            return {'code':501,'message':'数据库读取出错'}

    return dictRe


class sipbinding(tornado.web.RequestHandler):
    async def get(self):
        try:
            Bnumber = self.get_arguments('telB')[0]
            client_id = self.get_arguments('Cor_id')[0]
            con = pymysql.connect(

                host='39.105.115.68',

                port=3306,

                user='yanfa',

                password='hmbkhcm9FSsDvv2P',

                db='zbtx_privacy',

                charset='utf8'

            )
            cur = con.cursor()
            cur.execute('select money from zb_account where identify="{}"'.format(client_id))
            money = cur.fetchall()
            cur.close()
            con.close()
            print(money[0][0])
            if money[0][0] > 500:
                balance = 0
            elif 0<money[0][0]<=100:
                balance = 1
            else:
                data = {'alarm_level': '次要', 'alarm_types': '用户余额不足', 'alarm_object': client_id, 'alarm_value': '',
                        'alarm_threshold': '', 'alarm_info': ''}
                # requests.post(url='',data=data)
                self.write({'code': 501, 'message': '用户余额不足'})
                return 
        except:
            self.write({'code':501,'message':'查询用户余额出错'})
            return
        try:
            client_message = r.hgetall('{}'.format(client_id))
            print(client_message)
            x = client_message['gateway_group']
            groupXname = client_message['bind_xpool']
            appkey = client_message['Appkey']
            bind_type = client_message['bind_type']  # 从redis用户表中提取各种有用信息
            acc_max_limit = client_message['acc_max_limit']
            secret = client_message['secret']
            plat = client_message['plat']
            ClientConcurrency(acc_max_limit)
            sipgroup = r.zrange('{}'.format(x), 0, -1, withscores=True)
            sipcount = -1
            sip = (sipgroup[sipcount][0])
            try:
                while True:  # 根据权重来确定sip中继
                    if int((r.hget(sip, 'limit'))) > 0:
                        break
                    else:
                        sipcount = sipcount - 1
                        sip = (sipgroup[sipcount][0])
            except:
                data = {'alarm_level':'次要','alarm_types':'网关群组并发量已满','alarm_object':sipgroup,'alarm_value':'',
                        'alarm_threshold':'','alarm_info':''}
                # requests.post(url='',data=data)
                self.write({'code': 501, 'message': '网关群组并发已满'})
                return
            concurrency = int(r.hget(sip, 'limit')) - 1
            groupAname = r.hget(sip, 'affiliation')
            A = r.get(groupAname)  # 从A池中平均取出A号码
            Adict = json.loads(A)
            Apule = sorted(Adict.items(), key=operator.itemgetter(1))
            Anumber = Apule[-1][0]
            limita = Apule[-1][-1]
            if limita <= 0:
                data = {'alarm_level': '次要', 'alarm_types': 'A池并发量已满', 'alarm_object': groupAname, 'alarm_value': '',
                        'alarm_threshold': '', 'alarm_info': ''}
            # requests.post(url='', data=data)
                self.write({'code': 501, 'message': 'A池并发已满'})
                return
            Adict[Anumber] = limita - 1
            Astr = json.dumps(Adict)
            X = r.get('{}'.format(groupXname))  # 从X池中平均取出X号码
            Xdict = json.loads(X)
            Xpule = sorted(Xdict.items(), key=operator.itemgetter(1))
            Xnumber = Xpule[-1][0]
            limitx = Xpule[-1][-1]
            if limitx <= 0:
                data = {'alarm_level': '次要', 'alarm_types': 'X池并发量已满', 'alarm_object': groupXname, 'alarm_value': '',
                        'alarm_threshold': '', 'alarm_info': ''}
                # requests.post(url='', data=data)
                self.write({'code': 501, 'message': 'X池并发已满'})
                return
        except Exception as e:
            print(e)
            self.write({'code': 501, 'message': '数据库读取出错'})
            return
        dictRe = PhoneBindInter(client_id, appkey, Anumber, Xnumber, Bnumber, sip, x, groupXname, bind_type,secret,Xdict,balance)
        dictRe = {'code':0,'message':'成功','data':{}}
        dictRe['data']['telX'] = '{}'.format(Xnumber)
        dictRe['data']['sip'] = '{}'.format(sip)  # sip中继的唯一标识
        dictRe['data']['sip_group'] = '{}'.format(x)  # 网关群组
        dictRe['data']['Xpool'] = '{}'.format(groupXname)  # X号所在池
        dictRe['data']['call_type'] = 0  # 呼叫类型
        dictRe['data']['appkey'] = '{}'.format(appkey)  # Appkey
        dictRe['data']['bind_type'] = '{}'.format(bind_type)  # 绑定类型
        dictRe['data']['Anumber'] = '{}'.format(Anumber)  # A号码
        dictRe['data']['client_id'] = '{}'.format(client_id)  # 客户唯一标识
        dictRe['data']['secret'] = '{}'.format(secret)
        dictRe['data']['plat'] = '{}'.format(plat)
        # dictRe['data']['balance'] = '{}'.format(balance)
        print(dictRe)
        if dictRe["code"] == 0:
            Xdict[Xnumber] = limitx - 1
            Xstr = json.dumps(Xdict)
            try:
                r.hset(sip, 'limit', concurrency)  # 对AX，sip的时时并发量进行更改
                r.set(groupAname, Astr)
                r.set(groupXname, Xstr)
                r.hset(client_id, 'acc_max_limit', int(acc_max_limit) - 1)
            except:
                self.write({'code': 501, 'message': '数据库读取出错'})
                return
        self.write(dictRe)


application = tornado.web.Application([
    (r"/bind/v2/axb/", sipbinding)

])

if __name__ == '__main__':
    r = redis.Redis(host='r-2zed2mpeqshup0fiaqpd.redis.rds.aliyuncs.com', db=0, password='hqMsezH3ZDPkFuC8',
                    port=6379, decode_responses=True)
    application.listen(7778)
    tornado.ioloop.IOLoop.instance().start()
