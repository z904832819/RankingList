import pymysql
def mysql_connect_v1():#数据库连接
    try:
        con = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='',
            db='paihangbang',
            charset='utf8')
    except:
        return 500
    return con
