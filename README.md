# Malicious Traffic ML Detection System

基于机器学习的恶意流量识别系统，覆盖流量数据规范、特征提取、决策树/随机森林训练、后端识别服务、黑名单管理、回放演示和前端展示。

当前已经完成：

- 数据标签与样本清单规范
- 特征提取流水线
- 决策树与随机森林模型训练
- FastAPI 后端识别与黑名单接口
- React + TypeScript 前端展示页
- `pytest` 自动化验证

## 功能概览

- 识别类别：`benign`、`arp_spoof`、`ddos`、`trojan`
- 特征字段：包长、端口、发包频率及其衍生统计
- 模型：Decision Tree、Random Forest
- 后端：FastAPI + SQLite
- 前端：React + TypeScript + Vite
- 测试：pytest

## 目录结构

```text
backend/   FastAPI 服务、模型推理、API 测试
frontend/  React 展示页、检测交互、黑名单与回放界面
ml/        数据、模型、训练报告、配置
docs/      架构、数据、测试、部署、演示文档
deploy/    Ubuntu/nginx/systemd 等部署模板占位
scripts/   数据处理、训练、开发辅助脚本
ppt/       后续答辩图表与演示稿素材
```

## Windows 本地运行

### 1. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python ..\scripts\train\build_processed_dataset.py
python ..\scripts\train\train_models.py
uvicorn app.main:app --reload
```

后端默认地址：`http://127.0.0.1:8000`

接口文档：`http://127.0.0.1:8000/docs`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：`http://127.0.0.1:5173`

Vite 已配置 `/api` 代理到 `http://127.0.0.1:8000`。

### 3. 运行测试

```bash
cd backend
.venv\Scripts\python -m pytest -v
```

### 4. 构建前端

```bash
cd frontend
npm run build
```

## 当前已实现页面

- Overview Dashboard
- Detection
- Replay
- Blacklist
- Metrics
- Settings

## 当前已实现后端接口

- `GET /api/v1/health`
- `POST /api/v1/predict`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/trends`
- `GET /api/v1/dashboard/top-sources`
- `GET /api/v1/alerts`
- `GET /api/v1/blacklist`
- `POST /api/v1/blacklist`
- `DELETE /api/v1/blacklist/{id}`
- `POST /api/v1/replay/start`
- `GET /api/v1/replay/status`
- `GET /api/v1/metrics/summary`
- `GET /api/v1/settings`

## 当前验证状态

- 后端 `pytest`：通过
- 前端生产构建：通过

## 推荐演示顺序

1. 打开 Overview Dashboard，展示总体统计
2. 进入 Detection 页面，提交一条 DDoS 风格特征
3. 查看预测结果、风险等级与关键特征
4. 打开 Blacklist 页面，展示自动拉黑与手动增删
5. 打开 Replay 页面，按阶段启动演示
6. 打开 Metrics 页面，说明模型效果和特征重要性

## 后续待完成

- Ubuntu 部署模板与文档
- 答辩 PPT 文稿
- 更真实的数据集导入与训练扩展
- 展示页进一步图表化和大屏化
