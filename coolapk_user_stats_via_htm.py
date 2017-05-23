import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib import request
import re
import sys
import time

# 初始化数据库连接
engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/coolapk'
                                  + '?charset=utf8', encoding='utf-8')

dbSession = sessionmaker(bind=engine)

# 创建对象基类
base = declarative_base()


class User(base):
    # 定义 User 类（对应 user 表）
    # CREATE DATABASE coolapk;
    # CREATE TABLE user(
    #     id INT PRIMARY KEY,
    #     name VARCHAR(64),
    #     fan INT DEFAULT 0,
    #     feed INT DEFAULT 0,
    #     app INT DEFAULT 0,
    #     find INT DEFAULT 0,
    #     time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);

    # 表名
    __tablename__ = 'user'

    # UID
    id = sqlalchemy.Column(sqlalchemy.INT, primary_key=True)
    # 用户名
    name = sqlalchemy.Column(sqlalchemy.String(64))
    # 粉丝数
    fan = sqlalchemy.Column(sqlalchemy.INT, default=0)
    # 动态数
    feed = sqlalchemy.Column(sqlalchemy.INT, default=0)
    # 关注APP数
    app = sqlalchemy.Column(sqlalchemy.INT, default=0)
    # 发现APP数
    find = sqlalchemy.Column(sqlalchemy.INT, default=0)
    # 数据获取时间
    # time = sqlalchemy.Column(sqlalchemy.TIMESTAMP)


def run(id_list):
    session = dbSession()

    time_start = time.time()
    ok_num = 0
    page_size = 0

    for i, user_id in enumerate(id_list):
        try:
            res = request.urlopen('http://coolapk.com/u/%d/album' % user_id)
            page = res.read()
            page_size += len(page)
            page = page.decode('utf-8')
        except UnicodeDecodeError:
            # 有无法解析的Unicode字符，只有跳过它
            continue
        except request.HTTPError as e:
            if e.code == 400:
                print_status(time_start, i + 1, len(id_list), '')
                continue
            else:
                # print(e.reason)
                print(e)
                break
        except Exception as e:
            print(e)
            break

        user = User(id=user_id)

        search = re.search(r'class="username">(.+?)</a></h4>', page)
        if search:
            user.name = search.group(1)
        search = re.search(r'<strong>(\d+)</strong>好友关注', page)
        if search:
            user.fan = search.group(1)
        search = re.search(r'<strong>(\d+)</strong>动态', page)
        if search:
            user.feed = search.group(1)
        search = re.search(r'<strong>(\d+)</strong>应用关注', page)
        if search:
            user.app = search.group(1)
        search = re.search(r'<strong>(\d+)</strong>发现', page)
        if search:
            user.find = search.group(1)

        ok_num += 1

        # session.add(user)
        session.merge(user)
        if ok_num % 100 == 99:
            session.commit()

        print_status(time_start, i + 1, len(id_list), '%d - @%s' % (user_id, user.name))

    session.commit()
    session.close()

    print('All done! %.0fs %d/%d %.0fkb'
          % (time.time() - time_start, ok_num, len(id_list), page_size / 1024))


def print_status(time_start, progress, total, content):
    if progress % 100 == 0 or progress == max:
        print('%.0fs\t%d/%d:\t%s'
              % (time.time() - time_start, progress, total, content))
    else:
        sys.stdout.writelines('%.0fs\t%d/%d:\t%s                \r'
                              % (time.time() - time_start, progress, total, content))
        # sys.stdout.flush()


if __name__ == '__main__':
    # run(range(10000, 10002))
    args = sys.argv
    if len(args) == 3:
        run(range(int(args[1]), int(args[1]) + int(args[2])))
    else:
        start_id = int(input('Start UID: '))
        num = int(input('Num: '))
        run(range(start_id, start_id + num))
