# aiohttp 是一个基于 asyncio 的库，
# 它提供了两个核心功能：异步HTTP客户端和异步HTTP服务器。
# 原生支持WebSocket和HTTP/2协议
import asyncio
import aiohttp
'''
total：整个请求（包括连接、发送、读取）的最大时长。
connect：建立 TCP 连接的超时。
sock_read：从 socket 读取数据的超时（两次数据到达间隔）。
sock_connect：socket 连接超时（通常与 connect 类似）。
'''
time_out = aiohttp.ClientTimeout(total=10)

''''
如果不设置：默认 limit=100，limit_per_host=0（无限制）。
连接耗尽行为：当并发请求数超过 limit 时，
新的请求会等待直到有连接释放。这相当于内置的背压控制，避免压垮目标服务器或本地资源。
'''
connector = aiohttp.TCPConnector(
    limit=100,               # 总连接数上限
    limit_per_host=30,       # 同一主机最大连接数
    ttl_dns_cache=300,       # DNS 缓存时间（秒）
    enable_cleanup_closed=True  # 自动清理关闭的连接
)


'''
aiohttp.ClientSession()
# ClientSession 是 aiohttp 客户端的核心，
# 它管理连接池、保持 Cookie、复用 TCP 连接。
# 强烈建议在整个应用生命周期中只创建一个 session，而不是每次请求都新建。
为什么必须复用 session？
连接复用：避免每次请求都三次握手，显著提升性能。
Cookie 持久化：登录后后续请求自动携带。
连接池共享：限制总连接数、每主机连接数。

'''
session = aiohttp.ClientSession(timeout=time_out,connector=connector)


'''
params：字典或字符串，拼接到 URL 查询字符串。
data：表单编码（application/x-www-form-urlencoded）或字节/字符串。
json：自动序列化为 JSON 并设置 Content-Type: application/json。

headers：自定义请求头字典。
cookies：自定义 Cookie 字典。
allow_redirects：是否自动跟随重定向（默认 True）。
ssl：SSL 验证，可设为 False 跳过（不推荐生产）。
'''
# POST (JSON)
async def post_func():
    # params json data
    async with session.post('https://httpbin.org/post', json={'key': 'value'}) as resp:
        pass

# 响应处理
# 响应体只能读取一次，再次调用 text() / json() / read() 会得到空或异常。
async def receive_func():
    async with session.get('https://httpbin.org/get') as resp:
        # 检查状态码
        if resp.status == 200:
            # 文本内容
            text = await resp.text()
            # JSON
            data = await resp.json()
            # 二进制
            content = await resp.read()
            # 原始响应头
            print(resp.headers)
            # 获取特定头
            content_type = resp.headers.get('Content-Type')
            # 流式读取大文件：避免一次性加载到内存
            async with session.get('https://example.com/large-file') as resp:
                with open('output.bin', 'wb') as f:
                    async for chunk in resp.content.iter_chunks():
                        f.write(chunk[0])

# 异常处理
from aiohttp import ClientError, ClientConnectionError, ClientResponseError, ClientTimeout

try:
    async def exception_func():
        async with session.get('https://nonexistent.example.com') as resp:
            resp.raise_for_status()  # 状态码非 2xx 时抛出 ClientResponseError
            return await resp.json()
except ClientResponseError as e:
    print(f"HTTP 错误: {e.status}, {e.message}")
except ClientConnectionError as e:
    print(f"连接错误: {e}")
except ClientTimeout:
    print("超时")
except ClientError as e:  # 所有 aiohttp 客户端异常的基类
    print(f"其他客户端错误: {e}")


# 请求头
auth=aiohttp.BasicAuth('user', 'pass')  # auth
headers = {'Authorization': 'Bearer your_token'}  # Bearer Token headers=headers
# 代理
'''
# HTTP 代理
async with session.get('https://example.com', proxy='http://proxy.example.com:8080') as resp:
    pass

# 带认证的代理
proxy_auth = aiohttp.BasicAuth('user', 'pass')
async with session.get('https://example.com', proxy='http://proxy.example.com:8080', proxy_auth=proxy_auth) as resp:
    pass
'''

