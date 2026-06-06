# CycleAnalysis / Quant Sniper

基于周期分析的股票量化图表工具，整合 **Cycle 谐波拟合**、**TD Sequential**、**Squeeze Momentum**、**SuperTrend** 与 **Chaikin Money Flow (CMF)**，通过 Streamlit 在浏览器中运行。

> English documentation: [README_EN.md](README_EN.md)

原版桌面程序为 `../nya_V6.py`（Tkinter GUI），本目录为 Web 部署版本，引擎逻辑与桌面版一致。

---

## 文件说明

| 文件 | 作用 |
|------|------|
| **`streamlit_app.py`** | **应用入口**。Streamlit Community Cloud 的 Main file path 应指向此文件。负责侧边栏参数 UI、调用分析流程、展示 Plotly 图表、引擎日志与 HTML 下载按钮。 |
| **`quant_engine.py`** | **量化引擎**（从 `nya_V6.py` 抽取，无 GUI 依赖）。包含数据下载、周期检测 (DFE)、lookback 优选、指标计算、交易状态分析与 Plotly 图表构建。云端与本地分析的核心逻辑均在此文件。 |
| **`nya_V6_backup.py`** | **原版完整备份**。`TD9ETC/nya_V6.py` 的副本，供对照或回滚；不参与 Web 应用运行。 |
| **`requirements.txt`** | **Python 依赖清单**。Streamlit Cloud 部署时据此安装 `streamlit`、`yfinance`、`plotly`、`scipy` 等包。 |
| **`.python-version`** | **Python 版本锁定**。指定运行环境为 Python 3.12，避免云端使用过高版本导致兼容问题。 |
| **`.gitignore`** | **Git 忽略规则**。排除 `.venv/`、`tmp/`、`__pycache__/` 等无需上传的目录与缓存。 |
| **`README.md`** | 中文说明文档。 |
| **`README_EN.md`** | 英文说明文档。 |

### 运行时自动生成的目录（已被 `.gitignore` 忽略）

| 路径 | 作用 |
|------|------|
| `tmp/yf_cache/` | yfinance 时区缓存，减少重复请求 |
| `tmp/quant_sniper_v8.html` | 引擎默认 HTML 输出路径（Web 版主要通过页面内嵌图表展示，可选下载 HTML） |

---

## 功能概览

- **Cycle**：动态频率提取 (DFE) 或手动指定周期，谐波拟合与未来投影
- **SuperTrend**：主图红绿趋势带
- **TD Sequential**：TD9 Setup、TD13/15 Countdown 信号
- **Squeeze Momentum**：LazyBear 挤压动量副图
- **CMF**：Chaikin 资金流量副图
- **量化决策**：综合趋势、TD、SQZ、CMF 的交易建议输出

---

## 本地运行

```powershell
cd d:\Study\StockMart\TD9ETC\TD
pip install -r requirements.txt
streamlit run streamlit_app.py
```

浏览器打开 **http://localhost:8501**，在左侧配置参数后点击 **▶ Run & Analyze**。

首次自动 lookback 分析约需 30–90 秒。

---

## 部署到 Streamlit Community Cloud

1. 将本目录内容推送到 GitHub 仓库（如 `Deemolotus/CycleAnalysis`）
2. 打开 [share.streamlit.io](https://share.streamlit.io) → **Create app** → **From existing repo**
3. 配置：
   - **Repository**：你的仓库名
   - **Branch**：`main`
   - **Main file path**：`streamlit_app.py`
4. 点击 **Deploy**，等待依赖安装完成

无需配置 Secrets（仅使用 yfinance 公开行情数据）。

---

## 与原版的关系

| 版本 | 文件 | 界面 |
|------|------|------|
| 桌面版 | `TD9ETC/nya_V6.py` | Tkinter 窗口，本地运行 |
| Web 版 | 本目录 `streamlit_app.py` + `quant_engine.py` | 浏览器，可部署到 Streamlit Cloud |

修改引擎逻辑时，优先改 `quant_engine.py`；`nya_V6.py` 与 Web 版目前独立维护。

---

## 许可证
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file in the repository root.

见仓库根目录 `LICENSE`（MIT）。
