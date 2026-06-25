import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Loading the dataset
df = pd.read_csv('C:\\Users\\Toms\\Desktop\\SALES OPS\\Sales Funnel Analysis\\users_events.csv')
df['event_date'] = pd.to_datetime(df['event_date'])
print(df.head())

# Step 1: define funnel stages
last_30_days = df[df['event_date'] >= df['event_date'].max() - timedelta(days = 30)]

funnel_stages ={
    'stage1_views' : last_30_days[last_30_days['event_type'] == 'page_view']['user_id'].nunique(),
    'stage2_cart' : last_30_days[last_30_days['event_type'] == 'add_to_cart']['user_id'].nunique(),
    'stage3_checkout' : last_30_days[last_30_days['event_type'] == 'checkout_stat']['user_id'].nunique(),
    'stage4_payment' : last_30_days[last_30_days['event_type'] == 'payment_info']['user_id'].nunique(),
    'stage5_purchase' : last_30_days[last_30_days['event_type'] == 'purchase']['user_id'].nunique()
    }

funnel_df = pd.DataFrame([funnel_stages])
print(funnel_df)

# Step 2: calculate stage-to-stage conversion rates
conversion_metrics = {
    'stage1_views' : funnel_stages['stage1_views'],
    'stage2_cart' : funnel_stages['stage2_cart'],
    'view_to_cart_rate' : round(funnel_stages['stage2_cart'] / funnel_stages['stage1_views'] * 100, 2),
    'stage3_checkout' : funnel_stages['stage3_checkout'],
    'cart_to_checkout_rate' : round(funnel_stages['stage3_checkout'] / funnel_stages['stage2_cart'] * 100, 2),
    'stage4_payment' : funnel_stages['stage4_payment'],
    'checkout_to_payment_rate' : round(funnel_stages['stage4_payment'] / funnel_stages['stage3_checkout'] * 100, 2),
    'stage5_purchase' : funnel_stages['stage5_purchase'],
    'payment_to_purchase_rate' : round(funnel_stages['stage5_purchase'] / funnel_stages['stage4_payment'] * 100, 2),
    'overall_conversion_rate' : round(funnel_stages['stage5_purchase'] / funnel_stages['stage1_views'] * 100, 2)
}

print(pd.DataFrame([conversion_metrics]))

# Visualization of the funnel
stages = ['Views', 'Cart', 'Checkout', 'Payment', 'Purchase']
values = [
    funnel_stages['stage1_views'], 
    funnel_stages['stage2_cart'], 
    funnel_stages['stage3_checkout'], 
    funnel_stages['stage4_payment'], 
    funnel_stages['stage5_purchase']
    ]

plt.figure(figsize = (10, 6))

plt.bar(
    stages,
    values,
    color = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
    )

plt.title('Sales Funnel - User Count by Stage')
plt.ylabel('Number of Users')

for i, v in enumerate(values):
    plt.text(i, v + 200, str(v), ha = 'center', fontweight = 'bold')

plt.show()

# Step 3: Funnel by Traffic Source
source_funnel = last_30_days.groupby('traffic_source').agg({
    'user_id': lambda x : x [last_30_days.loc[x.index, 'event_type'] == 'page_view'].nunique(),
}).rename(columns = {'user_id': 'views'})

source_funnel['carts'] = last_30_days[last_30_days['event_type'] == 'add_to_cart'].groupby('traffic_source')['user_id'].nunique()
source_funnel['purchases'] = last_30_days[last_30_days['event_type'] == 'purchase'].groupby('traffic_source')['user_id'].nunique()

source_funnel['cart_conversion_rate'] = (source_funnel['carts'] / source_funnel['views'] * 100).round(2)
source_funnel['purchase_conversion_rate'] = (source_funnel['purchases'] / source_funnel['views'] * 100).round(2)
source_funnel['cart_to_purchase_rate'] = (source_funnel['purchases'] / source_funnel['carts'] * 100).round(2)   

source_funnel = source_funnel.sort_values('purchases', ascending = False)
print(source_funnel)

# Step 4: Time to Conversion Analysis
user_journey = last_30_days.groupby('user_id').agg({
    'event_date': lambda x : {
        'view_time': x[last_30_days.loc[x.index, 'event_type'] == 'page_view'].min(),
        'cart_time': x[last_30_days.loc[x.index, 'event_type'] == 'add_to_cart'].min(),
        'purchase_time': x[last_30_days.loc[x.index, 'event_type'] == 'purchase'].min()
    }
})

journey_times = []

for user_id, row in user_journey.iterrows():
    times = row['event_date']
    if pd.notna(times['purchase_time']):
        journey_times.append({
            'user_id': user_id,
            'view_to_cart_minutes': (times['cart_time'] - times['view_time']).total_seconds() / 60 if pd.notna(times['cart_time']) else np.nan,
            'cart_to_purchase_minutes': (times['purchase_time'] - times['cart_time']).total_seconds() / 60 if pd.notna(times['cart_time']) else np.nan,
            'total_journey_minutes': (times['purchase_time'] - times['view_time']).total_seconds() / 60
        })

journey_df = pd.DataFrame(journey_times)
time_metrics = {
    'converted_users': len(journey_df),
    'avg_view_to_cart_minutes': round(journey_df['view_to_cart_minutes'].mean(), 2),
    'avg_cart_to_purchase_minutes': round(journey_df['cart_to_purchase_minutes'].mean(), 2),
    'avg_total_journey_minutes': round(journey_df['total_journey_minutes'].mean(), 2)
}

print(pd.DataFrame([time_metrics]))

# Step 5: Drop-off Analysis
drop_off = []

transitions = [
    ('View to Cart', funnel_stages['stage1_views'], funnel_stages['stage2_cart']),
    ('Cart to Checkout', funnel_stages['stage2_cart'], funnel_stages['stage3_checkout']),
    ('Checkout to Payment', funnel_stages['stage3_checkout'], funnel_stages['stage4_payment']),
    ('Payment to Purchase', funnel_stages['stage4_payment'], funnel_stages['stage5_purchase'])
]

for stage_name, stage_from, stage_to in transitions:
    users_dropped = stage_from - stage_to
    drop_off_rate = round(users_dropped / stage_from * 100, 2)
    drop_off.append({
        'stage_transition': stage_name,
        'users_dropped': users_dropped,
        'drop_off_rate': drop_off_rate
    }) 

drop_off_df = pd.DataFrame(drop_off)
print(drop_off_df)

# Visuallization
plt.figure(figsize = (10, 6))

plt.barh(drop_off_df['stage_transition'], drop_off_df['drop_off_rate'], color = 'coral')

plt.title('Funnel Drop-off Rates by Stage')
plt.xlabel('Drop-off Rate (%)')

plt.xlim(0, 100)

for i, v in enumerate(drop_off_df['drop_off_rate']):
    plt.text(v + 2, i, str(v) + '%', va = 'center', fontweight = 'bold')

plt.tight_layout()
plt.show()

# Step 6: Revenue Funnel Dashboard
purchase_events = last_30_days[last_30_days['event_type'] == 'purchase']

revenue_metrics = {
    'total_visitors': funnel_stages['stage1_views'],
    'total_buyers': funnel_stages['stage5_purchase'],
    'conversion_rate': round(funnel_stages['stage5_purchase'] / funnel_stages['stage1_views'] * 100, 2),
    'total_revenue': purchase_events['amount'].sum(),
    'avg_order_value': round(purchase_events['amount'].mean(), 2),
    'revenue_per_buyer': round(purchase_events['amount'].sum() / funnel_stages['stage5_purchase'], 2),
    'revenue_per_visitor': round(purchase_events['amount'].sum() / funnel_stages['stage1_views'], 2)
}

revenue_df = pd.DataFrame([revenue_metrics])
print('\nRevenue Funnel Dashboard:')
print(revenue_df)

# Create comprehensive dashboard visualization
fig, axes = plt.subplots(2, 2, figsize = (14, 10))

axes[0, 0].bar(stages, values, color = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'])
axes[0, 0].set_title('Funnel Stages')
axes[0, 0].set_ylabel('Users')

# Conversion Rates
conv_rates = [conversion_metrics['view_to_cart_rate'], conversion_metrics['cart_to_checkout_rate'], conversion_metrics['checkout_to_payment_rate'], conversion_metrics['payment_to_purchase_rate']]
axes[0, 1].plot(['View to Cart', 'Cart to Checkout', 'Checkout to Payment', 'Payment to Purchase'], conv_rates, marker = 'o', linewidth = 2, markersize = 8, color = 'green')
axes[0, 1].set_title('Stage-to-Stage Conversion Rates')
axes[0, 1].set_ylabel('Conversion Rate (%)')
axes[0, 1].grid(True, alpha = 0.3)

# Drop-off Rates
axes[1, 0].barh(drop_off_df['stage_transition'], drop_off_df['drop_off_rate'], color = 'coral')
axes[1, 0].set_title('Drop-off Analysis')
axes[1, 0].set_xlabel('Drop-off Rate (%)')

# Revenue by Source
source_revenue = last_30_days[last_30_days['event_type'] == 'purchase'].groupby('traffic_source')['amount'].sum().sort_values(ascending = False)
axes[1, 1].pie(source_revenue, labels = source_revenue.index, autopct = '%1.1f%%', startangle = 140)
axes[1, 1].set_title('Revenue by Traffic Source')

plt.tight_layout()
plt.show()

print('\nSales Funnel Analysis Completed!')

# the end