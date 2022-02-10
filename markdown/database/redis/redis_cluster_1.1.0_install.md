---
title: redis-cluster: 1.1.0 安装
date: 2019-12-23 10:06:00
categories: database/redis
tags: [database,redis]
---

### redis-cluster简介
redis-cluster提供了一种方式，在多个redis节点中进行数据分片。同时，也在分区期间提供了一定程度的高可用性，当某个节点无法通信时，可以继续执行读写操作。

#### 1) 在实际应用中，使用redis-cluster可以得到如下特性
- 自动在多个节点之间分割数据集
- 当一部分节点出现故障或无法与其余集群通信时，继续执行操作

#### 2) redis-cluster中的端口
每一个redis节点需要监听两个端口，其中一个端口是用于提供客户端服务，例如6379，另外一个端口是给前一个端口加上10000，例如16379.第二个大端口号用于集群总线通信的，在上面节点与节点之间使用二进制协议进行通信。集群总线被节点用于失败检测、配置更新、failover授权和其他集群功能。
- 6379(默认)，需要给所有客户端开放访问，并且给所有集群节点开放访问(用于key的迁移)
- 16379(默认)，需要开放给所有集群节点
集群总线使用二进制协议，这样更适用于降低带宽和处理时间。

#### 3) redis-cluster和docker
redis-cluster目前不支持nat网络或端口重定向过的网络。而docker恰好使用了端口转发的方式，来实现了同一台主机上的多个容器可以在容器内部使用同一个端口的方式。所以，如果要使用docker来部署redis-cluster，我们必须给容器使用host网络的方式。

#### 4) redis-cluster数据分片
Redis Cluster不使用一致的哈希，而是使用一种不同形式的分片，其中每个键从概念上讲都是我们称为哈希槽的一部分。每一个redis-cluster中有16384个哈希槽，计算给定密钥的哈希槽是多少，我们只需对密钥的CRC16取模16384。

每一个redis节点负责哈希槽的一个子区间，例如我们有一个3节点的redis-cluster，那么：
- 节点A包含从0到5500的哈希槽。
- 节点B包含从5501到11000的哈希槽。
- 节点C包含从11001到16383的哈希槽。
这允许我们方便的增删节点，如果我们增加一个节点D，只需要从ABC中挪一部分哈希槽到D中即可。类似的，如果我们要删除节点A，我们只需要把A中的哈希槽挪动到
BC中即可。当节点A为空时，我可以将其从群集中完全删除。

因为将哈希槽从一个节点移动到另一个节点不需要停止操作，所以添加和删除节点或更改节点持有的哈希槽的百分比不需要任何停机时间。

redis-cluster支持针对多个key的批量操作，只需要目标keys存在在同一个哈希槽中。要达成将多个keys放在同一个哈希槽中，可以使用hash tags来手动分类(关键字就是`{}`，具体文档可以谷歌)。

#### 5) redis-cluster主从模型
当redis-cluster部分子节点无法和其他大部分节点通信或者发生错误时使整个集群依然可用，redis-cluster使用了主从模型，使每一个哈希槽存在多个副本。

在我们举得例子中，三个节点ABC，假设B发生了问题，那么5501-11000区间的哈希槽将无法被访问，但是因为我们给B提供了一个从节点B1，那么A和C将B1提升为主节点，此时就可以继续对5501-11000区间的哈希槽提供访问和操作。

但是需要注意的是，如果B和B1同时发生错误，那么整个集群会发生失败

#### 6) redis-cluster的一致性保证
redis-cluster不保证强一致性。在实际使用中，这意味着在某些特定条件下，redis-cluster会丢失丢失系统已确认给客户端的写入。

Redis Cluster可能会丢失写入的第一个原因是因为它使用异步复制。
- 客户端写入数据到B
- B回复给客户端写入完成
- B将这个写操作通告给B的从节点
如你所见，B不会等待从节点的确认，而是直接回复客户端写入完成，因为不这样做的话会对Redis造成极大的延迟损失。那么可想而知，如果B在告知从节点有改动之前挂掉了，在这个过程中就会造成客户端写入过的数据丢失。

基本上，我们需要在性能和一致性之间进行权衡。当然，如果你希望改变这种默认行为，而使用同步复制的话，可以使用WAIT命令。这样可以大大降低写操作的丢失，但是依然没有达到强一致性。在更复杂的故障情况下，总是有可能将无法接收写操作的从设备选为主设备。

还有一种值得注意的情况，Redis Cluster将丢失写操作，这种情况发生在网络分区期间，在该分区中，客户端与少数实例（至少包括主实例）隔离。

假设我们有三主三从ABCA1B1C1，然后有个客户端Z1，客户端Z1和B，被网络分区隔离出来，然后ACA1B1C1是在另外一个网络分区。Z1依然可以向B中写入，如果在很短的时间内集群恢复，然而时间已经长到足够B1被提升为主节点。此时Z1写入到B的数据会丢失。

请注意，Z1将能够发送到B的最大写入量有一个最大窗口，如果已经有足够的时间让分区的多数方选举一个从属方为主，则少数方中的每个主节点将停止接受写入。该时间量是Redis Cluster的一个非常重要的配置指令，称为node timeout。当node timeout超时后，主节点会进入失败状态，然后被其他从节点代替。类似地，在没有主节点能够感知大多数其他主节点的节点超时之后，它进入错误状态并停止接受写入。

#### 7) redis-cluster配置
- cluster-enabled <yes/no>，启用集群模式
- cluster-config-file <filename>，集群配置文件名称，无法手动编辑，会自动生成。此配置文件用于保存集群状态
- cluster-node-timeout <milliseconds>，Redis群集节点不可用的、不被认为是失败的最长时间。如果主节点无法访问的时间超过指定的时间长度，则它的从节点将对其进行故障转移。此参数控制Redis Cluster中的其他重要事项。值得注意的是，在指定的时间内无法到达大多数主节点的每个节点都将停止接受查询。
- cluster-slave-validity-factor <factor>，如果设定为0，slave节点会一直尝试去故障转移主节点，而不考虑master和slave断开连接的时间。如果设定的值大于0，那么slave尝试故障转移主节点的最大时间区间为，设定的值乘以node timeout，超过此时间，slave将不再尝试故障转移主节点。例如node timeout时间为5s，设定此因子为10，那么50s内，slave会尝试故障转移master，而超过50s，slave将停止尝试故障转移master。值得注意的是，如果没有slave可以成功的故障转移master，那么整个集群将不可用，直到故障的master重新加入集群。
- cluster-migration-barrier <count>，一个主站将保持连接的最小数量的从站，以便另一个从站迁移到不再被任何从站覆盖的主站。
- cluster-require-full-coverage <yes/no>，如果将其设置为“是”（默认情况下为默认值），则在任何节点未覆盖一定比例的密钥空间的情况下，群集将停止接受写入。如果该选项设置为no，即使仅可以处理有关密钥子集的请求，群集仍将提供查询。 创建和使用Redis集群

### docker本机搭建redis-cluster实践
``` bash
mkdir redis-cluster-test
cd redis-cluster-test

# 创建配置文件
# 基本上就是默认配置，然后修改了以下内容
# - port 7000（对应的端口组合的路径啥的一起改了）
# - protect-mode no
# - bind 0.0.0.0
# - maxmemory 1024mb
# - appendonly yes
# - cluster-enabled yes
# - cluster-config-file nodes-7000.conf
# - cluster-node-timeout 5000
# - cluster-replica-validity-factor 10
cat << EOF > 7000.conf
bind 0.0.0.0
protected-mode no
port 7000
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_7000.pid
loglevel notice
logfile ""
databases 16
always-show-logo yes
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
replica-priority 100
requirepass myredis123
maxmemory 1024mb
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 5000
cluster-replica-validity-factor 10
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
EOF
# 其他的7001.conf,7002.conf,7003.conf,7004.conf,7005.conf保持配置一致，然后端口改掉即可

# 创建docker-compose文件
# 重点注意：
# - 网络模式使用host
# - 生产环境中可以把rdb的目录(/data)给映射出来
cat << EOF > redis-cluster-test.yml
version: '3'
services:
  redis-7000:
    container_name: redis-7000
    image: redis:5
    network_mode: "host"
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - ./7000.conf:/usr/local/etc/redis/redis.conf
  redis-7001:
    container_name: redis-7001
    image: redis:5
    network_mode: "host"
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - ./7001.conf:/usr/local/etc/redis/redis.conf
  redis-7002:
    container_name: redis-7002
    image: redis:5
    network_mode: "host"
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - ./7002.conf:/usr/local/etc/redis/redis.conf
  redis-7003:
    container_name: redis-7003
    image: redis:5
    network_mode: "host"
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - ./7003.conf:/usr/local/etc/redis/redis.conf
  redis-7004:
    container_name: redis-7004
    image: redis:5
    network_mode: "host"
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - ./7004.conf:/usr/local/etc/redis/redis.conf
  redis-7005:
    container_name: redis-7005
    image: redis:5
    network_mode: "host"
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - ./7005.conf:/usr/local/etc/redis/redis.conf
EOF

# 启动redis-cluster集群
docker-compose -f redis-cluster-test.yml up -d

# 因为是host网络启动，会直接占用宿主机端口
netstat -lnpt |grep redis
tcp        0      0 0.0.0.0:7000            0.0.0.0:*               LISTEN      9090/redis-server 0 
tcp        0      0 0.0.0.0:7001            0.0.0.0:*               LISTEN      9218/redis-server 0 
tcp        0      0 0.0.0.0:7002            0.0.0.0:*               LISTEN      9297/redis-server 0 
tcp        0      0 0.0.0.0:7003            0.0.0.0:*               LISTEN      9323/redis-server 0 
tcp        0      0 0.0.0.0:7004            0.0.0.0:*               LISTEN      9143/redis-server 0 
tcp        0      0 0.0.0.0:7005            0.0.0.0:*               LISTEN      9192/redis-server 0 
tcp        0      0 0.0.0.0:17000           0.0.0.0:*               LISTEN      9090/redis-server 0 
tcp        0      0 0.0.0.0:17001           0.0.0.0:*               LISTEN      9218/redis-server 0 
tcp        0      0 0.0.0.0:17002           0.0.0.0:*               LISTEN      9297/redis-server 0 
tcp        0      0 0.0.0.0:17003           0.0.0.0:*               LISTEN      9323/redis-server 0 
tcp        0      0 0.0.0.0:17004           0.0.0.0:*               LISTEN      9143/redis-server 0 
tcp        0      0 0.0.0.0:17005           0.0.0.0:*               LISTEN      9192/redis-server 0 

# 初始化集群
redis-cli -a password --cluster create \
127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
--cluster-replicas 1
# 会输出建议的master和slave分布，同意的话，输入yes即可
# 会提示redis集群创建完毕
```

### docker/nat网络环境支持
在实际上生产的时候遇到了一个问题，因为机房是nat网络结构，导致了如果我们用内网ip把redis-cluster启动起来，机房外部的客户端A访问这个集群碰到redirect的情况会有问题。因为当连接上node01的时，碰到需要redirect的情况，node01给出的redirect的ip是内网ip，而客户端A是使用外网才能访问到redis-cluster，此时就是有报错。所以此时需要以下几个配置
- cluster-announce-ip，手动配置加入集群的ip
- cluster-announce-port，手动配置加入集群的port
- cluster-announce-bus-port，如果这个端口配置，则取代regular port+10000的策略，使用这个端口来替代

详细配置的官方解释看这里
```
########################## CLUSTER DOCKER/NAT support  ########################

# In certain deployments, Redis Cluster nodes address discovery fails, because
# addresses are NAT-ted or because ports are forwarded (the typical case is
# Docker and other containers).
#
# In order to make Redis Cluster working in such environments, a static
# configuration where each node knows its public address is needed. The
# following two options are used for this scope, and are:
#
# * cluster-announce-ip
# * cluster-announce-port
# * cluster-announce-bus-port
#
# Each instruct the node about its address, client port, and cluster message
# bus port. The information is then published in the header of the bus packets
# so that other nodes will be able to correctly map the address of the node
# publishing the information.
#
# If the above options are not used, the normal Redis Cluster auto-detection
# will be used instead.
#
# Note that when remapped, the bus port may not be at the fixed offset of
# clients port + 10000, so you can specify any port and bus-port depending
# on how they get remapped. If the bus-port is not set, a fixed offset of
# 10000 will be used as usually.
#
# Example:
#
# cluster-announce-ip 10.1.1.5
# cluster-announce-port 6379
# cluster-announce-bus-port 6380
```
> [redis.conf](http://download.redis.io/redis-stable/redis.conf)