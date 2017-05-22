/*
 * Copyright 2017 By_syk
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
-- 酷安用户表
CREATE TABLE user(
  id INT PRIMARY KEY,
  name VARCHAR(64),
  fan INT DEFAULT 0,
  feed INT DEFAULT 0,
  app INT DEFAULT 0,
  find INT DEFAULT 0,
  time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
*/

var express = require('express'); // npm install express
//var bodyParser = require('body-parser'); // npm install body-parser
var log4js = require('log4js'); // npm install log4js
var query = require('./mysql');
var utils = require('./utils');

// 服务运行目标端口
var serverPort = 8081;

var app = express();

// 解析 POST application/x-www-form-urlencoded
//app.use(bodyParser.urlencoded({ extended: false }));
// 解析 POST JSON
//app.use(bodyParser.json({ limit: '1mb' }));

// 支持静态文件
app.use(express.static('public'));

// console log is loaded by default, so you won't normally need to do this
//log4js.loadAppender('console');
log4js.loadAppender('file');
//log4js.addAppender(log4js.appenders.console());
log4js.addAppender(log4js.appenders.file('logs/coolapk' + serverPort + '.log'), 'coolapkuserstats' + serverPort);
var logger = log4js.getLogger('coolapkuserstats' + serverPort);
logger.setLevel('INFO'); // TRACE, DEBUG, INFO, WARN, ERROR, FATAL

// 用到的SQL命令
var sqlCmds = {
  count: 'SELECT COUNT(*) AS sum FROM user',
  queryById: 'SELECT * FROM (SELECT id, name, fan, feed, app, find, DATE_FORMAT(time, \'%Y-%m-%d %H:%i:%s\') AS time, FLOOR(fan * 0.5 + feed * 0.4 + app * 0.08 + find * 0.02) AS score, @rownum:=@rownum+1 AS pos FROM user, (SELECT @rownum:=0) temp WHERE fan > 0 OR feed > 0 OR app > 0 OR find > 0 ORDER BY score DESC) stats WHERE id = ?',
  queryByName: 'SELECT * FROM (SELECT id, name, fan, feed, app, find, DATE_FORMAT(time, \'%Y-%m-%d %H:%i:%s\') AS time, FLOOR(fan * 0.5 + feed * 0.4 + app * 0.08 + find * 0.02) AS score, @rownum:=@rownum+1 AS pos FROM user, (SELECT @rownum:=0) temp WHERE fan > 0 OR feed > 0 OR app > 0 OR find > 0 ORDER BY score DESC) stats WHERE name = ?'
};


// ====================================== API BLOCK START ======================================= //


// 接口：按用户ID或用户名查询评分情况
app.get('/query/:keyword', function(req, res) {
  var keyword = req.params.keyword;
  logger.info('GET /query/' + keyword + ' ' + utils.getClientIp(req));
  var sql;
  if (/^\d+$/.test(keyword)) {
    var uid = parseInt(keyword);
    if (uid <= 10000 || uid >= 1000000) {
      res.jsonp(utils.getResRes(2));
      return;
    }
    sql = sqlCmds.queryById;
  } else {
    sql = sqlCmds.queryByName;
  }
  var sqlOptions = [keyword];
  query(sql, sqlOptions, function(err, rows) {
    if (err) {
      logger.warn(err);
      res.jsonp(utils.getResRes(3));
      return;
    }
    if (rows.length == 0) {
      res.jsonp(utils.getResRes(0, undefined, {}));
    } else {
      res.jsonp(utils.getResRes(0, undefined, rows[0]));
    }
  });
});

// 接口：获取用户数
app.get('/usernum', function(req, res) {
  var keyword = req.params.keyword;
  logger.info('GET /usernum ' + utils.getClientIp(req));
  query(sqlCmds.count, [], function(err, rows) {
    if (err) {
      logger.warn(err);
      res.jsonp(utils.getResRes(3));
      return;
    }
    res.jsonp(utils.getResRes(0, undefined, rows[0].sum));
  });
});

// 接口：看门狗
app.get('/watchdog', function(req, res) {
  logger.info('GET /watchdog');
  
  res.jsonp(utils.getResRes(0, undefined, {
    port: serverPort,
    time: Date.now()
  }));
});


// ======================================= API BLOCK END ======================================== //


// ====================================== PAGE BLOCK START ====================================== //


app.get('/', function(req, res) {
  res.redirect('/page/query');
});

// 页面：查询
app.get('/page/query', function(req, res) {
  logger.info('GET /page/query');
  res.sendFile(__dirname + '/pages/query.htm');
});


// ======================================= PAGE BLOCK END ======================================= //


var server = app.listen(serverPort, function() {
  var host = server.address().address;
  var port = server.address().port;

  if (host == '::') {
    host = 'localhost';
  }
  
  logger.info('http://%s:%s/', host, port);
});

logger.info('CoolapkUserStatsQueryServer is running...');