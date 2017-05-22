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

// 解析客户端IP
exports.getClientIp = function(req) {
  return req.headers['x-forwarded-for']
    || req.connection.remoteAddress
    || req.socket.remoteAddress
    || req.connection.socket.remoteAddress;
};

// 拼装返回JSON数据
exports.getResRes = function(status, msg, result) {
  if (msg == undefined) {
    if (status == 0) {
      msg = 'success';
    } else if (status == 1) {
      msg = 'error';
    } else if (status == 2) {
      msg = 'invalid_req';
    } else if (status == 3) {
      msg = 'sql_error';
    } else if (status == 4) {
      msg = 'no_such';
    }
  }
  var resJson = {
    status: status,
    msg: msg
  };
  if (result != undefined) {
    resJson.result = result;
  }
  return resJson;
}