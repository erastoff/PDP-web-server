## PDP-web-server (Python Developer Professional Course)

### The fifth homework:
##### Thread pool web-server
<u>The terms of the task are given in the file homework.pdf.</u>
<br></br>



~/PycharmProjects/PDP-web-server$ ab -n 50000 -c 100 -r http://localhost:8080/ \
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>\
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/ \
Licensed to The Apache Software Foundation, http://www.apache.org/ 

Benchmarking localhost (be patient) \
Completed 5000 requests \
Completed 10000 requests \
Completed 15000 requests \
Completed 20000 requests \
Completed 25000 requests \
Completed 30000 requests \
Completed 35000 requests \
Completed 40000 requests \
Completed 45000 requests \
Completed 50000 requests \
Finished 50000 requests 

| Attribute             | Value                        |
|-----------------------|------------------------------|
| Server Software       | OTUServer                    |
| Server Hostname       | localhost                    |
| Server Port           | 8080                         |
| Document Path         | /                            |
| Document Length       | 0 bytes                      |
| Concurrency Level     | 100                          |
| Time taken for tests  | 16.676 seconds               |
| Complete requests     | 50000                        |
| Failed requests       | 0                            |
| Non-2xx responses     | 50000                        |
| Total transferred     | 7500000 bytes                |
| HTML transferred      | 0 bytes                      |
| Requests per second   | 2998.35 [#/sec] (mean)       |
| Time per request      | 33.352 [ms] (mean)           |
| Time per request      | 0.334 [ms] (mean, across all concurrent requests) |
| Transfer rate         | 439.21 [Kbytes/sec] received|


| Connection Times (ms) | min | mean[+/-sd] | median | max |
|-----------------------|-----|-------------|--------|-----|
| Connect:              | 0   | 2           | 39.1   | 1028|
| Processing:           | 4   | 32          | 11.5   | 447 |
| Waiting:              | 4   | 32          | 11.5   | 447 |
| Total:                | 9   | 33          | 44.6   | 1473|


Percentage of the requests served within a certain time (ms) \
  50%     32 \
  66%     32 \
  75%     33 \
  80%     34 \
  90%     35 \
  95%     37 \
  98%     42 \
  99%     68 \
 100%   1473 (longest request)