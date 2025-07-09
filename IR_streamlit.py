import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.integrate import quad
# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']

# 应用样式
st.set_page_config(
    page_title="飞机红外辐射特性分析系统",
    page_icon="✈✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .stApp {
        background-color: #2D2D30;
        color: #DCDCDC;
    }
    .st-b7 {
        background-color: #1E1E1E !important;
        border: 1px solid #3F3F46 !important;
        color: #DCDCDC !important;
    }
    .st-bb {
        background-color: #3E3E40 !important;
        color: #FFFFFF !important;
        border: 1px solid #3F3F46 !important;
    }
    .st-bb:hover {
        background-color: #0078D7 !important;
    }
    .st-bb:active {
        background-color: #005A9E !important;
    }
    .st-eb {
        background-color: #0078D7 !important;
    }
    .stSelectbox, .stNumberInput, .stTextInput, .stTextArea {
        background-color: #1E1E1E;
        color: #DCDCDC;
    }
    .css-1d391kg, .css-1d391kg:hover {
        border: 1px solid #3F3F46;
    }
    .css-1x8cf1d {
        background-color: #1E1E1E;
    }
    .css-1v3fvcr {
        background-color: #2D2D30;
    }
    .css-1oe5cao {
        background-color: #1E1E1E;
    }
    .st-cj {
        background-color: #1E1E1E;
    }
    .css-1d391kg {
        background-color: #1E1E1E;
        border: 1px solid #3F3F46;
    }
    .css-1aumxhk {
        color: #DCDCDC;
    }
    .stAlert {
        background-color: #1E1E1E !important;
        border: 1px solid #3F3F46 !important;
    }
    .st-ae {
        background-color: #1E1E1E;
    }
    .css-1v0mbdj {
        background-color: #1E1E1E;
    }
    .stProgress > div > div > div > div {
        background-color: #0078D7;
    }
    .st-bq {
        border-color: #3F3F46;
    }
    .css-1r6slb0 {
        background-color: #1E1E1E;
        border: 1px solid #3F3F46;
    }
    .css-1r6slb0:hover {
        background-color: #0078D7;
    }
</style>
""", unsafe_allow_html=True)

def radiation_calculations(params, s_value, angle_mode='horizontal'):
    """执行辐射计算"""
    # 物理常数
    c1 = 3.7415e-16
    c2 = 1.438e-2
    s4 = np.pi * params['Rp']**2
    
    # 1. 蒙皮辐射计算
    if params['H'] <= 11000:
        T0 = 288.2 - 0.0065 * params['H']
    elif params['H'] <= 20000:
        T0 = 216.7
    elif params['H'] <= 32000:
        T0 = 216.7 + 0.001 * (params['H'] - 20000)
    else:
        T0 = 216.7
    
    Tm = T0 * (1 + params['r'] * (params['gama'] - 1) / 2 * params['Ma']**2)
    
    def M(x):
        return c1 / x**5 / (np.exp(c2 / (x * Tm)) - 1)
    
    L = params['emissivity_skin'] / np.pi * quad(M, params['l1']/1e6, params['l2']/1e6)[0]
    
    # 2. 发动机喷口辐射
    Tp = params['tp_afterburner'] if params['jl'] == 1 else params['tp_normal']
    
    def Mp(x):
        return c1 / x**5 / (np.exp(c2 / (x * Tp)) - 1)
    
    Lp = params['emissivity_nozzle'] / np.pi * quad(Mp, params['l1']/1e6, params['l2']/1e6)[0]
    
    # 3. 尾焰辐射
    Tw = params['tw_base']
    if params['fdj'] == 1:
        Tw = 0.85 * Tw
    else:
        Tw = 0.9 * Tw
    
    def Mw(x):
        return c1 / x**5 / (np.exp(c2 / (x * Tw)) - 1)
    
    Lw = params['emissivity_flame'] / np.pi * quad(Mw, params['l1']/1e6, params['l2']/1e6)[0]
    
    # 准备角度数据
    myBeta = np.linspace(0, 2*np.pi, 360)
    results = np.zeros_like(myBeta)
    Im_arr = np.zeros_like(myBeta)
    Ip_arr = np.zeros_like(myBeta)
    Iw_arr = np.zeros_like(myBeta)
    
    # 角度分区计算
    for i, beta in enumerate(myBeta):
        if 0 <= beta < np.arctan(1/5):
            z = 0
        elif beta < np.pi/2:
            z = 1
        elif beta < (np.pi - np.arctan(0.2)):
            z = 2
        elif beta < (np.pi + np.arctan(0.2)):
            z = 3
        elif beta < 3*np.pi/2:
            z = 4
        elif beta < (2*np.pi - np.arctan(0.2)):
            z = 5
        else:
            z = 6
            
        s = params['s1'] * np.abs(np.cos(beta)) + s_value * np.abs(np.sin(beta))
        Im = s * L
        Im_arr[i] = Im
        
        # 根据不同区域计算辐射
        if z == 0:
            Sw = 0
            Ip = 0
        elif z == 1:
            Sw = (params['lwy'] * np.sin(beta) - np.cos(beta))**2 / (params['lwy'] * np.sin(beta))
            Ip = 0
        elif z == 2:
            Sw = (params['lwy'] * np.sin(beta) - np.abs(np.cos(beta)))**2 / (params['lwy'] * np.sin(beta)) + s4 * np.abs(np.cos(beta))
            Sp = np.pi * np.abs(np.cos(beta))**2
            Ip = Lp * Sp
        elif z == 3:
            Sw = s4 * np.abs(np.cos(beta))
            Sp = np.pi * np.abs(np.cos(beta))**2
            Ip = Lp * Sp
        elif z == 4:
            Sw = (params['lwy'] * np.abs(np.sin(beta)) - np.abs(np.cos(beta)))**2 / (params['lwy'] * np.abs(np.sin(beta))) + s4 * np.abs(np.cos(beta))
            Sp = np.pi * np.abs(np.cos(beta))**2
            Ip = Lp * Sp
        elif z == 5:
            Sw = (params['lwy'] * np.abs(np.sin(beta)) - np.abs(np.cos(beta)))**2 / (params['lwy'] * np.abs(np.sin(beta)))
            Ip = 0
        else:  # z == 6
            Sw = 0
            Ip = 0
            
        Iw = Lw * Sw
        Iw_arr[i] = Iw
        Ip_arr[i] = Ip
        
        # 总辐射强度
        if z in [2, 3, 4]:
            I = Im + Iw + Ip
        else:
            I = Im + Iw
            
        results[i] = I
        
    return myBeta, results, np.max(results), Im_arr, Iw_arr, Ip_arr

def calc_range_at_angle(params, intensity, angle, angle_type):
    """计算特定角度下的作用距离"""
    # 获取高度（转换为km）
    H_km = params['H'] / 1000.0
    
    # 确定波段（中波或长波）
    if "中波" in params['band']:
        # 中波红外大气透过率模型
        # 基础衰减系数 (km⁻¹)
        k_base = 0.2
        
        # 高度修正因子 (高度增加，透过率增加)
        h_factor = np.exp(-H_km / 10.0)  # 10km为特征高度
        
        # 气象条件修正因子
        weather_factors = {
            "晴天": 1.0,
            "多云": 0.8,
            "阴天": 0.6,
            "雨天": 0.2  # 雨天对长波影响更大
        }
        w_factor = weather_factors.get(params['weather'], 1.0)
        
        # 综合衰减系数
        k = k_base * h_factor * w_factor
    else:
        # 长波红外大气透过率模型
        # 基础衰减系数 (km⁻¹)
        k_base = 0.15
        
        # 高度修正因子
        h_factor = np.exp(-H_km / 8.0)  # 8km为特征高度
        
        # 气象条件修正因子
        weather_factors = {
            "晴天": 1.0,
            "多云": 0.8,
            "阴天": 0.6,
            "雨天": 0.2  # 雨天对长波影响更大
        }
        w_factor = weather_factors.get(params['weather'], 1.0)
        
        # 综合衰减系数
        k = k_base * h_factor * w_factor
    
    # 探测器参数
    D = params['detector_aperture']  # 探测器孔径(m)
    SNR_min = params['snr_threshold']  # 最小信噪比
    
    # 光学系统参数
    f_number = params['f_number']  # F数
    τ0 = params['optical_trans']  # 光学透过率
    
    # 探测器性能参数
    NETD = params['netd']  # 噪声等效温差(K)
    Δf = params['system_bandwidth']  # 系统带宽(Hz)
    # D_ratio = params['detector_resp']  # 探测器响应率(A/W)
    D_star = params['d_star']  # 比探测率(cm√Hz/W)
    pixel_size = params['pixel_size'] * 1e-6  # 敏感元尺寸(m)
    # t_int = params['integration_time'] / 1000.0  # 积分时间(s)
    
    # 计算探测器敏感元面积
    A_d = (pixel_size)**2  # m²
    
    # 计算接收面积
    A0 = np.pi * (D/2)**2  # 接收面积(m²)
    
    # 计算dW/dT (温度对辐射的变化率)
    # 使用简化模型：dW/dT ≈ 4σT^3，其中σ是Stefan-Boltzmann常数
    σ = 5.67e-8  # W/m²K⁴⁴⁴⁴⁴⁴⁴⁴
    T_bg = params['bg_temp']  # 背景温度(K) - 假设为300K
    dWdT = 4 * σ * T_bg**3  # W/m²K
    
    try:
        range_netd = np.sqrt(
            (intensity * τ0 * A0 * D_star * np.sqrt(A_d * Δf * 1e4)) /  # 注意单位转换
            (NETD * np.sqrt(4*f_number**2 + 1) * dWdT * SNR_min)
        ) / 1000.0  # 转换为km
        
        R_prev = range_netd
        for _ in range(5):  # 进行5次迭代
            τ_atm = np.exp(-k * R_prev)
            R = np.sqrt(
                (intensity * τ0 * τ_atm * A0 * D_star * np.sqrt(A_d * Δf * 1e4)) / 
                (NETD * np.sqrt(4*f_number**2 + 1) * dWdT * SNR_min)
            ) / 1000.0
            R_prev = R  # 更新迭代值
            
    except Exception as e:
        st.error(f"作用距离计算错误: {e}")
        # 使用简单的经验公式作为后备
        R = np.sqrt(intensity * τ0 * A0 * 1e6) / 1000.0  # km
    
    return R

def main():
    # 应用标题
    st.title("目标红外辐射特性分析及作用距离评估系统")
    st.markdown("---")
    
    # 创建选项卡
    tabs = ["目标红外辐射特性及作用距离仿真评估"]
    tab_selected = st.sidebar.radio("导航菜单", tabs)
    
    # 主分析选项卡
    if tab_selected == "目标红外辐射特性及作用距离仿真评估":
        with st.expander("目标参数设置", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("基本参数")
                gama = st.number_input("Gamma (γ):", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
                r = st.number_input("r:", min_value=0.5, max_value=1.0, value=0.82, step=0.01)
                s1 = st.number_input("S1 (m²):", min_value=0.1, max_value=50.0, value=8.3, step=0.1)
                s2 = st.number_input("S2 (m²):", min_value=0.1, max_value=50.0, value=26.61, step=0.1)
                s3 = st.number_input("S3 (m²):", min_value=0.1, max_value=150.0, value=96.37, step=0.1)
                Rp = st.number_input("Rp (m):", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
                lwy = st.number_input("尾焰长度 (lwy):", min_value=0.1, max_value=20.0, value=5.0, step=0.1)
                
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    l1 = st.number_input("波长范围起始 (μm):", min_value=1.0, max_value=12.0, value=3.0, step=0.1)
                with col_l2:
                    l2 = st.number_input("波长范围结束 (μm):", min_value=1.0, max_value=12.0, value=5.0, step=0.1)
                
                H = st.number_input("高度 H (m):", min_value=0, max_value=30000, value=12000, step=100)
                Ma = st.number_input("马赫数 (Ma):", min_value=0.1, max_value=5.0, value=2.0, step=0.1)
                engine_mode = st.selectbox("发动机类型:", ["常规模式", "加力模式"])
                fw = st.number_input("方位角 (deg):", min_value=0, max_value=360, value=75, step=1)
                fy = st.number_input("俯仰角 (deg):", min_value=0, max_value=90, value=75, step=1)
            
            with col2:
                st.subheader("辐射特性参数")
                emissivity_skin = st.number_input("蒙皮发射率:", min_value=0.1, max_value=1.0, value=0.7, step=0.05)
                emissivity_nozzle = st.number_input("喷口发射率:", min_value=0.1, max_value=1.0, value=0.8, step=0.05)
                emissivity_flame = st.number_input("尾焰发射率:", min_value=0.1, max_value=1.0, value=0.2, step=0.05)
                tw_base = st.number_input("尾焰基温 (K):", min_value=300, max_value=2000, value=750, step=10)
                tp_normal = st.number_input("常规温度 (K):", min_value=300, max_value=2000, value=600, step=10)
                tp_afterburner = st.number_input("加力温度 (K):", min_value=300, max_value=2000, value=1000, step=10)
                
                st.subheader("大气与探测器参数")
                band = st.selectbox("探测波段:", ["中波 (3-5μm)", "长波 (8-12μm)"])
                weather = st.selectbox("气象条件:", ["晴天", "多云", "阴天", "雨天"])
                bg_temp = st.number_input("背景温度 (K):", min_value=200, max_value=400, value=300, step=5)
                detector_aperture = st.number_input("探测器孔径 (m):", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
                snr_threshold = st.number_input("信噪比阈值:", min_value=1.0, max_value=20.0, value=5.0, step=0.1)
                f_number = st.number_input("光学系统F数:", min_value=1.0, max_value=16.0, value=4.0, step=0.1)
                optical_trans = st.number_input("光学透过率:", min_value=0.1, max_value=1.0, value=0.85, step=0.05)
                netd = st.number_input("NETD (mK):", min_value=1.0, max_value=100.0, value=20.0, step=1.0) / 1000.0
                system_bandwidth = st.number_input("系统带宽 (Hz):", min_value=1.0, max_value=1000.0, value=100.0, step=1.0)
                detector_resp = st.number_input("探测器响应率 (A/W):", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
                d_star = st.number_input("比探测率 D* (cm√Hz/W):", min_value=1e8, max_value=1e12, value=1e10, step=1e9, format="%.0e")
                pixel_size = st.number_input("敏感元尺寸 (μm):", min_value=1.0, max_value=50.0, value=15.0, step=1.0)
                integration_time = st.number_input("积分时间 (ms):", min_value=1.0, max_value=1000.0, value=10.0, step=1.0)
        
        # 组织参数
        params = {
            'gama': gama,
            'r': r,
            's1': s1,
            's2': s2,
            's3': s3,
            'Rp': Rp,
            'lwy': lwy,
            'l1': l1,
            'l2': l2,
            'H': H,
            'Ma': Ma,
            'jl': 1 if engine_mode == "加力模式" else 0,
            'fdj': 1 if engine_mode == "常规模式" else 2,
            'fwjiaodu': fw,
            'fyjiaodu': fy,
            'emissivity_skin': emissivity_skin,
            'emissivity_nozzle': emissivity_nozzle,
            'emissivity_flame': emissivity_flame,
            'tw_base': tw_base,
            'tp_normal': tp_normal,
            'tp_afterburner': tp_afterburner,
            'band': band,
            'weather': weather,
            'bg_temp': bg_temp,
            'detector_aperture': detector_aperture,
            'snr_threshold': snr_threshold,
            'f_number': f_number,
            'optical_trans': optical_trans,
            'netd': netd,
            'system_bandwidth': system_bandwidth,
            'detector_resp': detector_resp,
            'd_star': d_star,
            'pixel_size': pixel_size,
            'integration_time': integration_time
        }
        
        # 添加操作按钮
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        with col_btn1:
            btn_calc_horizontal = st.button("计算水平方向", use_container_width=True)
        with col_btn2:
            btn_calc_vertical = st.button("计算垂直方向", use_container_width=True)
        with col_btn3:
            btn_calc_range = st.button("计算作用距离包线", use_container_width=True)
        with col_btn4:
            btn_calculate_all = st.button("执行所有计算", use_container_width=True)
        
        # 绘制图表区域
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("水平方向辐射模式")
            if btn_calculate_all or btn_calc_horizontal:
                with st.spinner("计算水平方向辐射中..."):
                    beta_h, results_h, max_I_h, Im_arr_h, Iw_arr_h, Ip_arr_h = radiation_calculations(params, s2, 'horizontal')
                    
                    # 绘制水平方向辐射模式
                    fig1 = plt.figure(figsize=(8, 6))
                    ax1 = fig1.add_subplot(111, projection='polar')
                    ax1.plot(beta_h, results_h, 'r-', linewidth=2, label='总辐射')
                    ax1.plot(beta_h, Im_arr_h, 'b--', label='蒙皮辐射')
                    ax1.plot(beta_h, Iw_arr_h, 'g:', label='尾焰辐射')
                    ax1.plot(beta_h, Ip_arr_h, 'm-.', label='喷口辐射')
                    ax1.set_rlabel_position(22.5)
                    ax1.grid(True)
                    ax1.legend(loc='upper right', bbox_to_anchor=(1.15, 1.15))
                    st.pyplot(fig1)
                    
                    # 显示水平方向计算结果
                    st.subheader("水平方向计算结果")
                    # 找到最接近指定角度的索引
                    beta = np.linspace(0, 2*np.pi, 360)
                    idx = int(round(fw * len(beta) / 360))
                    idx = min(idx, len(beta)-1)
                    
                    I_total = results_h[idx]
                    I_skin = Im_arr_h[idx]
                    I_flame = Iw_arr_h[idx]
                    I_nozzle = Ip_arr_h[idx]
                    
                    # 计算作用距离
                    R_range = calc_range_at_angle(params, I_total, fw, 'horizontal')
                    
                    # 使用卡片样式展示结果
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; border-radius: 5px; padding: 15px; margin-bottom: 10px;">
                        <h4>方位角 {fw}° 的辐射特性</h4>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <div style="width: 48%;">
                                <p><b>总辐射:</b> {I_total:.6f} W/sr</p>
                                <p><b>蒙皮辐射:</b> {I_skin:.6f} W/sr</p>
                            </div>
                            <div style="width: 48%;">
                                <p><b>尾焰辐射:</b> {I_flame:.6f} W/sr</p>
                                <p><b>喷口辐射:</b> {I_nozzle:.6f} W/sr</p>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #3F3F46;">
                            <p style="font-size: 1.1em;"><b>作用距离:</b> <span style="color: #FF8C00; font-weight: bold;">{R_range:.2f} km</span></p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_chart2:
            st.subheader("垂直方向辐射模式")
            if btn_calculate_all or btn_calc_vertical:
                with st.spinner("计算垂直方向辐射中..."):
                    beta_v, results_v, max_I_v, Im_arr_v, Iw_arr_v, Ip_arr_v = radiation_calculations(params, s3, 'vertical')
                    
                    # 绘制垂直方向辐射模式
                    fig2 = plt.figure(figsize=(8, 6))
                    ax2 = fig2.add_subplot(111, projection='polar')
                    ax2.plot(beta_v, results_v, 'r-', linewidth=2, label='总辐射')
                    ax2.plot(beta_v, Im_arr_v, 'b--', label='蒙皮辐射')
                    ax2.plot(beta_v, Iw_arr_v, 'g:', label='尾焰辐射')
                    ax2.plot(beta_v, Ip_arr_v, 'm-.', label='喷口辐射')
                    ax2.set_rlabel_position(22.5)
                    ax2.grid(True)
                    ax2.legend(loc='upper right', bbox_to_anchor=(1.15, 1.15))
                    st.pyplot(fig2)
                    
                    # 显示垂直方向计算结果
                    st.subheader("垂直方向计算结果")
                    # 找到最接近指定角度的索引
                    beta = np.linspace(0, 2*np.pi, 360)
                    idx = int(round(fy * len(beta) / 360))
                    idx = min(idx, len(beta)-1)
                    
                    I_total = results_v[idx]
                    I_skin = Im_arr_v[idx]
                    I_flame = Iw_arr_v[idx]
                    I_nozzle = Ip_arr_v[idx]
                    
                    # 计算作用距离
                    R_range = calc_range_at_angle(params, I_total, fy, 'vertical')
                    
                    # 使用卡片样式展示结果
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; border-radius: 5px; padding: 15px; margin-bottom: 10px;">
                        <h4>俯仰角 {fy}° 的辐射特性</h4>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <div style="width: 48%;">
                                <p><b>总辐射:</b> {I_total:.6f} W/sr</p>
                                <p><b>蒙皮辐射:</b> {I_skin:.6f} W/sr</p>
                            </div>
                            <div style="width: 48%;">
                                <p><b>尾焰辐射:</b> {I_flame:.6f} W/sr</p>
                                <p><b>喷口辐射:</b> {I_nozzle:.6f} W/sr</p>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #3F3F46;">
                            <p style="font-size: 1.1em;"><b>作用距离:</b> <span style="color: #FF8C00; font-weight: bold;">{R_range:.2f} km</span></p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 作用距离包线图
        if btn_calculate_all or btn_calc_range:
            st.subheader("作用距离包线")
            st.warning("计算作用距离包线需要较长时间，请耐心等待...")
            
            with st.spinner("计算作用距离包线中..."):
                # 获取辐射数据
                beta_h, results_h, _, _, _, _ = radiation_calculations(params, s2, 'horizontal')
                beta_v, results_v, _, _, _, _ = radiation_calculations(params, s3, 'vertical')
                
                # 存储数据
                range_data = {
                    'horizontal': {
                        'beta': beta_h,
                        'range_values': [],
                        'intensities': results_h
                    },
                    'vertical': {
                        'beta': beta_v,
                        'range_values': [],
                        'intensities': results_v
                    }
                }
                
                # 计算总步数
                total_steps = len(results_h) + len(results_v)
                current_step = 0
                progress_bar = st.progress(0.0)
                
                # 计算各角度对应的作用距离（水平方向）
                for i, intensity in enumerate(results_h):
                    range_data['horizontal']['range_values'].append(
                        calc_range_at_angle(params, intensity, np.degrees(beta_h[i]), 'horizontal')
                    )
                    current_step += 1
                    progress_bar.progress(min(1.0, current_step / total_steps))
                
                # 计算各角度对应的作用距离（垂直方向）
                for i, intensity in enumerate(results_v):
                    range_data['vertical']['range_values'].append(
                        calc_range_at_angle(params, intensity, np.degrees(beta_v[i]), 'vertical')
                    )
                    current_step += 1
                    progress_bar.progress(min(1.0, current_step / total_steps))
                
                # 绘制水平方向作用距离图
                fig3 = plt.figure(figsize=(8, 6))
                ax3 = fig3.add_subplot(111, projection='polar')
                
                # 绘制作用距离包线
                ax3.plot(beta_h, range_data['horizontal']['range_values'], 'c-', linewidth=2, label='作用距离包线')
                
                # 标记最大作用距离点
                range_values_h = range_data['horizontal']['range_values']
                max_range_idx_h = np.argmax(range_values_h)
                max_range_h = range_values_h[max_range_idx_h]
                max_range_angle_h = np.degrees(beta_h[max_range_idx_h])
                ax3.plot([beta_h[max_range_idx_h]], [max_range_h], 'ro', markersize=8)
                ax3.annotate(f'最大: {max_range_h:.1f}km', 
                            xy=(beta_h[max_range_idx_h], max_range_h),
                            xytext=(beta_h[max_range_idx_h] + 0.3, max_range_h * 1.1),
                            arrowprops=dict(facecolor='red', shrink=0.05),
                            color='white')
                
                # 设置标题和标签
                ax3.set_title("水平方向作用距离包线", fontsize=12, pad=15, color='white')
                ax3.set_rlabel_position(22.5)
                ax3.grid(True)
                ax3.legend(loc='upper right')
                
                # 添加表格信息
                table_text_h = (
                    f"最大作用距离: {max_range_h:.1f} km @ {max_range_angle_h:.1f}°\n"
                    f"平均作用距离: {np.mean(range_values_h):.1f} km\n"
                    f"最小作用距离: {np.min(range_values_h):.1f} km"
                )
                ax3.text(0.5, -0.3, table_text_h, transform=ax3.transAxes, 
                        fontsize=10, ha='center', va='top', color='white',
                        bbox=dict(boxstyle='round', facecolor='#1E1E1E', alpha=0.8, edgecolor='#0078D7'))
                
                # 绘制垂直方向作用距离图
                fig4 = plt.figure(figsize=(8, 6))
                ax4 = fig4.add_subplot(111, projection='polar')
                
                # 绘制作用距离包线
                ax4.plot(beta_v, range_data['vertical']['range_values'], 'm-', linewidth=2, label='作用距离包线')
                
                # 标记最大作用距离点
                range_values_v = range_data['vertical']['range_values']
                max_range_idx_v = np.argmax(range_values_v)
                max_range_v = range_values_v[max_range_idx_v]
                max_range_angle_v = np.degrees(beta_v[max_range_idx_v])
                ax4.plot([beta_v[max_range_idx_v]], [max_range_v], 'ro', markersize=8)
                ax4.annotate(f'最大: {max_range_v:.1f}km', 
                            xy=(beta_v[max_range_idx_v], max_range_v),
                            xytext=(beta_v[max_range_idx_v] + 0.3, max_range_v * 1.1),
                            arrowprops=dict(facecolor='red', shrink=0.05),
                            color='white')
                
                # 设置标题和标签
                ax4.set_title("垂直方向作用距离包线", fontsize=12, pad=15, color='white')
                ax4.set_rlabel_position(22.5)
                ax4.grid(True)
                ax4.legend(loc='upper right')
                
                # 添加表格信息
                table_text_v = (
                    f"最大作用距离: {max_range_v:.1f} km @ {max_range_angle_v:.1f}°\n"
                    f"平均作用距离: {np.mean(range_values_v):.1f} km\n"
                    f"最小作用距离: {np.min(range_values_v):.1f} km"
                )
                ax4.text(0.5, -0.3, table_text_v, transform=ax4.transAxes, 
                        fontsize=10, ha='center', va='top', color='white',
                        bbox=dict(boxstyle='round', facecolor='#1E1E1E', alpha=0.8, edgecolor='#0078D7'))
                
                # 显示图表
                col_range1, col_range2 = st.columns(2)
                with col_range1:
                    st.pyplot(fig3)
                with col_range2:
                    st.pyplot(fig4)
                
                st.success("作用距离包线计算完成！")

if __name__ == "__main__":
    main()