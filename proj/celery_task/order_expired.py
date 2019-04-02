import pymysql

from .celery import cel


@cel.task(name='order_expired.order_auto_expired')
def order_auto_expired(orderlist):
    '''

    :param orderlist: [order_id1,order_id2]
    :return:
    '''
    conn = pymysql.connect(
        host='172.96.198.74',
        user='yuanzhu',
        password='123456',
        database='hy',
        charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    for i in orderlist:
        sql = "select * from userorder where id=%s"
        cursor.execute(sql, [i])
        dic = cursor.fetchone()
        if dic['status'] == '0':
            print('1')
            sql = "update userorder set status=1 where id=%s"
            cursor.execute(sql, [i])
            conn.commit()
        else:
            continue
    cursor.close()
    conn.close()
    return 'mission order_auto_expired success'
