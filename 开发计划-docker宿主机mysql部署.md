# 开发计划-docker宿主机mysql部署
创建时间：2026-03-28
当前状态：已完成
执行目标：将当前项目调整为通过 Docker 连接宿主机 MySQL，并在本地完成前后端部署与验证。
步骤：[x] 梳理当前 Docker 与数据库接入方式  [x] 编写部署方案与计划  [x] 调整 Docker 编排和环境配置  [x] 检查并补齐宿主机 MySQL 库表与账号  [x] 启动并验证容器  [x] 回填结果
改动明细：
- 新增 `.env` 本地运行环境文件，初始化后台登录账号为 `zhangbo/zhangbo`。
- 调整 `.env`，将 `WERSS_AUTH_WEB` 改为 `False`，切换到不依赖浏览器的 API 授权实现。
- 更新 `.gitignore`，忽略本地 `.env`。
- 新增 `compose/docker-compose.host-mysql.yaml`，部署方式改为 Docker 后端容器连接宿主机 MySQL：`host.docker.internal:3306`。
- 新增 `Dockerfile.local`，使用轻量 Python 运行镜像构建本地容器，避免大基础镜像拉取导致部署失败。
- 修复 `driver/wx.py` 与 `driver/wx_api.py` 中 `check_lock` 逻辑，改为优先检查锁文件并清理超时锁，避免重复点击“刷新授权”时反复拉起授权线程。
- 新增 `driver/test_wx_lock.py`，覆盖 Web/API 两套授权实现的锁文件判定逻辑。
- 宿主机 MySQL 中创建数据库 `we_mp_rss`，由应用启动时自动完成建表和初始化用户。
校验结果：
- `docker compose -f compose/docker-compose.host-mysql.yaml up -d --build` 成功完成，容器 `we-mp-rss-backend-host-mysql` 状态为 `Up`。
- `docker compose -f compose/docker-compose.host-mysql.yaml ps` 显示 `0.0.0.0:8001->8001/tcp` 端口映射正常。
- `docker logs --tail 200 we-mp-rss-backend-host-mysql` 显示已成功连接 MySQL、完成模型同步、初始化用户 `zhangbo`，并启动 Uvicorn。
- `curl http://localhost:8001/` 返回前端 HTML 页面。
- `curl http://localhost:8001/api/docs` 返回 200。
- `curl -X POST http://localhost:8001/api/v1/wx/auth/login --data 'username=zhangbo&password=zhangbo'` 成功返回 `access_token`。
- `docker exec we-mp-rss-backend-host-mysql python -m unittest driver.test_wx_lock -v` 通过，Web/API 两套锁逻辑测试均为 `OK`。
- `docker exec we-mp-rss-backend-host-mysql python -c "import os; import driver.base as b; ..."` 确认 `WERSS_AUTH_WEB=False`，当前授权实现为 `driver.wx_api`。
- `GET /api/v1/wx/auth/qr/code` 后，`HEAD /static/wx_qrcode.png` 返回 `200 OK`，二维码文件已生成。
- `mysql -uzhangbo -pzhangbo -D we_mp_rss -e "SHOW TABLES; SELECT id, username FROM users;"` 确认数据库表已创建，用户表存在 `zhangbo`。
