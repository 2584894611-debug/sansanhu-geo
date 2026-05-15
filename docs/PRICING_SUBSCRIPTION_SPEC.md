# 模块1补充：定价结构+订阅机制 详细需求

> 本文档补充PRD中"模块1：定价结构重做"的详细开发需求，供Codex执行。

---

## 一、定价页改造

### 页面结构
```
[顶部导航栏]
[定价标题区] - "选择适合你的方案" + 月付/年付切换
[三列定价卡片] - 免费版 | Pro版⭐ | 企业版
[FAQ折叠区]
```

### 定价卡片详细规范

#### 免费版卡片
- 价格：¥0/月
- 功能列表：
  - ✓ 每月1次基础检测
  - ✓ 前3个AI平台结果
  - ✓ 品牌总分+4维度分数
  - ✗ 完整9平台排名
  - ✗ 优化建议
  - ✗ 趋势监控
  - ✗ 预警通知
- 按钮：「免费开始」（绿色描边按钮，低调）
- 样式：普通边框，白色背景

#### Pro版卡片（高亮）
- 价格：¥399/月（年付¥319/月，标"省20%"）
- 顶部标签：「最受欢迎」橙色小标签
- 功能列表：
  - ✓ 月度检测+趋势报告
  - ✓ 完整9平台排名
  - ✓ 关键词渗透率分析
  - ✓ 1次播种建议
  - ✓ 3个竞品对比
  - ✓ 监控仪表盘
  - ✓ 邮件预警通知
- 按钮：「立即订阅」（橙色填充按钮）
- 样式：橙色边框2px + 轻微阴影突出

#### 企业版卡片
- 价格：「联系我们」
- 功能列表：
  - ✓ 无限次检测+实时监控
  - ✓ 播种方案+执行落地
  - ✓ 内容分发执行
  - ✓ KOC/KOL真实账号播种
  - ✓ 月度执行报告
  - ✓ 专属客服+4小时响应
  - ✓ 竞品监控+舆情预警
- 按钮：「联系销售」（深色填充按钮）
- 样式：深色背景(#1A1A2E)，白色文字

### 月付/年付切换
- 使用el-segmented组件
- 月付默认选中
- 年付选项旁标"省20%"小标签
- 切换时三列价格同步变化

### FAQ（4-6个，手风琴折叠）
1. GEO是什么？— GEO（生成式引擎优化）是让品牌在AI搜索结果中被优先引用的优化策略
2. 免费版有什么限制？— 每月1次检测，仅展示前3个AI平台结果
3. 可以随时取消订阅吗？— 可以，Pro版按月订阅，随时取消
4. 企业版怎么收费？— 根据品牌数量和服务深度定制，¥2,999-9,999/月
5. 支付方式有哪些？— 支持微信支付和支付宝

---

## 二、用户订阅系统

### 数据库新增表

```sql
-- 订阅记录表
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free',  -- free / pro / enterprise
    start_date TEXT NOT NULL,
    expire_date TEXT,
    auto_renew INTEGER DEFAULT 1,
    payment_method TEXT,  -- wechat / alipay
    payment_order_id TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 免费次数计数表
CREATE TABLE IF NOT EXISTS free_quota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    month TEXT NOT NULL,  -- 格式 2026-05
    used_count INTEGER DEFAULT 0,
    max_count INTEGER DEFAULT 1,  -- 免费版每月1次
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, month)
);
```

### 后端API

#### 1. GET /api/v1/subscription/status
获取当前用户订阅状态
```json
{
  "success": true,
  "data": {
    "tier": "pro",
    "start_date": "2026-05-01",
    "expire_date": "2026-06-01",
    "auto_renew": true,
    "days_remaining": 17,
    "features": {
      "max_detect_per_month": -1,  // -1表示无限
      "platform_count": 9,
      "competitor_count": 3,
      "dashboard": true,
      "alerts": true,
      "seeding": true
    }
  }
}
```

#### 2. POST /api/v1/subscription/create
创建Pro版订阅（先做模拟，不接真实支付）
```
请求参数：
- tier: "pro" | "enterprise"
- billing_cycle: "monthly" | "yearly"
- payment_method: "wechat" | "alipay"

返回：
{
  "success": true,
  "data": {
    "order_id": "GEO20260515170001",
    "tier": "pro",
    "amount": 39900,  // 单位：分
    "expire_date": "2026-06-15"
  }
}
```
注意：支付暂时用模拟逻辑，创建订阅后直接生效，不需要真实支付回调。后续接入支付时替换即可。

#### 3. POST /api/v1/subscription/cancel
取消自动续费
```
请求参数：
- device_id

返回：
{
  "success": true,
  "message": "已取消自动续费，当前订阅将在到期日后失效"
}
```

#### 4. GET /api/v1/subscription/feature-access
检查功能权限
```
请求参数：
- device_id
- feature: "dashboard" | "alerts" | "seeding" | "competitor" | "full_report"

返回：
{
  "success": true,
  "data": {
    "allowed": true,
    "tier_required": "pro",
    "current_tier": "pro"
  }
}
```

#### 5. GET /api/v1/user/quota
获取剩余免费次数
```
返回：
{
  "success": true,
  "data": {
    "month": "2026-05",
    "used": 1,
    "max": 1,
    "remaining": 0,
    "tier": "free"
  }
}
```

### 现有接口改造

#### POST /api/detect（检测接口）
- 增加免费次数检查逻辑
- 免费用户：检查当月已用次数，超限返回提示升级
- Pro/企业用户：不限制

#### GET /api/report/{id}（报告接口）
- 保持全开放，不做数据分层（当前策略）

---

## 三、用户中心-订阅管理页

### 页面布局
```
[左侧菜单] - 个人信息 | 我的品牌 | 订阅管理 | 预警设置 | 历史报告
[右侧内容区]
```

### 订阅管理页内容
```
┌──────────────────────────────────────┐
│  当前方案                              │
│                                        │
│  ┌────────────────────────────────┐   │
│  │  Pro版 ⭐          到期：6月15日 │   │
│  │  ¥399/月        自动续费：已开启 │   │
│  │                                │   │
│  │  [管理订阅]  [取消续费]  [升级] │   │
│  └────────────────────────────────┘   │
│                                        │
│  本月使用情况                           │
│  检测次数：5次（无限）                  │
│  监控品牌：3个                         │
│  预警通知：2条                         │
│                                        │
│  续费历史                              │
│  2026-05-01  Pro版月付  ¥399  ✓已支付  │
│  2026-04-01  Pro版月付  ¥399  ✓已支付  │
└──────────────────────────────────────┘
```

### 免费用户看到的
```
┌──────────────────────────────────────┐
│  当前方案：免费版                       │
│                                        │
│  本月剩余检测次数：0/1                  │
│                                        │
│  ┌────────────────────────────────┐   │
│  │  升级Pro版，解锁完整功能         │   │
│  │  ✓ 完整9平台排名               │   │
│  │  ✓ 监控仪表盘                  │   │
│  │  ✓ 竞品对比                    │   │
│  │  ✓ 预警通知                    │   │
│  │                                │   │
│  │  [立即升级 ¥399/月]            │   │
│  └────────────────────────────────┘   │
└──────────────────────────────────────┘
```

---

## 四、导航栏改造

### 付费用户标识
- 导航栏右侧：用户手机号 + 标签
- 免费用户：灰色标签「免费版」
- Pro用户：橙色标签「Pro」
- 企业用户：深蓝标签「企业版」

### 监控仪表盘入口
- 导航中「监控仪表盘」链接
- 免费用户点击后弹出付费引导弹窗（不是锁页面，而是弹窗提示升级）
- Pro/企业用户直接进入仪表盘

---

## 五、技术要求

1. 前端路由新增：/pricing（定价页）
2. 前端路由改造：/profile 增加订阅管理子页
3. 后端新增5个订阅API
4. 后端改造2个现有API（detect增加次数检查）
5. 数据库新增2张表（subscriptions、free_quota）
6. 支付暂时模拟，预留支付回调接口
7. UI风格参照UI_LAYOUT_SPEC.md的全局设计规范（橙色主色#FF6B35）
