"""Quant Sniper Ultimate v8.0 — Streamlit web app for Streamlit Community Cloud."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st

import quant_engine as qe

PLOTLY_CONFIG = {"scrollZoom": True, "displaylogo": False}


@dataclass
class AnalysisParams:
    symbol: str
    end_date: str
    start_date: str
    lookback: str
    future_days: int
    auto_dfe: bool
    periods: list[float] | None
    show_st: bool
    st_len: int
    st_mult: float
    show_td: bool
    show_td_setup: bool
    show_td_cd: bool
    show_td_nums: bool
    cd_tgt: int
    cd_ext: int
    show_sqz: bool
    sqz_bb_len: int
    sqz_bb_mult: float
    sqz_kc_len: int
    sqz_kc_mult: float


def run_analysis(params: AnalysisParams) -> dict:
    """Run the full analysis pipeline; returns fig, log text, and detected periods."""
    log: list[str] = []
    symbol = params.symbol.strip() or qe.DEFAULT_SYMBOL
    end_date = params.end_date.strip() or date.today().isoformat()
    start_date = params.start_date.strip()
    lb_str = params.lookback.strip()
    future_days = params.future_days

    log.append(f"Fetching Data for {symbol}...")

    explicit_lookback = None
    auto_lookback = False
    if start_date:
        pass
    elif lb_str:
        explicit_lookback = int(lb_str)
        start_date = (pd.Timestamp(end_date) - pd.offsets.BDay(explicit_lookback)).date().isoformat()
    else:
        auto_lookback = True
        start_date = (pd.Timestamp(end_date) - pd.offsets.BDay(qe.MAX_LOOKBACK_BARS)).date().isoformat()
        log.append("Auto lookback: fetching max window for DFE + sweep…")

    close, high, low, volume = qe.download_ohlcv(symbol, start_date, end_date)
    log.append(f"  Downloaded {len(close)} bars ({start_date} → {end_date})")
    if len(close) < qe.MIN_LOOKBACK_BARS:
        log.append(
            f"  Warning: only {len(close)} bars available; "
            f"recommended minimum is {qe.MIN_LOOKBACK_BARS}."
        )

    if auto_lookback:
        log.append("Auto-selecting lookback (period-driven min + stability sweep)…")

    cfg = qe.resolve_cycle_config(
        close, high, low, volume,
        periods_manual=params.periods,
        auto_dfe=params.auto_dfe,
        future_days=future_days,
        explicit_lookback=explicit_lookback,
        auto_lookback=auto_lookback,
        log_cb=lambda m: log.append(m),
    )
    close, high, low, volume = cfg["close"], cfg["high"], cfg["low"], cfg["volume"]
    periods = cfg["periods"]
    for msg in cfg["messages"]:
        log.append(msg)

    period_str = ", ".join(f"{p:.1f}" for p in periods)
    log.append(
        f"Cycle periods: [{period_str}] d  (source: {cfg['periods_source']})  "
        f"lookback: {cfg['lookback_bars']} bars"
    )

    m = qe.metrics_for_window(close, periods, future_days)
    overlay, cs = m["overlay"], m["cycle_stats"]
    log.append(f"Fit R²={m['combined_r2']:.4f}  ranked={[int(p) for p in m['ranked_periods']]}")
    log.append(m["timing_report"])

    trend, st_line = qe.calculate_supertrend(high, low, close, params.st_len, params.st_mult)
    _, _, sigs = qe.td_sequential(close, high, low, params.cd_tgt, params.cd_ext)
    sqz_val, _, _, _, _, _ = qe.squeeze_momentum(
        close, high, low,
        params.sqz_bb_len, params.sqz_bb_mult, params.sqz_kc_len, params.sqz_kc_mult,
    )
    cmf_val = qe.chaikin_money_flow(close, high, low, volume)

    trade_advice = qe.analyze_trade_state(close, low, high, trend, st_line, sigs, sqz_val, cmf_val)
    log.append(trade_advice)

    fig = qe.build_plotly_chart(
        close, overlay, cs, symbol, periods, high, low,
        params.show_td, params.show_td_setup, params.show_td_cd, params.show_td_nums,
        params.cd_tgt, params.cd_ext,
        params.show_sqz, params.sqz_bb_len, params.sqz_bb_mult, params.sqz_kc_len, params.sqz_kc_mult,
        params.show_st, params.st_len, params.st_mult, cmf_val,
        projection_extrema=m.get("projection_extrema"),
    )

    return {
        "fig": fig,
        "log": "\n".join(log),
        "symbol": symbol,
        "periods": periods,
    }


def build_sidebar() -> AnalysisParams | None:
    st.sidebar.title("Ultimate Quant Sniper")
    st.sidebar.caption("v8.0 — Dynamic Frequency Extraction (DFE)")

    st.sidebar.subheader("Cycle Parameters")
    symbol = st.sidebar.text_input("Ticker Symbol", value=qe.DEFAULT_SYMBOL)
    end_date = st.sidebar.text_input("End Date (YYYY-MM-DD)", value=date.today().isoformat())
    start_date = st.sidebar.text_input("Start Date (optional)", value="", help="Leave blank → auto lookback (678–900)")
    lookback = st.sidebar.text_input("Lookback Bars (optional)", value="")
    future_days = st.sidebar.number_input("Future Projection (days)", min_value=1, max_value=365, value=qe.DEFAULT_FUTURE_DAYS)

    auto_dfe = st.sidebar.checkbox("Auto-detect cycle periods (DFE)", value=True)
    st.sidebar.markdown("**Cycle Periods (Days)**")
    c1, c2, c3 = st.sidebar.columns(3)
    p1 = c1.text_input("P1", value=str(qe.DEFAULT_PERIODS[0]), disabled=auto_dfe, label_visibility="collapsed")
    p2 = c2.text_input("P2", value=str(qe.DEFAULT_PERIODS[1]), disabled=auto_dfe, label_visibility="collapsed")
    p3 = c3.text_input("P3", value=str(qe.DEFAULT_PERIODS[2]), disabled=auto_dfe, label_visibility="collapsed")

    periods_manual = None
    if not auto_dfe:
        raw = [p.strip() for p in (p1, p2, p3) if p.strip()]
        periods_manual = [float(x) for x in raw] if raw else None

    st.sidebar.divider()
    st.sidebar.subheader("SuperTrend")
    show_st = st.sidebar.checkbox("启用 SuperTrend 主图红绿带", value=True)
    st_col1, st_col2 = st.sidebar.columns(2)
    st_len = st_col1.number_input("ATR Period", min_value=1, value=10)
    st_mult = st_col2.number_input("Multiplier", min_value=0.1, value=3.0, step=0.1)

    st.sidebar.divider()
    st.sidebar.subheader("TD Sequential (DeMark)")
    show_td = st.sidebar.checkbox("启用 TD 信号叠加", value=True)
    show_td_setup = st.sidebar.checkbox("显示 TD9 Setup 标记", value=True)
    show_td_cd = st.sidebar.checkbox("显示 TD13/15 Countdown", value=True)
    show_td_nums = st.sidebar.checkbox("显示逐根计数 (缩放后看)", value=False)
    cd_col1, cd_col2 = st.sidebar.columns(2)
    cd_tgt = cd_col1.number_input("Countdown", min_value=1, value=13)
    cd_ext = cd_col2.number_input("Extended", min_value=1, value=15)

    st.sidebar.divider()
    st.sidebar.subheader("Squeeze Momentum [LazyBear]")
    show_sqz = st.sidebar.checkbox("启用 SQZ 动量副图", value=True)
    sqz_col1, sqz_col2 = st.sidebar.columns(2)
    sqz_bb_len = sqz_col1.number_input("BB Length", min_value=1, value=20)
    sqz_bb_mult = sqz_col2.number_input("BB Mult", min_value=0.1, value=2.0, step=0.1)
    sqz_col3, sqz_col4 = st.sidebar.columns(2)
    sqz_kc_len = sqz_col3.number_input("KC Length", min_value=1, value=20)
    sqz_kc_mult = sqz_col4.number_input("KC Mult", min_value=0.1, value=1.5, step=0.1)

    run_clicked = st.sidebar.button("▶ Run & Analyze", type="primary", use_container_width=True)

    params = AnalysisParams(
        symbol=symbol,
        end_date=end_date,
        start_date=start_date,
        lookback=lookback,
        future_days=int(future_days),
        auto_dfe=auto_dfe,
        periods=periods_manual,
        show_st=show_st,
        st_len=int(st_len),
        st_mult=float(st_mult),
        show_td=show_td,
        show_td_setup=show_td_setup,
        show_td_cd=show_td_cd,
        show_td_nums=show_td_nums,
        cd_tgt=int(cd_tgt),
        cd_ext=int(cd_ext),
        show_sqz=show_sqz,
        sqz_bb_len=int(sqz_bb_len),
        sqz_bb_mult=float(sqz_bb_mult),
        sqz_kc_len=int(sqz_kc_len),
        sqz_kc_mult=float(sqz_kc_mult),
    )
    return params if run_clicked else None


def main() -> None:
    st.set_page_config(
        page_title="Quant Sniper Ultimate",
        page_icon="📈",
        layout="wide",
    )
    st.title("Ultimate Quant Sniper")
    st.caption("Cycle + TD9 + SQZ Momentum + SuperTrend + CMF")

    params = build_sidebar()

    if params is None:
        st.info("在左侧配置参数后，点击 **▶ Run & Analyze** 开始分析。")
        if "last_result" in st.session_state:
            result = st.session_state["last_result"]
            _render_result(result)
        return

    try:
        with st.spinner("分析中，请稍候（自动 lookback 可能需要 30–90 秒）…"):
            result = run_analysis(params)
        st.session_state["last_result"] = result
        _render_result(result)
    except qe.DataFetchError as exc:
        st.error(str(exc))
    except Exception:
        st.error("分析失败，请检查参数或稍后重试。")
        st.code(traceback.format_exc())


def _render_result(result: dict) -> None:
    st.plotly_chart(result["fig"], use_container_width=True, config=PLOTLY_CONFIG)

    html_bytes = result["fig"].to_html(
        include_plotlyjs="cdn",
        config=PLOTLY_CONFIG,
    ).encode("utf-8")
    st.download_button(
        label="下载 HTML 图表",
        data=html_bytes,
        file_name=f"{result['symbol']}_quant_sniper.html",
        mime="text/html",
    )

    with st.expander("Engine Output", expanded=True):
        st.code(result["log"], language=None)

    period_str = ", ".join(f"{p:.1f}" for p in result["periods"])
    st.caption(f"Detected periods: [{period_str}] d")


if __name__ == "__main__":
    main()
