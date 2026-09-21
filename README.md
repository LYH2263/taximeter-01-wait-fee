# 14-taximeter（打车计价）

Taximeter — 起步价 + 里程价 + 低速时长费 + 等候费（夜间加价系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4300 |
| API | http://localhost:9300 |

## 主链

录行程里程与低速时长 → 拆解车费 → 行程单

## 等候费模块

- 等候规则：免费等候分钟（不得为负）+ 超出后每分钟单价（必须为正），同一时刻只允许一条启用规则，冲突时 409 并点名两条标识。
- 接口：`GET/POST /api/wait-fee/rules`、`PUT /api/wait-fee/rules/{id}`、`POST /api/wait-fee/rules/{id}/deactivate`。
- 打表：`POST /api/fare` 增加 `wait_min`（负值整单拒绝且不写记录）；计入分钟 = max(0, 等候 − 免费)，应付 = 起步 + 里程 + 低速 + 等候费；`persist=false` 只读试算不写 `calc_runs`。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
