# 酷安用户数据爬虫案例


### 背景

「[酷安](http://www.coolapk.com)」是一个成长中的优秀国内应用社区。截至目前（201705），注册用户数在100万左右（当然，活跃用户并没有这么多）。
为了满足自己了解酷安粉丝数排名情况的好奇心，以及学习实践 Python，于是写了这个小玩意儿。

![酷安](art/coolapk_463675_web.png)

![酷安](art/coolapk_463675_app.png)

在此之前，已有酷友 [@unnamed5719](http://www.coolapk.com/u/547008) 基于 Python 实现对酷安全网用户的爬取分析，同时也开源了他的代码以及分析结果。（去查看：[酷安大数据（伪）](https://github.com/unnamed5719/coolapk-users)）
而这个小项目也是在其启发之下完成，感谢 @unnamed5719！


### 分析

每一位注册酷安的用户会获得一个唯一的ID，这些ID从`10001`开始依次递增。

如何获取每个用户的数据呢？有两个方案：
1. 解析酷安用户网页

  `http://coolapk.com/u/{uid}`

  为了节省流量，有一个更佳的选择：`http://coolapk.com/u/{uid}/album`

  ![HTML](art/coolapk_463675_web_html.png)

2. 调用酷安APP的API

  `https://api.coolapk.com/v6/user/profile?uid={uid}`

  ![API](art/coolapk_463675_app_api.png)

比较：
| . | 方案一 | 方案二 |
| :---- | :---- | :---- |
| 速度 | 快 | 慢 |
| 信息量 | 少 | 多 |
| 其他 |  | 接口需要的`X-App-Token`值难于构造 |

这两个方案，均已实现。以下以方案一为例。


### 准备

##### 运行系统：Ubuntu 14

##### 数据库：MySQL 5.5

```
apt-get update
apt-get upgrade
apt-get install mysql-server
apt-get install mysql-client
```

```
CREATE DATABASE coolapk;
USE coolapk;
CREATE TABLE user(
    id INT PRIMARY KEY,
    name VARCHAR(64),
    fan INT DEFAULT 0,
    feed INT DEFAULT 0,
    app INT DEFAULT 0,
    find INT DEFAULT 0,
    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

##### 开发语言：Python 3

```
apt-get install python3
apt-get install python3-pip
pip3 install pymysql
pip3 install sqlalchemy
```


### GO！

以每次处理10000用户的节奏，进行100次执行。

```
python3 coolapk_user_stats_via_htm.py 10000 10000
python3 coolapk_user_stats_via_htm.py 20000 10000
python3 coolapk_user_stats_via_htm.py 30000 10000
...
```

![过程](art/run.png)

以腾讯家的云服务器（配置：单核/1G/1Mbps）为例，效率状况为每秒平均处理`10.2`个用户。
按酷安百万用户计，单机单线程大概需耗时`1634`min（`27`h）。如果使用多台机器同时跑，可在数小时内完成。


### 结果

TODO


### License

    Copyright 2017 By_syk

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


*Copyright &#169; 2017 By_syk. All rights reserved.*