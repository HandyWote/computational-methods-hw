# 计算方法课程作业仓库

黄应辉 2024611031 —— 《计算方法》课程作业归档。

## 作业目录

| 作业 | 主题 | 目录 |
|---|---|---|
| 作业一 | 拉格朗日插值与牛顿插值的比较 | [`01-interpolation/`](01-interpolation/) |
| 作业二 | 数值积分算法的比较实现 | `02-integration/`（待完成） |

## 环境与运行

- Python ≥ 3.12，包管理使用 [uv](https://docs.astral.sh/uv/)
- 每个作业目录都是独立的 uv 项目，进入对应目录后：

```bash
uv run main.py          # 交互演示
uv run python -m doctest *.py   # 运行全部 doctest
```

## 每个作业目录的结构

```
NN-topic/
├── README.md            # 作业任务书
├── pyproject.toml       # 该作业的 uv 项目配置
├── *.py                 # 实验代码
├── docs/                # 实验报告（Markdown + 提交用 PDF）
└── figures/             # 实验产生的图（不入库）
```
