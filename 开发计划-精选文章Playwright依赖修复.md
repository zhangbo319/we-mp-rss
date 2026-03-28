# 开发计划-精选文章Playwright依赖修复
创建时间：2026-03-29
当前状态：已完成
执行目标：定位“订阅管理 -> 添加精选文章”失败原因，并修复本地 Docker 环境下 Playwright 浏览器及系统依赖不可用的问题。
步骤：[x] 复现失败并收集错误信息  [x] 检查容器内 Playwright 浏览器与系统依赖状态  [x] 调整本地 Docker 镜像构建依赖源  [x] 重建并验证容器运行环境  [x] 回归验证精选文章任务
改动明细：
- 复现文章链接 `https://mp.weixin.qq.com/s/ptKc4KY60vODvj1eK1C85w` 的精选文章任务失败。
- 确认当前运行容器中不存在 `/root/.cache/ms-playwright`，说明镜像未携带 Playwright 浏览器运行时。
- 手工执行 `python -m playwright install webkit` 后确认浏览器二进制可下载，但 `--with-deps` 阶段因 `deb.debian.org` 网络连接失败，无法安装系统库。
- 更新 `Dockerfile.local`，将 Debian 源切换为清华镜像并增加 `apt-get` 重试，降低构建阶段拉取 Playwright 依赖时的网络失败概率。
- 使用重建完成的新镜像重新创建本地容器，确认运行容器内存在 `/root/.cache/ms-playwright/webkit-2203/pw_run.sh`。
- 重新调用精选文章任务接口，文章链接 `https://mp.weixin.qq.com/s/ptKc4KY60vODvj1eK1C85w` 返回成功，标题为 `幻觉`。
校验结果：
- `GET /api/v1/wx/mps/featured/article/tasks/{task_id}` 返回 `status=failed`，错误为 `BrowserType.launch: Executable doesn't exist...`
- `docker exec ... ls /root/.cache/ms-playwright` 返回不存在。
- `docker exec ... python -m playwright install --with-deps webkit` 失败，报错为 `Unable to connect to deb.debian.org:http`。
- `docker compose -f compose/docker-compose.host-mysql.yaml build --no-cache backend` 完成，生成新镜像 `we-mp-rss-backend:host-mysql-local`，镜像环境变量中包含 `BROWSER_TYPE=webkit`。
- `docker compose -f compose/docker-compose.host-mysql.yaml up -d --force-recreate backend` 完成，容器正常启动。
- `docker exec we-mp-rss-backend-host-mysql sh -lc 'test -f /root/.cache/ms-playwright/webkit-2203/pw_run.sh && echo PW_OK'` 输出 `PW_OK`。
- `curl http://localhost:8001/api/docs` 验证服务可访问。
- `POST /api/v1/wx/mps/featured/article` 返回任务 `60baa86b-12c3-4277-93d0-e168ce7b671a`。
- `GET /api/v1/wx/mps/featured/article/tasks/60baa86b-12c3-4277-93d0-e168ce7b671a` 返回 `status=success`，消息为 `精选文章添加成功`，文章标题为 `幻觉`。
