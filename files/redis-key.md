# Redis Keyspace Notifications

Redis keyspace notifications are a publish/subscribe mechanism that allows clients to receive specific event notifications about keys in the Redis database by subscribing to channels. This feature is very useful for building real-time applications, data synchronization systems, and monitoring tools.

## Basic Concepts

Keyspace notifications have two types of events:
1. **Keyspace events**: Focus on operations on the key itself, such as `del`, `expire`, etc.
2. **Key-event events**: Focus on the event itself, such as `expired`, `evicted`, etc.

## Enabling Keyspace Notifications

By default, Redis does not enable keyspace notifications and needs to be configured:

```bash
# Configure in redis.conf
notify-keyspace-events "parameters"

# Or configure at runtime
CONFIG SET notify-keyspace-events "parameters"
```

## Notification Parameters

Parameters are combinations of the following characters:
- `K`: Enable keyspace notifications
- `E`: Enable key-event notifications
- `g`: Generic commands (like DEL, EXPIRE, etc.)
- `$`: String commands
- `l`: List commands
- `s`: Set commands
- `h`: Hash commands
- `z`: Sorted set commands
- `x`: Expiration events
- `e`: Eviction events (when memory is insufficient)
- `A`: All events (equivalent to alias for `g$lshzxe`)

Common configuration examples:
- `"AKE"`: All keyspace and key-event notifications
- `"Ex"`: Only enable expiration notifications in key events
- `"K$"`: Only enable string operation notifications in keyspace

## 订阅通知

客户端通过订阅 `__keyspace@<db>__:<key>` 或 `__keyevent@<db>__:<event>` 频道来接收通知：

```bash
# 订阅所有键空间事件
PSUBSCRIBE __keyspace@0__:*

# 订阅所有键事件
PSUBSCRIBE __keyevent@0__:*

# 订阅特定键的过期事件
SUBSCRIBE __keyevent@0__:expired
```

## 事件类型

常见事件包括：
- `set`：键被设置
- `del`：键被删除
- `expire`：键被设置过期时间
- `expired`：键因过期被删除
- `evicted`：键因内存策略被驱逐
- `rename`：键被重命名
- `hset`：哈希字段被设置
- `lpush`：列表被推入元素

## 使用示例

1. 启用过期事件通知：
```bash
CONFIG SET notify-keyspace-events Ex
```

2. 在一个客户端订阅过期事件：
```bash
SUBSCRIBE __keyevent@0__:expired
```

3. 在另一个客户端设置一个会过期的键：
```bash
SETEX mykey 10 "value"
```

10秒后，订阅客户端将收到类似的消息：
```
1) "message"
2) "__keyevent@0__:expired"
3) "mykey"
```

## 注意事项

1. 性能影响：启用通知会对 Redis 性能产生轻微影响
2. 可靠性：如果客户端断开连接，可能会丢失通知
3. 持久性：通知不会被持久化，只发送给当前连接的订阅者
4. 内存使用：大量事件可能导致内存使用增加

键空间通知是构建实时应用和监控系统的强大工具，合理使用可以显著提高应用的响应能力和数据一致性。

---

Redis 键空间通知（Keyspace Notifications）适用于多种需要实时响应数据变更的场景，以下是常见的应用场景：

---

### **1. 订单超时自动取消**
- **场景**：电商系统中，用户下单后若未在指定时间（如30分钟）内支付，订单自动取消。
- **实现**：
    - 使用 `SETEX order:123 1800 "订单数据"` 设置订单键，并订阅 `__keyevent@0__:expired` 事件。
    - 键过期时触发回调，执行撤单逻辑。

---

### **2. 优惠券/活动过期处理**
- **场景**：限时优惠券或活动结束后，自动关闭领取入口或触发后续结算。
- **实现**：
    - 设置活动键的过期时间（如 `EXPIRE event:coupon 86400`）。
    - 订阅 `expired` 事件，触发清理或通知操作。

---

### **3. 缓存一致性维护**
- **场景**：数据库更新后，需同步失效或更新Redis缓存。
- **实现**：
    - 订阅 `del` 或 `set` 事件，当缓存键被修改时，重新加载数据或标记为失效。

---

### **4. 会话（Session）超时管理**
- **场景**：用户会话过期后，自动清理关联资源（如退出登录、释放锁）。
- **实现**：
    - 设置会话键的TTL（如 `SETEX session:user1 3600 "data"`）。
    - 监听 `expired` 事件执行清理逻辑。

---

### **5. 分布式任务调度**
- **场景**：延迟任务（如定时提醒、消息重试）。
- **实现**：
    - 使用 `SETEX task:reminder 60 "任务内容"`，通过键过期事件触发任务执行，替代轮询查询。

---

### **6. 实时数据监控与告警**
- **场景**：监控关键数据变更（如库存变动、配置更新）。
- **实现**：
    - 订阅 `hset`（哈希字段更新）、`incr`（计数器变更）等事件，触发告警或日志记录。

---

### **7. 排行榜/热点数据刷新**
- **场景**：定时重置每日排行榜或刷新热点数据。
- **实现**：
    - 设置每日过期键（如 `EXPIRE rank:daily 86400`），过期后自动重新计算排名。

---

### **注意事项**
1. **可靠性**：Redis通知是“发送即忘”（fire-and-forget），断线期间的事件会丢失，需结合持久化或重试机制。
2. **性能**：大量事件可能增加CPU和网络负载，建议按需配置（如仅启用 `Ex` 监听过期事件）。
3. **多实例协同**：多个服务节点可能同时收到通知，需确保业务逻辑的幂等性。

如需具体代码实现（如PHP/Python），可参考相关示例。


---

我将基于不同应用场景给出 **Redis键空间通知** 的具体实现代码（使用Python + Redis-py库），包含完整的事件订阅和处理逻辑。

---

### 场景1：订单超时自动取消（Python实现）
```python
import redis
import threading

# 初始化Redis连接
r = redis.Redis(host='localhost', port=6379, db=0)

# 启用键过期事件通知
r.config_set('notify-keyspace-events', 'Ex')

# 订单处理函数
def cancel_order(order_id):
    print(f"订单 {order_id} 已超时，执行取消操作")
    # 这里添加实际业务逻辑（如更新数据库状态）

# 订阅过期事件的线程
def listen_expired_events():
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired')  # 订阅所有过期事件
    
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            expired_key = message['data'].decode('utf-8')
            if expired_key.startswith('order:'):
                order_id = expired_key.split(':')[1]
                cancel_order(order_id)

# 启动监听线程
threading.Thread(target=listen_expired_events, daemon=True).start()

# 模拟下单（30分钟后过期）
order_id = "12345"
r.setex(f"order:{order_id}", 1800, "订单数据")  # 30分钟 = 1800秒
print(f"订单 {order_id} 已创建，等待支付...")

# 主线程保持运行
while True:
    pass
```

---

### 场景2：优惠券过期处理（Node.js实现）
```javascript
const redis = require('redis');
const client = redis.createClient();
const subscriber = redis.createClient();

// 启用过期事件通知
client.send_command('CONFIG', ['SET', 'notify-keyspace-events', 'Ex']);

// 监听优惠券过期事件
subscriber.psubscribe('__keyevent@0__:expired');
subscriber.on('pmessage', (pattern, channel, expiredKey) => {
    if (expiredKey.startsWith('coupon:')) {
        const couponId = expiredKey.split(':')[1];
        console.log(`优惠券 ${couponId} 已过期，关闭领取入口`);
        // 这里添加实际业务逻辑
    }
});

// 设置优惠券（24小时后过期）
const couponId = "coupon_100";
client.setex(`coupon:${couponId}`, 86400, "折扣信息");
console.log(`优惠券 ${couponId} 已发布`);
```

---

### 场景3：缓存一致性维护（Java实现）
```java
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPubSub;

public class CacheInvalidator {
    public static void main(String[] args) {
        Jedis jedis = new Jedis("localhost");
        JedisPubSub listener = new JedisPubSub() {
            @Override
            public void onPMessage(String pattern, String channel, String message) {
                if (message.startsWith("product:")) {
                    System.out.println("缓存键 " + message + " 被修改，重新加载数据");
                    // 这里添加缓存重建逻辑
                }
            }
        };

        // 启用键空间通知并订阅
        jedis.configSet("notify-keyspace-events", "Kg");
        new Thread(() -> jedis.psubscribe(listener, "__keyspace@0__:*")).start();

        // 模拟数据库更新后删除缓存
        jedis.del("product:1001");
    }
}
```

---

### 场景4：会话超时管理（Go实现）
```go
package main

import (
	"github.com/go-redis/redis"
	"log"
)

func main() {
	client := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
	
	// 启用键事件通知
	client.ConfigSet("notify-keyspace-events", "Ex")
	
	pubsub := client.PSubscribe("__keyevent@0__:expired")
	defer pubsub.Close()
	
	// 启动goroutine监听事件
	go func() {
		for msg := range pubsub.Channel() {
			key := msg.Payload
			if strings.HasPrefix(key, "session:") {
				userID := strings.TrimPrefix(key, "session:")
				log.Printf("用户 %s 会话已过期，清理资源", userID)
				// 这里添加清理逻辑
			}
		}
	}()

	// 设置会话（1小时后过期）
	client.SetEX("session:user789", 3600, "session_data", 0)
	log.Println("会话已创建")
	
	select {} // 阻塞主线程
}
```

---

### 关键点说明
1. **事件类型选择**：
    - 订单超时用 `Ex`（仅监听过期事件）
    - 缓存更新用 `Kg`（键空间通用操作）

2. **多语言适配**：
    - Python：`redis-py` + 多线程
    - Node.js：`redis` 库 + 事件回调
    - Java：`Jedis` + 单独订阅线程
    - Go：`go-redis` + goroutine

3. **生产环境建议**：
   ```python
   # 添加异常处理和重连机制
   def listen_expired_events():
       while True:
           try:
               pubsub = r.pubsub()
               pubsub.psubscribe('__keyevent@0__:expired')
               for message in pubsub.listen():
                   # 处理逻辑
           except redis.ConnectionError:
               time.sleep(5)  # 等待重连
   ```

如果需要其他语言（如PHP/C#）实现或更复杂的业务逻辑整合，可以进一步扩展。