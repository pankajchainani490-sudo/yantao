# 幻灯片页面简版拷贝稿

适用场景：

- 想快速把内容粘贴到 PowerPoint
- 不想看长篇备注

## 1. 封面

基于机器学习的恶意流量识别系统

流量分析、机器学习、网络攻防一体化演示平台

## 2. 项目背景与意义

- 恶意流量持续增长
- 传统规则检测泛化能力有限
- 机器学习可从流量特征中自动学习分类边界
- 本项目兼顾识别、展示和部署

## 3. 项目目标

- 识别正常流量、ARP 攻击、DDoS 攻击、木马流量
- 提取包长、端口、发包频率等特征
- 使用决策树和随机森林完成分类
- 输出告警、风险等级和黑名单结果
- 支持 Ubuntu 部署与答辩展示

## 4. 系统总体架构

- 数据层：raw / interim / processed / sample
- 算法层：特征提取、训练、评估、推理
- 服务层：FastAPI + SQLite
- 展示层：React 前端多页面系统

## 5. 数据来源与标签设计

- 数据策略：公共数据集 + 隔离实验抓包
- 公共数据集：CIC-IDS2017、CIC-DDoS2019、CTU-13
- 标签映射：benign / arp_spoof / ddos / trojan

## 6. 特征工程设计

- 源端口、目标端口
- 平均/最大/最小包长
- 包长标准差
- 每秒包数、每秒字节数
- 流持续时间
- 包长范围、每包字节数、系统端口标记

## 7. 模型设计与训练流程

- 模型：Decision Tree、Random Forest
- 流程：样本整理 -> 特征构建 -> 数据划分 -> 训练评估 -> 保存模型

## 8. 模型结果与性能指标

- Accuracy
- Precision
- Recall
- F1-score
- 混淆矩阵
- 特征重要性

## 9. 后端服务设计

- /predict
- /dashboard/summary
- /alerts
- /blacklist
- /replay/status
- /metrics/summary

## 10. 前端展示系统

- Dashboard
- Detection
- Replay
- Blacklist
- Metrics
- Settings

## 11. 黑名单与预警机制

- 恶意预测生成告警
- 重复命中达到阈值后自动拉黑
- 支持人工手动加入和删除
- 模型输出 + 阈值规则 + 人工管理

## 12. 系统演示流程

1. Dashboard 总览
2. Detection 单条识别
3. Blacklist 管理
4. Replay 分阶段演示
5. Metrics 指标说明

## 13. 测试与验证

- pytest 阶段验证
- 特征流水线验证
- 模型训练验证
- API 接口验证
- 部署就绪验证

## 14. Ubuntu 部署方案

- Ubuntu 22.04
- nginx 托管前端
- uvicorn + systemd 启动后端
- SQLite 作为第一阶段数据库
- 已提供部署模板与脚本

## 15. 总结与展望

- 已完成从数据到展示的完整闭环
- 已完成训练、识别、前后端、测试和部署准备
- 后续可扩展真实数据集、深度学习和实时抓包能力
