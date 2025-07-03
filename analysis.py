#Import streamlit
import streamlit as st
# Configure the app page layout to wide
st.set_page_config(layout="wide") 
# import other needed libraries
import pandas as pd
import plotly.express as pt
import plotly.graph_objects as go


# Get data
# Read csv file (or connect to a database)

order_table = pd.read_excel('Sales Tables.xlsx')


# Transform your data
order_table['orderDate'] = pd.to_datetime(order_table['orderDate'])
order_table['orderYear'] = order_table['orderDate'].dt.year
order_table['orderMonth'] = order_table['orderDate'].dt.month
order_table['orderMonth_full'] = order_table['orderDate'].dt.strftime('%b')
order_table['days_to_deliver'] = (order_table['deliveryDate'] - order_table['orderDate']).dt.days
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
order_table['orderMonth_full'] = pd.Categorical(order_table['orderMonth_full'], categories=month_order, ordered=True)
order_table['sales_per_order'] = round(order_table['UnitPrice'] * (1 - order_table['DiscountApplied']) * order_table['OrderQuantity'])
order_table['profit_per_order'] = round(((order_table['UnitPrice'] * (1 - order_table['DiscountApplied'])) - order_table['UnitCost']) * order_table['OrderQuantity'])


# Page design

# Dashboard Title
with st.container(border=True):
    st.markdown(
        "<h3 style='text-align: center;'>📊 Sales Performance Dashboard</h3>",
        unsafe_allow_html=True
    )


# Create filters
a, b, c, d = st.columns(4)

sales_team = a.selectbox("Select Sales Team", options=['All'] + sorted(order_table['salesTeam'].unique().tolist()))
if sales_team != 'All':
    filtered_table = order_table[order_table['salesTeam'] == sales_team]
else:
    filtered_table = order_table

region = b.selectbox("Select Sales Region", options=['All'] + sorted(filtered_table['salesTeam_Region'].unique().tolist()))
if region != 'All':
    filtered_table = filtered_table[filtered_table['salesTeam_Region'] == region]

product = c.selectbox("Product", options=['All'] + sorted(filtered_table['productName'].unique().tolist()))
if product != 'All':
    filtered_table = filtered_table[filtered_table['productName'] == product]

year = d.selectbox("Year", options=['All'] + sorted(filtered_table['orderYear'].unique().tolist()))
if year != 'All':
    filtered_table = filtered_table[filtered_table['orderYear'] == year]


# Calculate the metrics/KPIs needed
units_sold = filtered_table['OrderQuantity'].sum()
total_order = filtered_table['orderNumber'].nunique()
total_sales = round(filtered_table['sales_per_order'].sum())
net_profit = round(filtered_table['profit_per_order'].sum())
top10 = filtered_table.groupby('productName')['OrderQuantity'].sum().reset_index()
top10 = top10.sort_values(by='OrderQuantity', ascending=False).head(10)
top10_profit = filtered_table.groupby('productName')['profit_per_order'].sum().reset_index()
top10_profit = top10_profit.sort_values(by='profit_per_order', ascending=False).head(10)
sales_over_time = filtered_table.groupby(['orderYear', 'orderMonth_full'], as_index=False)['sales_per_order'].sum()
sales_details = filtered_table[['orderNumber', 'OrderQuantity', 'orderDate', 'deliveryDate', 'days_to_deliver', 'CustomerID', 'customerName', 'sales_per_order',
                             'productName', 'salesTeam', 'salesTeam_Region']]


# Display Visual

# Display the metrics / KPIs
col1, col2, col3, col4 = st.columns(4, vertical_alignment="bottom")

col1.metric('Total Unit sold', f'{units_sold:,}', border=True)
col2.metric('Total Sales', f'${total_sales:,}', border=True)
col3.metric('Total Net Profit', f'${net_profit:,}', border=True)
col4.metric('Total order', f'{total_order:,}', border=True)


# Display the Bar Charts
col1, col2 = st.columns(2, border=True, vertical_alignment="center")

fig = pt.bar(top10, 
             y='productName', 
             x='OrderQuantity', 
             text ='OrderQuantity',
             title='Top 10 Products by Sales',
             orientation='h')

fig.update_traces(texttemplate='%{text}', textposition='outside')
fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    yaxis=dict(autorange='reversed'),
    xaxis=dict(showticklabels=False),
    margin=dict(l=150),
                  ) 
col1.plotly_chart(fig, use_container_width=True, theme=None)


fig1 = pt.bar(top10_profit, 
             y='productName', 
             x='profit_per_order', 
             text ='profit_per_order',
             title='Top 10 Products by Profit',
             orientation='h')

fig1.update_traces(texttemplate='$%{text:,}', textposition='outside',  width=0.7 )
fig1.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    yaxis=dict(autorange='reversed'),
    xaxis=dict(showticklabels=False),
    margin=dict(l=200),
    uniformtext_minsize=8,
    uniformtext_mode='show',
                          )  
col2.plotly_chart(fig1, use_container_width=True, theme=None)




# Display the line chart
fig2 = pt.line(sales_over_time, x='orderMonth_full', y='sales_per_order', color='orderYear', markers=True, title=None)

fig2.update_traces(
    hovertemplate='Month: %{x}<br>Sales: $%{y:,.0f}',
    # customdata=sales_over_time[['orderYear']]
)

fig2.update_yaxes(title='Sales', showgrid=False, showticklabels=False)
fig2.update_xaxes(title='Month')
fig2.update_layout(hovermode='x unified')
with st.container(border=True):  
    st.markdown(
    "<h6 style='text-align: center;'>📈 Sales Month on Month By Year</h6>",
    unsafe_allow_html=True)       # did this for a border
    st.plotly_chart(fig2, use_container_width=True)



# Display Sales Summary Table
with st.container(border=True):
    st.markdown(
    "<h6 style='text-align: center;'>📊 Sales Per Order Summary</h6>",
    unsafe_allow_html=True)
    st.dataframe(data=sales_details, use_container_width=True, hide_index=True, height=1000,
                column_config={
            "sales_per_order": st.column_config.NumberColumn("Sales Per Order", format="dollar"),
            "orderNumber": st.column_config.Column("Order Number"),
            "OrderQuantity": st.column_config.Column("Quantity"),
            "orderDate": st.column_config.DateColumn("Order Date", format="YYYY-MM-DD"),
            "deliveryDate": st.column_config.DateColumn("Delivery Date", format="YYYY-MM-DD"),
            "days_to_deliver": st.column_config.Column("Delivery days"),
            "CustomerID": st.column_config.Column("Customer ID"),
            "customerName": st.column_config.Column("Quantity"),
            "productName": st.column_config.Column("Product"),
            "salesTeam": st.column_config.Column("Sales Team"),
            "salesTeam_Region": st.column_config.Column("Region"),


        })