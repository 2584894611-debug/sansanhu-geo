# 好易易GEO 线上部署方案

> 版本：v1.0  
> 日期：2025年5月  
> 状态：正式版

---

## 一、项目概述

### 1.1 产品简介
好易易GEO是一款面向B端的AI搜索优化分析工具，帮助品牌方洞察在豆包、DeepSeek、元宝、Kimi、通义千问、智谱等6大AI搜索平台的推荐表现，并提供优化建议。

### 1.2 核心功能
- **GEO评分系统**：品牌AI搜索可见性评分（0-100）
- **竞品对比分析**：多平台横向对比
- **优化建议生成**：基于AI推荐逻辑的内容策略
- **Freemium模式**：免费1次/天，付费解锁详细报告

### 1.3 技术栈
| 层级 | 技术方案 |
|------|----------|
| 前端 | Vue3 + Vite + Pinia + ECharts |
| 后端 | FastAPI (Python 3.10+) |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| AI引擎 | DeepSeek API |
| 运行环境 | Docker + Docker Compose |

---

## 二、云服务商选择

### 2.1 主流方案对比

| 服务商 | 优势 | 劣势 | 推荐场景 |
|--------|------|------|----------|
| **阿里云** | 国内访问快、备案方便、产品生态完善 | 价格较高、配置复杂 | 生产环境首选 |
| **腾讯云** | 微信生态集成、优惠活动多 | 文档质量一般 | 需微信支付首选 |
| **Vercel** | 免费额度大、CDN全球覆盖 | 国内访问慢、需企业备案 | 前端静态部署备选 |
| **Railway** | 部署简单、按需付费 | 国内访问慢、价格偏高 | 快速验证/海外 |
| **Zeabur** | 支持Docker、国内节点 | 新兴产品、文档较少 | 技术团队偏好 |

### 2.2 推荐方案

**🏆 最佳选择：阿里云 ECS + 容器服务**

**推荐理由：**
1. **国内访问速度最优**：用户群主要在国内，阿里云BGP网络覆盖好
2. **备案支持完善**：.com/.cn域名均可快速备案
3. **成本可控**：2核4G ECS约80-120元/月，满足初期需求
4. **扩展性强**：后续可平滑升级至K8s集群
5. **生态完善**：可搭配OSS、日志服务、监控等

### 2.3 备选方案

| 阶段 | 推荐配置 | 月成本 |
|------|----------|--------|
| 初期验证 | 1核2G轻量应用服务器 | ¥30-50 |
| 正式运营 | 2核4G ECS | ¥80-120 |
| 规模扩展 | 2核4G × 2 + SLB负载均衡 | ¥200-300 |

---

## 三、架构设计

### 3.1 整体架构图

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                        用户端                                │
                    │                    https://geo.haoyiyi.com                   │
                    └─────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │                      CDN / OSS                               │
                    │                  (前端静态资源加速)                            │
                    └─────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    阿里云 ECS                                │
                    │  ┌─────────────────┐      ┌─────────────────────────────┐   │
                    │  │   Nginx         │      │     FastAPI 后端服务         │   │
                    │  │  (反向代理/SSL)  │ ───▶ │   - /api/analysis           │   │
                    │  │  端口: 80/443   │      │   - /api/user/status        │   │
                    │  └─────────────────┘      │   - /api/payment/webhook    │   │
                    │                          └─────────────────────────────┘   │
                    │                                      │                      │
                    │                          ┌───────────┴───────────┐           │
                    │                          ▼                       ▼           │
                    │                  ┌─────────────┐      ┌─────────────────┐    │
                    │                  │ PostgreSQL  │      │   DeepSeek API  │    │
                    │                  │  (数据存储)  │      │  (AI分析引擎)   │    │
                    │                  └─────────────┘      └─────────────────┘    │
                    │                          │                      │          │
                    │                          ▼                      ▼          │
                    │                  ┌─────────────┐      ┌─────────────────┐    │
                    │                  │ 定时任务    │      │ 微信支付API    │    │
                    │                  │ (自动采集)  │      │ (支付回调)     │    │
                    │                  └─────────────┘      └─────────────────┘    │
                    └─────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │                     数据持久化层                              │
                    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
                    │  │  geo.db      │  │  用户数据    │  │  分析报告存储   │     │
                    │  │ (SQLite→PG) │  │  (users)     │  │  (reports)       │     │
                    │  └──────────────┘  └──────────────┘  └──────────────────┘     │
                    └─────────────────────────────────────────────────────────────┘
```

### 3.2 前端部署方案

#### 方案A：阿里云 OSS + CDN（推荐）

```bash
# 构建前端
cd geo-insight/web
npm install
npm run build  # 输出到 dist/

# 上传到 OSS
ossutil cp -r dist/ oss://your-bucket/ --force

# 配置 CDN 回源到 OSS
```

**优势：**
- 静态资源全球加速
- 自动 Gzip 压缩
- 免费 HTTPS 证书
- 月成本约 ¥20-50

#### 方案B：ECS + Nginx

```nginx
# /etc/nginx/conf.d/geo.conf
server {
    listen 80;
    server_name geo.haoyiyi.com;
    
    location / {
        root /var/www/geo-insight/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3.3 后端部署方案

#### FastAPI 服务配置

```dockerfile
# geo-insight/server/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 5000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### docker-compose.yml（生产版）

```yaml
version: '3.8'

services:
  # 后端 API 服务
  geo-api:
    build:
      context: ./server
      dockerfile: Dockerfile
    container_name: geo-api
    ports:
      - "5000:5000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - DATABASE_URL=${DATABASE_URL}  # postgresql://user:pass@host:5432/geo
      - WECHAT_APPID=${WECHAT_APPID}
      - WECHAT_SECRET=${WECHAT_SECRET}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: geo-postgres
    environment:
      - POSTGRES_DB=geo_insight
      - POSTGRES_USER=${POSTGRES_USER:-geo}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U geo"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: geo-redis
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # 定时任务（自动采集）
  geo-scheduler:
    build:
      context: ./tasks
      dockerfile: Dockerfile.scheduler
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3.4 数据库方案

#### 开发阶段：SQLite
- 零配置，零成本
- 适合 < 1000 用户
- 数据文件： `./data/geo.db`

#### 生产阶段：PostgreSQL
- 高并发支持
- 完整事务支持
- 备份恢复完善

**迁移命令：**
```bash
# SQLite → PostgreSQL
pgloader ./data/geo.db postgresql://geo:password@localhost:5432/geo_insight
```

**阿里云 RDS PostgreSQL 配置：**
| 配置项 | 推荐值 |
|--------|--------|
| 实例规格 | 1核2G 通用型 |
| 存储空间 | 40GB |
| 自动备份 | 开启 |
| SSL连接 | 开启 |

---

## 四、域名建议

### 4.1 域名推荐

| 域名 | 用途 | 推荐度 | 价格 |
|------|------|--------|------|
| `haoyiyi.com` | 品牌主域名 | ⭐⭐⭐⭐⭐ | ¥50-80/年 |
| `geo.haoyiyi.com` | 产品主站 | ⭐⭐⭐⭐⭐ | 免费子域名 |
| `api.geo.haoyiyi.com` | API服务 | ⭐⭐⭐⭐⭐ | 免费子域名 |
| `haoyiyi.cn` | 品牌保护 | ⭐⭐⭐⭐ | ¥30-50/年 |
| `geoai.com` | 产品备用 | ⭐⭐⭐ | ¥100-200/年 |

### 4.2 域名注册推荐

| 注册商 | 优势 | 优惠码 |
|--------|------|--------|
| 阿里云域名 | 备案便捷、续费稳定 | 可用优惠券 |
| 腾讯云域名 | 微信生态集成 | 新客优惠 |

### 4.3 域名备案
- **必须备案**：使用国内服务器（阿里云/腾讯云）必须备案
- **备案时间**：7-15个工作日
- **备案材料**：身份证、营业执照、网站说明书

---

## 五、成本预估

### 5.1 月度成本明细

| 项目 | 方案A（经济型） | 方案B（标准型） | 方案C（生产型） |
|------|----------------|----------------|----------------|
| **云服务器** | | | |
| 轻量应用服务器 1核2G | ¥30 | - | - |
| ECS 2核4G | - | ¥99 | ¥180 |
| **数据库** | | | |
| 自建 SQLite | ¥0 | - | - |
| RDS PostgreSQL 1核2G | - | ¥60 | ¥120 |
| **存储/CDN** | | | |
| OSS + CDN | - | ¥30 | ¥50 |
| **域名** | | | |
| .com 域名 | ¥7 | ¥7 | ¥7 |
| **SSL证书** | 免费 | 免费 | 免费 |
| **微信支付** | | | |
| 服务商手续费 | 0.6% | 0.6% | 0.6% |
| **DeepSeek API** | | | |
| 估算（日均500次分析） | ¥300 | ¥500 | ¥800 |
| **总计** | **¥337+** | **¥696+** | **¥1157+** |

### 5.2 DeepSeek API 成本估算

| 场景 | 次数/月 | Token估算 | 月成本 |
|------|---------|-----------|--------|
| 免费用户（1次/天） | 30次 | 10K/次 | ¥3 |
| 付费用户（10次/天） | 300次 | 10K/次 | ¥30 |
| 100付费用户 | 30,000次 | 10K/次 | ¥3,000 |

> DeepSeek API 价格：约 ¥1/1M tokens（参考价，具体以官方定价为准）

### 5.3 成本优化建议

1. **API调用优化**：
   - 添加结果缓存（Redis），相同查询返回缓存
   - 限制详细报告生成频率
   - 使用更低价的模型做预筛选

2. **资源优化**：
   - 前端静态资源充分利用 CDN
   - 数据库连接池复用
   - 非高峰时段执行定时任务

3. **阶梯定价**：
   - 免费层：1次/天基础分析
   - 付费基础版：¥29/月，10次/天
   - 付费专业版：¥99/月，无限次 + 详细报告

---

## 六、支付接入方案

### 6.1 微信支付接入流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户端    │ ──▶ │   后端API   │ ──▶ │  微信支付   │
│  选择套餐   │     │  创建订单   │     │   统一下单  │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                          ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   订单入库   │     │  支付成功   │
                    └─────────────┘     └─────────────┘
                          │                    │
                          ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │ 等待支付   │ ◀── │  微信回调   │
                    │ 查询结果   │     │  更新状态   │
                    └─────────────┘     └─────────────┘
```

### 6.2 微信支付申请

#### 个人开发者
- 使用微信收款码（个人转账）
- 限制：无法开通正式支付

#### 企业用户（推荐）
1. **注册微信商户号**：https://pay.weixin.qq.com
2. **选择主体类型**：
   - 小程序支付（需有小程序）
   - 公众号支付（需有公众号）
   - H5支付（推荐，无需小程序）
3. **提交资质审核**：1-7个工作日
4. **开发配置**：
   - 设置 APIv3 密钥
   - 下载证书
   - 配置支付回调地址

### 6.3 后端支付接口实现

```python
# server/utils/payment.py

import hashlib
import time
import json
import httpx
from typing import Dict, Any

class WechatPay:
    def __init__(self, appid: str, mchid: str, apiv3_key: str, private_key_path: str):
        self.appid = appid
        self.mchid = mchid
        self.apiv3_key = apiv3_key
        self.private_key_path = private_key_path
        self.api_base = "https://api.mch.weixin.qq.com/v3"
    
    def create_order(self, out_trade_no: str, description: str, 
                     amount: int, notify_url: str) -> Dict[str, Any]:
        """
        创建支付订单
        amount: 金额（分）
        """
        # 实际实现需使用微信支付APIv3签名
        # 此处为伪代码
        
        order_data = {
            "appid": self.appid,
            "mchid": self.mchid,
            "out_trade_no": out_trade_no,
            "description": description,
            "amount": {"total": amount, "currency": "CNY"},
            "notify_url": notify_url,
            "scene_type": "H5",
            "h5_info": {"type": "Wap"}
        }
        
        # 调用微信支付统一下单接口
        # ...
        return {"code_url": "weixin://..."}  # 跳转支付链接
```

### 6.4 支付回调处理

```python
# server/api_server.py

from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/payment", tags=["支付"])

class PaymentCallback(BaseModel):
    transaction_id: str
    out_trade_no: str
    trade_state: str
    total: int

@router.post("/notify")
async def payment_notify(request: Request):
    """微信支付回调"""
    # 1. 获取原始回调数据
    body = await request.body()
    headers = dict(request.headers)
    
    # 2. 验证签名（必须！）
    # if not verify_wechat_sign(body, headers):
    #     return {"code": "FAIL", "message": "签名验证失败"}
    
    # 3. 解析并处理
    data = await request.json()
    
    if data.get("trade_state") == "SUCCESS":
        # 4. 更新用户权限
        await activate_premium(data["out_trade_no"])
        
        return {"code": "SUCCESS", "message": "成功"}
    
    return {"code": "FAIL"}

async def activate_premium(order_no: str):
    """激活付费会员"""
    # 1. 查询订单信息
    # 2. 更新用户表 is_premium = 1
    # 3. 记录订阅信息
    pass
```

### 6.5 备选支付方案

| 方案 | 接入难度 | 费用 | 推荐场景 |
|------|----------|------|----------|
| **Stripe** | 中等 | 3.2%+ | 国际化、信用卡 |
| **PayPal** | 简单 | 3.5%+ | 跨境收款 |
| **收款码** | 极简 | 0 | 早期验证 |

---

## 七、部署步骤详解

### 7.1 第一阶段：服务器准备（Day 1）

#### 1. 购买阿里云 ECS

```bash
# 配置推荐
地域：华北2（北京）或华东1（上海）
实例：2核4G 突发性能型 t6
系统盘：40GB SSD
带宽：5Mbps 按量付费
系统：Ubuntu 22.04 LTS
```

#### 2. 域名购买与备案

```bash
# 购买域名
# 阿里云控制台 → 域名与网站 → 域名注册
# 推荐：haoyiyi.com

# 备案流程
# 1. 购买服务器后获取备案服务号
# 2. 阿里云ICP代备案系统提交
# 3. 上传证件、真实性核验
# 4. 等待审核：7-15个工作日
```

#### 3. 安装基础软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# 安装 Docker Compose
sudo apt install docker-compose -y

# 安装 Nginx
sudo apt install nginx -y
```

### 7.2 第二阶段：代码部署（Day 2-3）

#### 1. 上传代码

```bash
# 创建项目目录
sudo mkdir -p /var/www/geo-insight
cd /var/www/geo-insight

# 上传代码（方式一：Git）
git clone https://your-repo/geo-insight.git .

# 上传代码（方式二：SCP）
scp -r geo-insight ubuntu@your-server:/var/www/
```

#### 2. 配置环境变量

```bash
# 创建 .env 文件
cat > /var/www/geo-insight/.env << EOF
# DeepSeek API
DEEPSEEK_API_KEY=sk-8914498a0fff48e793153ab852a38ae5

# 数据库
POSTGRES_USER=geo
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://geo:your_secure_password_here@postgres:5432/geo_insight

# Redis
REDIS_URL=redis://redis:6379/0

# 微信支付
WECHAT_APPID=wx_your_appid
WECHAT_MCHID=your_mchid
WECHAT_APIV3_KEY=your_apiv3_key
WECHAT_NOTIFY_URL=https://api.geo.haoyiyi.com/api/payment/notify

# JWT密钥
JWT_SECRET=your_jwt_secret_here
EOF

# 保护 .env 文件
chmod 600 /var/www/geo-insight/.env
```

#### 3. 构建并启动服务

```bash
cd /var/www/geo-insight

# 构建镜像
docker-compose build

# 启动服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

#### 4. 配置 Nginx

```bash
# 创建 Nginx 配置
sudo cat > /etc/nginx/sites-available/geo-insight << 'EOF'
server {
    listen 80;
    server_name geo.haoyiyi.com api.geo.haoyiyi.com;
    
    # 重定向到 HTTPS（SSL配置后启用）
    # return 301 https://$server_name$request_uri;
    
    client_max_body_size 50M;
    
    location / {
        root /var/www/geo-insight/web/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/geo-insight /etc/nginx/sites-enabled/

# 测试并重载
sudo nginx -t
sudo systemctl reload nginx
```

### 7.3 第三阶段：SSL 配置（Day 3）

#### 使用 Let's Encrypt 免费证书

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 申请证书
sudo certbot --nginx -d geo.haoyiyi.com -d api.geo.haoyiyi.com

# 自动续期（Let's Encrypt 证书90天有效期，Certbot 自动续期）
sudo systemctl status certbot.timer
```

### 7.4 第四阶段：数据库迁移（Day 4）

#### SQLite 迁移到 PostgreSQL

```bash
# 1. 安装 pgloader
sudo apt install pgloader -y

# 2. 停止服务
docker-compose down

# 3. 迁移数据
pgloader ./data/geo.db postgresql://geo:password@localhost:5432/geo_insight

# 4. 验证数据
psql -U geo -d geo_insight -c "SELECT COUNT(*) FROM users;"

# 5. 重启服务
docker-compose up -d
```

### 7.5 第五阶段：支付接入（Day 5-7）

#### 微信支付配置

```bash
# 1. 下载微信支付证书
# 登录微信商户平台 → API安全 → 申请证书

# 2. 上传证书到服务器
scp apiclient_cert.pem ubuntu@your-server:/var/www/geo-insight/certs/
scp apiclient_key.pem ubuntu@your-server:/var/www/geo-insight/certs/

# 3. 配置 Nginx 支持大请求体
# （微信支付回调可能较大）
```

### 7.6 第六阶段：监控与运维（Day 8）

#### 日志配置

```bash
# 配置日志轮转
cat > /etc/logrotate.d/geo-insight << 'EOF'
/var/www/geo-insight/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        docker-compose -f /var/www/geo-insight/docker-compose.yml restart geo-api
    endscript
}
EOF
```

#### 健康检查

```bash
# 创建健康检查脚本
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash
# 健康检查脚本

API_URL="http://127.0.0.1:5000/api/health"
ALERT_EMAIL="admin@haoyiyi.com"

# 检查 API
if ! curl -sf "$API_URL" > /dev/null; then
    echo "$(date): API 健康检查失败" | tee -a /var/log/geo-health.log
    # 发送告警（可接入钉钉/飞书/短信）
fi
EOF

chmod +x /usr/local/bin/health-check.sh

# 添加到 crontab
echo "*/5 * * * * /usr/local/bin/health-check.sh" | sudo tee -a /var/spool/cron/crontabs/root
```

---

## 八、时间预估

### 8.1 项目总工期

| 阶段 | 任务 | 预计时间 | 依赖项 |
|------|------|----------|--------|
| **Day 1** | 云服务器购买、配置 | 2-4小时 | 无 |
| **Day 1** | 域名购买 | 1小时 | 无 |
| **Day 1-15** | 域名备案 | 7-15工作日 | 域名+服务器 |
| **Day 2** | 代码部署 | 4-6小时 | 服务器就绪 |
| **Day 2** | SSL证书配置 | 1-2小时 | 域名DNS |
| **Day 3** | 数据库配置 | 2-3小时 | PostgreSQL就绪 |
| **Day 4-5** | 微信支付申请 | 1-3天 | 营业执照 |
| **Day 5-7** | 支付接口开发 | 1-2天 | 商户号 |
| **Day 8** | 监控配置 | 2-3小时 | 无 |
| **Day 9** | 测试与调优 | 4-8小时 | 全功能 |

### 8.2 关键路径

```
域名备案（7-15天） ─────────────────────────┐
      │                                      │
      ▼                                      ▼
服务器购买 ──▶ 代码部署 ──▶ SSL配置 ──▶ 支付接入 ──▶ 上线
```

### 8.3 加速上线建议

| 策略 | 效果 | 建议 |
|------|------|------|
| **提前备案** | 节省7-15天 | 与开发并行 |
| **个人收款过渡** | 节省3-5天 | 早期验证 |
| **使用现有域名** | 节省1天 | 如已有域名 |
| **简化支付流程** | 节省1-2天 | 先接基础版 |

### 8.4 快速上线时间线

| 方案 | 最快时间 | 说明 |
|------|----------|------|
| **最低配上线** | 3-5天 | 个人收款+已有域名 |
| **标准上线** | 15-20天 | 含完整支付+备案 |
| **完整上线** | 30天+ | 含所有高级功能 |

---

## 九、附录

### 9.1 环境变量清单

```bash
# ========== 必填项 ==========

# DeepSeek API（核心AI能力）
DEEPSEEK_API_KEY=sk-8914498a0fff48e793153ab852a38ae5

# 数据库
DATABASE_URL=postgresql://geo:your_password@host:5432/geo_insight

# ========== 微信支付 ==========
WECHAT_APPID=wx1234567890abcdef
WECHAT_MCHID=1234567890
WECHAT_APIV3_KEY=your_32_char_key_here
WECHAT_NOTIFY_URL=https://api.geo.haoyiyi.com/api/payment/notify
WECHAT_CERT_PATH=/app/certs/apiclient_cert.pem
WECHAT_KEY_PATH=/app/certs/apiclient_key.pem

# ========== 安全配置 ==========
JWT_SECRET=generate_a_secure_random_string_here
CORS_ORIGINS=https://geo.haoyiyi.com

# ========== 可选项 ==========
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO
```

### 9.2 常用命令速查

```bash
# 服务管理
docker-compose up -d              # 启动服务
docker-compose down               # 停止服务
docker-compose restart            # 重启服务
docker-compose logs -f            # 查看日志
docker-compose logs -f geo-api   # 查看特定服务日志

# 数据库
docker exec -it geo-postgres psql -U geo -d geo_insight  # 连接数据库
pg_dump -U geo geo_insight > backup.sql                   # 导出数据

# Nginx
sudo nginx -t                    # 测试配置
sudo systemctl reload nginx      # 重载配置
sudo systemctl restart nginx     # 重启Nginx

# SSL
sudo certbot renew --dry-run     # 测试续期
sudo certbot renew               # 手动续期
```

### 9.3 推荐监控方案

| 监控项 | 推荐工具 | 成本 |
|--------|----------|------|
| 服务可用性 | 阿里云云监控 | 免费 |
| 日志分析 | 阿里云日志服务 | ¥0.1/GB |
| APM | 阿里云ARMS | ¥99/月起 |
| 告警通知 | 钉钉机器人 | 免费 |

---

## 十、联系与支持

- **技术支持邮箱**：support@haoyiyi.com
- **开发者文档**：docs.geo.haoyiyi.com
- **状态页**：status.geo.haoyiyi.com

---

> 📝 **文档更新记录**
> - v1.0 (2025-05)：初始版本
