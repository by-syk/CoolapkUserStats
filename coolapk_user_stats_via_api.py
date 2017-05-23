import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib import request
import json
import sys
import time

# 初始化数据库连接
engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/coolapk'
                                  + '?charset=utf8', encoding='utf-8')

dbSession = sessionmaker(bind=engine)

# 创建对象基类
base = declarative_base()


class User2(base):
    # 定义 User2 类（对应 user2 表）
    # CREATE DATABASE coolapk;
    # CREATE TABLE user2(
    #     uid INT PRIMARY KEY,
    #     username VARCHAR(64),
    #     gender TINYINT(1) DEFAULT -1,
    #     province VARCHAR(32),
    #     city VARCHAR(32),
    #     developer TINYINT(1) DEFAULT 0,
    #     fan INT DEFAULT 0,
    #     follow INT DEFAULT 0,
    #     feed INT DEFAULT 0,
    #     app_dev INT DEFAULT 0,
    #     app_follow INT DEFAULT 0,
    #     app_rating INT DEFAULT 0,
    #     app_find INT DEFAULT 0,
    #     album INT DEFAULT 0,
    #     flag_black TINYINT(1) DEFAULT 0,
    #     flag_ignore TINYINT(1) DEFAULT 0,
    #     flag_limit TINYINT(1) DEFAULT 0,
    #     time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);

    # 表名
    __tablename__ = 'user2'

    # UID
    uid = sqlalchemy.Column('uid', sqlalchemy.INT, primary_key=True)
    # 用户名
    username = sqlalchemy.Column('username', sqlalchemy.String(64))
    # 性别（-1：未设定，0：女，1：男）
    gender = sqlalchemy.Column('gender', sqlalchemy.SMALLINT)
    # 省份
    province = sqlalchemy.Column('province', sqlalchemy.String(32))
    # 城市
    city = sqlalchemy.Column('city', sqlalchemy.String(32))
    # 是否为开发者
    is_developer = sqlalchemy.Column('developer', sqlalchemy.SMALLINT)
    # 粉丝数
    fan_num = sqlalchemy.Column('fan', sqlalchemy.INT, default=0)
    # 关注用户数
    follow_num = sqlalchemy.Column('follow', sqlalchemy.INT, default=0)
    # 动态数
    feed_num = sqlalchemy.Column('feed', sqlalchemy.INT, default=0)
    # 开发APP数（仅开发者）
    app_dev_num = sqlalchemy.Column('app_dev', sqlalchemy.INT, default=0)
    # 关注APP数
    app_follow_num = sqlalchemy.Column('app_follow', sqlalchemy.INT, default=0)
    # 评分APP数
    app_rating_num = sqlalchemy.Column('app_rating', sqlalchemy.INT, default=0)
    # 发现APP数
    app_find_num = sqlalchemy.Column('app_find', sqlalchemy.INT, default=0)
    # 应用集数
    album_num = sqlalchemy.Column('album', sqlalchemy.INT, default=0)
    # 黑名单标记
    flag_black = sqlalchemy.Column('flag_black', sqlalchemy.SMALLINT)
    # 全网屏蔽标记
    flag_ignore = sqlalchemy.Column('flag_ignore', sqlalchemy.SMALLINT)
    # 禁言标记
    flag_limit = sqlalchemy.Column('flag_limit', sqlalchemy.SMALLINT)
    # 数据获取时间
    # time = sqlalchemy.Column('time', sqlalchemy.TIMESTAMP)


def run(id_list, token):
    session = dbSession()

    time_start = time.time()
    ok_num = 0
    data_size = 0

    for i, user_id in enumerate(id_list):
        try:
            url = 'https://api.coolapk.com/v6/user/profile?uid=%d' % user_id
            headers = {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Z2 Plus Build/N2G47O) +CoolMarket/6.10.6',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Sdk-Int': '25',
                'X-Sdk-Locale': 'en-US',
                'X-App-Id': 'coolmarket',
                'X-App-Token': token,  # 有效期为5min
                'X-App-Version': '6.10.6',
                'X-App-Code': '1608291',
            }
            req = request.Request(url=url, headers=headers)
            res = request.urlopen(req)
            data = res.read()
            data_size += len(data)
            data = data.decode('utf-8')
        except Exception as e:
            # print(e.reason)
            print(e)
            break

        jo = json.loads(data)
        if 'data' not in jo:
            if 'status' in jo:
                if jo['status'] == 1004:  # token 过期
                    print(jo)
                    break
                elif jo['status'] == -10001:  # 无权访问，如 10001 admin
                    print_status(time_start, i + 1, len(id_list), '')
                    continue
                elif jo['status'] == -1:  # 用户不存在
                    print_status(time_start, i + 1, len(id_list), '')
                    continue
                else:
                    print(jo)
                    break
            else:
                print(jo)
                break
        jo_data = jo['data']

        user2 = User2(uid=user_id)
        user2.username = jo_data['username']
        user2.username = jo_data['username']
        user2.gender = jo_data['gender']
        user2.province = jo_data['province']
        user2.city = jo_data['city']
        user2.is_developer = jo_data['isDeveloper']
        user2.fan_num = jo_data['fans']
        user2.follow_num = jo_data['follow']
        user2.feed_num = jo_data['feed']
        user2.app_dev_num = jo_data['apkDevNum']
        user2.app_follow_num = jo_data['apkFollowNum']
        user2.app_rating_num = jo_data['apkRatingNum']
        user2.app_find_num = jo_data['discoveryNum']
        user2.album_num = jo_data['albumNum']
        user2.flag_black = jo_data['isBlackList']
        user2.flag_ignore = jo_data['isIgnoreList']
        user2.flag_limit = jo_data['isLimitList']

        ok_num += 1

        # session.add(user2)
        session.merge(user2)
        if ok_num % 100 == 99:
            session.commit()

        print_status(time_start, i + 1, len(id_list), '%d - @%s' % (user_id, user2.username))

    session.commit()
    session.close()

    print('All done! %.0fs %d/%d %.0fkb'
          % (time.time() - time_start, ok_num, len(id_list), data_size / 1024))


def print_status(time_start, progress, total, content):
    if progress % 100 == 0 or progress == max:
        print('%.0fs\t%d/%d:\t%s'
              % (time.time() - time_start, progress, total, content))
    else:
        sys.stdout.writelines('%.0fs\t%d/%d:\t%s                \r'
                              % (time.time() - time_start, progress, total, content))
        # sys.stdout.flush()


if __name__ == '__main__':
    # run(range(10000, 10100, ''))
    args = sys.argv
    if len(args) == 4:
        run(range(int(args[1]), int(args[1]) + int(args[2])), args[3])
    else:
        start_id = int(input('Start UID: '))
        num = int(input('Num: '))
        token = input('Token: ')
        run(range(start_id, start_id + num), token)
