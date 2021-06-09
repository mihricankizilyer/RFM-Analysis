########################################
# Customer Segmentation with RFM
#######################################

# 1. Import & Reading
# 2. Data Understanding
# 3. Data Preparation
# 4. Calculating RFM Metrics
# 5. Calculating RFM Scores
# 6. Creating & Analysing RFM Segments

#######################
# 1. Import & Reading
#######################

# Import Libraries
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None) # show max rows in rows
pd.set_option('display.max_row', None) # show max column in columns
pd.set_option('display.float_format', lambda x: ' %.2f' % x) # show 2 numbers after the comma

# Reading the dataset
df_ = pd.read_excel('datasets/csv_path/w3/online_retail_II.xlsx', sheet_name = "Year 2010-2011") # 2010-2011 page is taken

# Data is copied against data corruption
df = df_.copy()

#######################
# 2. Data Understanding
#######################

# Are there any missing observations in the dataset? If so, how many missing observations are there?
df.isnull().sum()

# Remove the missing observations from the data set.
df = df.dropna()

#######################
# 3. Data Preparation
#######################

# Descriptive statistics of the dataset
df.describe().T

# Unique number of StockCode
df["StockCode"].nunique()

# How many of each product
df["StockCode"].value_counts()

# Sorting from the 5 most ordered products to the lowest
df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values(by = 'Quantity',ascending=False).head()

# The 'C' in the invoice shows the canceled transactions. Canceled transactions leave the dataset.
df = df[~df["Invoice"].astype(str).str.contains('C', na = False)] # na (blank observation) means disregard

# Earnings per invoice
df["Total Price"] = df["Quantity"] * df["Price"]

#######################
# 4. Calculating RFM Metrics
#######################

"""
 Recency: Müşterinin son satın almasından bugüne kadar geçen süre
 
 Frequency: Toplam satın alma sayısı
 
 Monetary: Müşterinin yaptığı toplam harcama
"""

# The date of the last purchase is found
df["InvoiceDate"].max() #-> 2011-12-09

# Recency account is selected after 2 days to avoid problems.
today_date =dt.datetime(2011,12,11)

# Recency, frequency and monetary values were calculated
rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date:(today_date-date.max()).days,  # last purchase - today's purchase and .days -> returns the format in days
                                    "Invoice": lambda num : num.nunique(), # nunique -> number of unique invoices
                                    "Total Price": lambda total_price: total_price.sum()})

# Column names changed
rfm.columns = ["Recency","Frequency","Monetary"]

# Values with a total spend of zero are discarded
rfm = rfm[rfm["Monetary"] > 0]

#######################
# 5. Calculating RFM Scores
#######################

# The lowest recency value is the most valuable
# So in order from largest to smallest
rfm["recency_score"] = pd.qcut(rfm["Recency"], 5, labels = [5, 4, 3, 2, 1])

# Higher frequency indicates more frequent shopping.
# Sort from smallest to largest
# If the same quarter is still observed when going to different quarters after sorting, mehtod first is used because this causes a problem.
# duplicates -> gives value error
rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels = [1,2,3,4,5])

# A high Monetary value indicates that the total amount paid is high.
# Sort from smallest to largest
rfm["monetary_score"] = pd.qcut(rfm["Monetary"], 5, labels = [1,2,3,4,5])

rfm["RFM_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)

#######################
# 6. Creating & Analysing RFM Segments
#######################

# Defining RFM scores as segments
seg_map = {
    r'[1-2][1-2]': 'hibreating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# Regular expression: r'[1-2]->recency [1-2]->frequency => r'[1-2][1-2] => gives naming according to values
rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex = True)

# The metrics created at the beginning are selected, not the scores
rfm[["segment", "Recency", "Frequency", "Monetary"]].groupby("segment").agg(["mean", "count"])

# Customers with high frequency continue as soon as they bring a lot of income.
# 3 segments with the highest frequency are selected.
# Highest-> champions
# Second -> cant_loose
# Third -> loyal_customers

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()

# csv the ids of the loyal_customers class
# reload from disk to view
# these ids are sent to the relevant department
new_df.to_csv("loyal_customers.csv") # save df








