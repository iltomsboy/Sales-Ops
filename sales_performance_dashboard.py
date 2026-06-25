import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

df = pd.read_csv('C:\\Users\\Toms\\Desktop\\SALES OPS\\Sales Performance Dashboard\\sales.csv')
df['sale_date'] = pd.to_datetime(df['sale_date'])
print(df.head())

# Step 1: Core Revenue Metrics
current_month = df[df['sale_date'] >= df['sale_date']].max().replace(day = 1)

core_metrics = {
    'total_orders': len(current_month),
    'total_revenue': round(current_month['revenue'].sum(), 2),
    'total_cost': round(current_month['cost'].sum(), 2),
    'gross_profit': round(current_month['revenue'].sum() - current_month['cost'].sum(), 2),
    'unique_customers': current_month['customer_id'].nunique(),
    'active_reps': current_month['sales_rep'].nunique()
}

core_metrics['gross_margin_profit'] = round(core_metrics['gross_profit'] / core_metrics['total_revenue'] * 100, 2)
core_metrics['avg_order_value'] = round(core_metrics['total_revenue'] / core_metrics['total_orders'], 2)
core_metrics['revenue_per_customer'] = round(core_metrics['total_revenue'] / core_metrics['unique_customers'], 2)

print('Core Revenue Metrics:')

for key, value in core_metrics.items():
    print(f"{key}: {value}")

# Step 2: Growth Metrics (MoM and YoY)
current_month_start = df['sale_date'].max().replace(day = 1)
previous_month_start = (current_month_start - pd.DateOffset(months = 1))
last_year_month_start = (current_month_start - pd.DateOffset(months = 12))

current = df[df['sale_date'] >= current_month_start]
previous = df[(df['sale_date'] >= previous_month_start) & (df['sale_date'] < current_month_start)]
last_year = df[(df['sale_date'] >= last_year_month_start) & (df['sale_date'] < last_year_month_start + pd.DateOffset(months = 1))  ]

growth_metrics = {
    'current_revenue': round(current['amount'].sum(), 2),
    'previous_month_revenue': round(previous['amount'].sum(), 2),
    'last_year_revenue': round(last_year['amount'].sum(), 2),
    'current_orders': len(current),
    'previous_orders': len(previous),
    'current_customers': current['customer_id'].nunique(),
    'previous_customers': previous['customer_id'].nunique()
}

growth_metrics['mom_revenue_growth'] = round(
    (growth_metrics['current_revenue'] - growth_metrics['previous_month_revenue']) 
    / growth_metrics['previous_month_revenue'] * 100,
                                             2)
growth_metrics['yoy_revenue_growth'] = round(
    (growth_metrics['current_revenue'] - growth_metrics['last_year_revenue']) 
    / growth_metrics['last_year_revenue'] * 100,
                                             2)
growth_metrics['mom_order_growth'] = round(
    (growth_metrics['current_orders'] - growth_metrics['previous_orders'])
    / growth_metrics['previous_orders'] * 100,
                                             2)
growth_metrics['current_customers'] = round(
    (growth_metrics['current_customers'] - growth_metrics['previous_customers'])
    / growth_metrics['previous_customers'] * 100,
                                             2)

print('\nGrowth Metrics:')
print(pd.DataFrame([growth_metrics]))

# Visualization
fig, axes = plt.subplots(1, 2, figsize = (14, 6))
growth_data = [growth_metrics['mom_revenue_growth'], growth_metrics['yoy_revenue_growth']]
axes[0].bar(['MoM Revenue Growth', 'YoY Revenue Growth'], growth_data, color = ['skyblue', 'salmon'])
axes[0].set_title('Revenue Growth Metrics')
axes[0].set_ylabel('Growth Rate (%)')
axes[0].axhline(y = 0, color = 'green', linewidth = 0.8, linestyle = '--')

revenue_comparison = [
    growth_metrics['previous_month_revenue'], 
    growth_metrics['current_revenue'], 
    growth_metrics['last_year_revenue']
]

axes[1].bar(['Previous Month', 'Current Month', 'Last Year Same Month'], revenue_comparison, color = ['lightgreen', 'lightcoral', 'lightblue'])
axes[1].set_title('Revenue Comparison')
axes[1].set_ylabel('Revenue ($)')

plt.tight_layout()
plt.show()

# Step 3: Regional Performance Analysis
current_regional = current.groupby('region').agg({
    'amount': 'sum',
    'cost': 'sum',
    'sale_id': 'count',
    'customer_id': 'nunique'
}).reset_index()

current_regional.columns =[
    'region', 
    'total_revenue', 
    'total_cost', 
    'total_orders', 
    'total_customers'
]

previous_regional = previous.groupby('region')['amount'].sum().reset_index()
previous_regional.columns = ['region', 'previous_revenue']

regional_performance = current_regional.merge(previous_regional, on = 'region', how = 'left')
regional_performance['margin_pct'] = ( 
    (regional_performance['total_revenue'] - regional_performance['total_cost']) 
    / regional_performance['total_revenue'] * 100
    ).round(2)
regional_performance['avg_order_value'] = (
    regional_performance['total_revenue'] / regional_performance['total_orders']
    ).round(2)
regional_performance['mom_growth'] = (
    (regional_performance['total_revenue'] - regional_performance['previous_revenue'])
    / regional_performance['previous_revenue'] * 100
    ).round(2)

regional_performance = regional_performance.sort_values(by = 'total_revenue', ascending = False)

print('\nRegional Performance Analysis:')
print(regional_performance[['region', 
                            'total_revenue', 
                            'margin_pct',
                            'total_orders', 
                            'avg_order_value', 
                            'revenue_share',
                            'mom_growth']])

# Visualization
fig, axes = plt.subplots(1, 2, figsize = (14, 6))

axes[0].bar(regional_performance['region'], regional_performance['total_revenue'], color = 'skyblue')
axes[0].set_title('Total Revenue by Region')   
axes[0].set_ylabel('Revenue ($)')

axes[1].bar(regional_performance['region'], regional_performance['margin_pct'], color = 'salmon')
axes[1].set_title('Gross Margin Percentage by Region')
axes[1].set_ylabel('Gross Margin (%)')

plt.tight_layout
plt.show()

# Step 4: Sales Rep Performance Analysis
rep_performance = current.groupby('sales_rep').agg({
    'sale_id': 'count',
    'amount': 'sum',
    'cost': 'sum',
    'customer_id': 'nunique'
}).reset_index()

rep_performance.columns = [
    'sales_rep', 
    'deals_closed', 
    'total_revenue', 
    'total_cost', 
    'unique_customers'
]

rep_performance['margin_pct'] = (
    (rep_performance['total_revenue'] - rep_performance['total_cost']) 
    / rep_performance['total_revenue'] * 100
    ).round(2)
rep_performance['avg_deal_size'] = (
    rep_performance['total_revenue'] / rep_performance['deals_closed']
    ).round(2)
rep_performance['deals_per_customer'] = (
    rep_performance['deals_closed'] / rep_performance['unique_customers'] * 100
    ).round(2)
rep_performance['revenue_rank'] = rep_performance['total_revenue'].rank(ascending = False, method = 'min').astype(int)

rep_performance = rep_performance.sort_values(by = 'total_revenue', ascending = False).head(10)

print('\nTop 10 Sales Rep Performance:')
print(rep_performance[['sales_rep', 
                        'deals_closed', 
                        'total_revenue', 
                        'margin_pct', 
                        'avg_deal_size',
                        'unique_customers',
                        'deals_per_customer', 
                        'revenue_rank']])

# Step 5:
products = pd.read_csv('C:\\Users\\Toms\\Desktop\\SALES OPS\\Sales Performance Dashboard\\products.csv')
current_with_category = current.merge(products[['product_id', 'category']], on = 'product_id', how = 'left')

category_performance = current_with_category.groupby('category').agg({
    'sale_id': 'count',
    'amount': 'sum',
    'cost': 'sum',
    'customer_id': 'nunique'
}).reset_index()
category_performance.columns = [
    'category', 
    'units_sold',
    'revenue',
    'cost',
    'customers'
]

category_performance['margin_pct'] = (
    (category_performance['revenue'] - category_performance['cost'])
    / category_performance['revenue'] * 100
).round(2)
category_performance['avg_unit_price'] = (
    category_performance['revenue'] / category_performance['units_sold']
).round(2)
category_performance['revenue_contribution'] = (
    category_performance['revenue'] / category_performance['revenue'] * 100
).round(2)

category_performance = category_performance.sort_values('revenue', ascending = False)

print('\nProduct Category Performance:')
print(category_performance)

# Visualization:
plt.figure(figsize = (12, 6))

plt.subplot(1, 2, 1)
plt.pie(
    category_performance['revenue'],
    laberls = category_performance['category'],
    autopct = '%1.1f%%',
    startangle = 90
    )

plt.title('Revenue Distribution by Category')

plt.subplot(1, 2, 2)
plt.barh(category_performance['category'], 
         category_performance['margin_pct'],
         color = 'purple')

plt.xlabel('Margin (%)')
plt.title('Profit Margin by Category')

plt.tight_layout()
plt.show()

# Step 6: 
active_days = current['sales_date'].nunique()

executive_summary = {
    'total_revenue': round(current['amount'].sum(), 2),
    'gross_profit': round((current['amount'].sum() - current['cost'].sum()) 
                    / current['amount'] * 100, 2),
    'total_orders': len(current),
    'avg_order_value': round(current['amount'].mean(), 2),
    'total_customers': current['customer_id'].nunique(),
    'customer_lifetime_value': round(current['amount'].sum()
                                / current['customer_id'].nunique(), 2),
    'orders_per_customer': round(len(current) / current['customer_id'].nunique(), 2),
    'avg_daily_revenue': round(current['amount'].sum() / active_days, 2),
    'avg_daily_orders': round(len(current) / active_days, 2)
}

print('\nExecutive Summary Dashboard:')
summary_df = pd.DataFrame([executive_summary])
print(summary_df.T)

# Comprehensive Dashboard Visualization
fig = plt.figure(figsize = (16, 10))
gs = fig.add_gridspec(3, 3, hspace = 0.3, wspace = 0.3)

# Revenue Trend
ax1 = fig.add_subplot(gs[0, :])
daily_revenue = current.groupby('sale_date')['amount'].sum()
ax1.plot(
    daily_revenue.index,
    daily_revenue.values,
    marker = 'o',
    linewidth = 2,
    color = 'steelblue'
)
ax1.set_title('Daily Revenue Trend', fontsize = 14, fotnweight = 'bold')
ax1.set_ylabel('Revenue ($)')
ax1.grid(True, alpha = 0.3)

# Regional Performance
ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(
    regional_performance['region'], 
    regional_performance['revenue'],
    color = 'coral')
ax2.set_title('Reveneu by Region', fontwight = 'bold')
ax2.set_ylabel('Revenue ($)')
ax2.tick_params(axis = 'x', rotation = 45)

# Category Distribution
ax3 = fig.add_subplot(gs[1, 0])
ax3.pie(
    category_performance['revenue'],
    labels = category_performance['category'],
    autopct = '%1.1f%%',
    startangle = 90
)
ax3.set_title('Category Mix', fontweight = 'bold')

# Top reps
ax4 = fig.add_subplot(gs[1, 2])
top5_reps = rep_performance.head(5)
ax4.barh(
    top5_reps['sales_rep'],
    top5_reps['revenue'],
    color = 'green')
ax4.set_title('Top 5 Sales Reps', fontweight = 'bold')
ax4.set_xlabel('Revenue ($)')

# KPI cards
ax5 = fig.add_subplot(gs[2, 0])
ax5.axis('off')

kpi_text = f'Total Revenue\n${executive_summary['total_orders']:,.0f}\n\nGross Profit\n${executive_summary['gross_profit']:,.0f}'

ax5.text(
    0.5, 
    0.5, 
    kpi_text, 
    ha = 'center', 
    va = 'center', 
    fontsize = 12, 
    fontweight = 'bold', 
    bbox = dict(boxstyle = 'round', facecolor = 'lightblue', alpha = 0.5)
)

ax6 = fig.add_subplot(gs[2, 1])
ax6.axis('off')

kpi_text2 = f'Total Orders\n{executive_summary['total_orders']:,}\n\nAOV\n${executive_summary['avg_order_value']:.2f}'

ax6.text(
    0.5,
    0.5,
    kpi_text2,
    ha = 'center',
    va = 'center',
    fontsize = 12,
    fontweight = 'bold',
    bbox = dict(boxstyle = 'round', facecolor = 'lightgreen', alpha = 0.5)
)

ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')

kpi_text3 = f'Customers\n{executive_summary['total_customers']:,}\n\nMargin\n{executive_summary['gross_margin_pct']:.1f}%'

ax7.text(
    0.5,
    0.5,
    kpi_text3,
    ha = 'center',
    va = 'center',
    fontsize = 12,
    fontweight = 'bold',
    bbox = dict(boxstyle = 'round', facecolor = 'lightyellow', alpha = 0.5)
)

plt.suptitle('Sales Performance Dashboard', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('sales_dashboard.png', dpi=150, bbox_inches='tight')

plt.show()

print('\nSales Analysis Completed!')

#the end