from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from RankingList.mysql_connect import mysql_connect_v1
# Create your views here.
class UploadScores(View):#上传分数
    def post(self,request):
        username = request.POST.get('username')#接收用户名
        scores = request.POST.get('scores')#接收用户分数
        scores = int(scores)
        con = mysql_connect_v1()
        if con == 500:#数据库连接
            return JsonResponse({'code':501,'message':'数据库连接出错'})
        cur = con.cursor()
        try:
            exist = cur.execute('select * from game_ranking where username="{}"'.format(username))#查询该用户有没有提交分数
            if exist == 0:#如果没有提交过，将这次分数提交
                cur.execute('INSERT INTO game_ranking value (0,"{}",{})'.format(username,scores))
                con.commit()
            else:#又提交过覆盖之前提交的分数
                cur.execute('UPDATE game_ranking SET score={} where username="{}"'.format(scores,username))
                con.commit()
        except:
            return JsonResponse({'code':501,'message':'数据库操作出错'})
        cur.close()
        con.close()
        return JsonResponse({'code':200,'message':'分数上传成功'})

class InquireRanking(View):#查看排行榜
    def get(self,request):
        head = int(request.GET.get('head'))
        tail = int(request.GET.get('tail'))
        #接收任何名次段，例如可以查询排名20~30的表格
        interval = tail - head
        con = mysql_connect_v1()
        if con == 500:#数据库连接
            return JsonResponse({'code': 501, 'message': '数据库连接出错'})
        cur = con.cursor()
        try:
            Response = {}
            cur.execute('SELECT * FROM  game_ranking  ORDER BY score DESC LIMIT {},{}'.format(head,interval))
            #按照分数从大到小把任何名次段查询出来
            paihang = cur.fetchall()
            for userranking in paihang:
                head += 1
                Response[head] = {"user":"{}".format(userranking[1]),"score":"{}".format(userranking[2])}#结构化返回
        except Exception as e:
            print(e)
            return JsonResponse({'code':501,'message':'数据库操作出错'})
        return JsonResponse(Response)
    """
    返回结果示例
    {
    "1": {
        "user": "客户端10",
        "score": "1111111"
    },
    "2": {
        "user": "客户端7",
        "score": "10006"
    },
    "3": {
        "user": "客户端6",
        "score": "10005"
    },
    "4": {
        "user": "客户端5",
        "score": "10004"
    },
    "5": {
        "user": "客户端4",
        "score": "10003"
    },
    "6": {
        "user": "客户端2",
        "score": "10002"
    },
    "7": {
        "user": "客户端3",
        "score": "10002"
    },
    "8": {
        "user": "客户端1",
        "score": "10000"
    },
    "9": {
        "user": "客户端8",
        "score": "9999"
    },
    "10": {
        "user": "客户端9",
        "score": "123"
    }
}
    """