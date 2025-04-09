# app_pricing_tool.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ------------------------
# 定價資料表
# ------------------------
pricing_df = pd.DataFrame({
    '人數區間': ['0-100', '101-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10000+'],
    '人數上限': [100, 200, 500, 1000, 5000, 10000, float('inf')],
    '月訂原價/月': [250, 240, 230, 220, 210, 185, 160],
    '季訂58折/季': [435, 302, 291, 283, 263, 230, 202],
    '季訂42折/月': [145, 100, 97, 94, 88, 77, 67],
    '半年74折/半年': [390, 378, 364, 354, 329, 287, 252],
    '半年26折/月': [65, 63, 61, 59, 55, 48, 42],
    '年訂80折/年': [600, 576, 552, 528, 504, 444, 384],
    '年訂20折/月': [50, 48, 46, 44, 42, 37, 32]
})

# ------------------------
# 找出訂閱單價（根據人數與方案）
# ------------------------
def get_unit_price(paid_users, plan, total_employees):
    if total_employees <= 100:
        return 0
    for _, row in pricing_df.iterrows():
        if paid_users <= row['人數上限']:
            return {
                '月訂': row['月訂原價/月'],
                '季訂': row['季訂42折/月'],
                '半年訂': row['半年26折/月'],
                '年訂': row['年訂20折/月']
            }[plan]

# ------------------------
# 主頁面
# ------------------------
def main():
    st.set_page_config(page_title="企業訂閱定價試算工具", layout="centered")
    st.title("訂閱價格試算（含多種訂閱方案）")
    st.markdown("本工具可協助模擬不同訂閱方案下的總預算與平均月費。")

    total_employees = st.number_input("總人數", min_value=1, value=350)
    free_users = st.number_input("免費人數（例如前100人）", min_value=0, value=100)
    if free_users > total_employees:
        st.warning("⚠️ 免費人數不能大於總人數，系統已自動修正。")
        free_users = total_employees

    include_platform_fee = st.checkbox("是否計入平台費（預設為 NT$100,000）", value=True)
    apply_platform_discount = st.checkbox("平台費是否打8折？（打勾代表只收 NT$80,000）", value=False)

    paid_users = max(0, total_employees - free_users)
    platform_fee = 80000 if (include_platform_fee and apply_platform_discount) else (100000 if include_platform_fee else 0)

    st.markdown(f"\n👉 **需付費人數：{paid_users} 人**")

    result_data = []
    best_plan = None
    lowest_cost = float('inf')
    for plan in ['月訂', '季訂', '半年訂', '年訂']:
        unit_price = get_unit_price(paid_users, plan, total_employees)
        yearly_cost = unit_price * paid_users * 12
        total_cost = yearly_cost + platform_fee
        avg_per_person = total_cost / total_employees / 12

        if total_cost < lowest_cost:
            lowest_cost = total_cost
            best_plan = plan

        result_data.append({
            "方案": plan,
            "每人每月費用": f"NT${unit_price:.0f}",
            "年度總費（不含平台費）": f"NT${int(yearly_cost):,}",
            "加上平台費": f"NT${int(total_cost):,}",
            "折合每人每月成本": f"NT${avg_per_person:.2f}"
        })

    result_df = pd.DataFrame(result_data)
    st.subheader("📘 各方案比較表")
    st.dataframe(result_df, use_container_width=True)

    if total_employees <= 100:
        st.markdown(f"""
        ### 💡 小型企業優惠說明：
        總人數為 **{total_employees} 人**，屬於 100 人以下方案。
        👉 免收訂閱費，僅收平台建置費 **NT${platform_fee:,}**
        非常適合小型企業或初期導入體驗。
        """)
    else:
        st.markdown(f"""
        ### ✅ 該如何選擇？
        - 總人數：**{total_employees} 人**，其中 **{free_users} 人免費**，實際付費人數 **{paid_users} 人**
        - 平台費用：**NT${platform_fee:,}**
        - 👉 最划算方案為：**⭐ {best_plan} ⭐**
        """)

    st.subheader("📊 每人每月成本比較圖")
    fig2, ax2 = plt.subplots()
    labels = ['Monthly', 'Quarterly', 'Semi-Annual', 'Annual']
    values = [float(row['折合每人每月成本'].replace('NT$', '')) for row in result_data]
    bars = ax2.bar(labels, values, color='skyblue')
    ax2.set_ylabel("Avg. Monthly Cost (NT$)")
    ax2.set_xlabel("Subscription Plan")
    ax2.set_title("Average Monthly Cost per Plan")
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.annotate(f"${int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height + 2),
                    xytext=(0, 3), textcoords="offset points", ha='center')
    st.pyplot(fig2)

    st.subheader("💾 下載建議報告")
    csv = result_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📄 下載建議方案報告（CSV）",
        data=csv,
        file_name="pricing_recommendation.csv",
        mime='text/csv'
    )

if __name__ == '__main__':
    main()
