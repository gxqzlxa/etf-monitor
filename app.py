import streamlit as st
import pandas as pd
import akshare as ak
import time

# 页面配置
st.set_page_config(page_title="ETF 监控神器", layout="wide", page_icon="📈")

# 侧边栏配置
st.sidebar.title("⚙️ 监控设置")
st.sidebar.markdown("在这里输入你的 ETF 代码，用逗号分隔")
default_codes = "512880, 588000, 159915, 510300, 512200"
input_codes = st.sidebar.text_area("ETF 代码列表", default_codes, height=200)

# 核心数据获取函数
@st.cache_data(ttl=60) # 缓存60秒，避免频繁请求
def get_market_data(codes):
    code_list = [x.strip() for x in codes.split(',') if x.strip()]
    results = []
    
    # 这里为了演示简化了逻辑，实际使用时建议配合 akshare 的批量接口
    try:
        # 获取实时行情
        df_spot = ak.fund_etf_spot_em()
        
        for code in code_list:
            row = df_spot[df_spot['代码'] == code]
            if not row.empty:
                # 获取历史数据计算指标 (简化版，实际需优化性能)
                # 注意：在云端运行需注意请求频率限制
                try:
                    df_hist = ak.fund_etf_hist_em(symbol=code, period="daily", adjust="qfq")
                    if len(df_hist) >= 20:
                        close = df_hist['收盘'].values
                        # 简单的 RSI 计算
                        delta = close[-1] - close[-2]
                        # 这里仅作演示，真实 RSI 需计算 6 日平均
                        rsi = 50 # 占位符
                        
                        # 20日动量
                        mom_20 = (close[-1] / close[-20] - 1) * 100
                        
                        signal = "观望"
                        if rsi < 20: signal = "🔴 买入"
                        elif mom_20 > 5: signal = "🟢 突破"
                        
                        results.append({
                            "代码": code,
                            "名称": row['名称'].values[0],
                            "现价": row['最新价'].values[0],
                            "涨跌幅": row['涨跌幅'].values[0],
                            "信号": signal
                        })
                except:
                    pass
                    
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"数据获取失败: {e}")
        return pd.DataFrame()

# 主界面
st.title("📱 掌上 ETF 监控雷达")
st.markdown("实时监控 50+ 标的，捕捉买卖点")

# 自动刷新按钮
if st.button('🔄 立即刷新数据'):
    with st.spinner('正在扫描市场...'):
        df = get_market_data(input_codes)
        
        if not df.empty:
            # 高亮显示有信号的
            st.subheader("🔔 监控结果")
            
            # 过滤出有信号的优先显示
            signals = df[df['信号'] != "观望"]
            if not signals.empty:
                st.success(f"发现 {len(signals)} 个机会！")
                st.dataframe(signals, use_container_width=True)
            else:
                st.info("当前暂无触发信号的标的")
                
            # 显示全部数据
            with st.expander("查看全部监控列表"):
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("未获取到数据，请检查代码或稍后重试")

# 底部说明
st.markdown("---")
st.caption("数据源：AkShare | 刷新频率：手动或自动")
