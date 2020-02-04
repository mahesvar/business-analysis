import os
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter
import DateTime as dt

path = "./Sales_Data"       

files = [file for file in os.listdir(path) if not file.startswith('.')] # Ignore hidden files

# create all_month_data data frame to store all month data
all_months_data = pd.DataFrame()

for file in files:
    current_data = pd.read_csv(path+"/"+file)
    all_months_data = pd.concat([all_months_data, current_data])
 
# convert the file to csv file and read it 
all_months_data.to_csv("all_data_copy.csv", index=False)
all_data = pd.read_csv("all_data_copy.csv")

# cleaning the data
# drop all rows with Nan value
all_data = all_data.dropna(how='all')
all_data.head()

# remove 'Or' str in the order date column
all_data = all_data[all_data['Order Date'].str[0:2]!='Or']

# converting Quantity Ordered and Price Each to numeric type
all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered'])
all_data['Price Each'] = pd.to_numeric(all_data['Price Each'])

# extracting month from order date column and creating new column
all_data['Month'] = all_data['Order Date'].str[0:2]
all_data['Month'] = all_data['Month'].astype('int32')

# adding city and state columns
def get_city(address):
    return address.split(",")[1].strip(" ")

def get_state(address):
    return address.split(",")[2].split(" ")[1]
    
# business analysis 
# 1.which is the best month for the sale and its revenue
all_data['City'] = all_data['Purchase Address'].apply(lambda x: f"{get_city(x)}  ({get_state(x)})")
all_data['Sales'] = all_data['Quantity Ordered'].astype('int') * all_data['Price Each'].astype('float')
all_data.groupby(['Month']).sum()

months = range(1,13)

plt.bar(months,all_data.groupby(['Month']).sum()['Sales'])
plt.xticks(months)
plt.ylabel('Sales in USD ($)')
plt.xlabel('Month number')
plt.show()

# 2.which city sold the most products
all_data.groupby(['City']).sum()

keys = [city for city, df in all_data.groupby(['City'])]

plt.bar(keys,all_data.groupby(['City']).sum()['Sales'])
plt.ylabel('Sales in USD ($)')
plt.xlabel('Month number')
plt.xticks(keys, rotation='vertical', size=8)
plt.show()

# 3.what time should we display ads to maximize the chance for better sales
all_data['Order Date'] = pd.to_datetime(all_data['Order Date'])
all_data['hour'] = all_data['Order Date'].dt.hour
all_data['minute'] = all_data['Order Date'].dt.minute

hours = [hour for hour, dt in all_data.groupby('hour')]
plt.plot(hours,all_data.groupby(['hour']).count(),'-o')
plt.grid()
plt.xticks(hours)
plt.show()

# describing the product column will show which product sold the most and unique products and its frequency
all_data.Product.describe()

# 4.which products are sold together
## most product sold together
df = all_data[all_data['Order ID'].duplicated(keep=False)]
df['grouped'] = df.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))
df = df[['Order ID','grouped']].drop_duplicates()

count = Counter()
for row in df['grouped']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list,2)))

# most commonly sold items together
for key,value in count.most_common(10):
    print(key,value)

# 5.what product sold the most and why ?
product_grp = all_data.groupby('Product')
quantity_ordered = product_grp.sum()['Quantity Ordered']
products = [product for product,df in product_grp]

plt.bar(products,quantity_ordered)
plt.xticks(rotation=90,size=8);
plt.grid();

prices = all_data.groupby('Product').mean()['Price Each']

# ploting the corelation between no of item sold vs price of that item
fig,ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.bar(products,quantity_ordered,color = 'green',alpha=0.5)
ax2.plot(products,prices,'-o')

ax1.grid()
ax1.set_xlabel('product name')
ax1.set_ylabel('quantity ordered',color = 'r')
ax1.set_ylabel('price ($) ',color = 'b')
ax1.set_xticklabels(products,rotation=90,size=8)
fig.show()








