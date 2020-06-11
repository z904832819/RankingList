from django.conf.urls import url
from . import views

urlpatterns = [
    #上传分数
    url(r'uploadscores/$',views.UploadScores.as_view()),
    #查看排行榜
    url(r'InquireRanking/$',views.InquireRanking.as_view())

]
