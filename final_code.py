#importing all the packages we need to code this project
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import streamlit as st

#Title
st.title("An Analysis on Manhattan's Yellow Taxis and COVID-19")

#Header
st.header("Network Analysis of Taxis")

#First we put all the data we need into these variables
taxiDatatypes = {"VendorID":"float","passenger_count":"float","trip_distance":"float","RatecodeID":"float","store_and_fwd_flag":"string","PULocationID":"float","DOLocationID":"float","payment_type":"float","fare_amount":"float","extra":"float","mta_tax":"float","tip_amount":"float","tolls_amount":"float","improvement_surcharge":"float","total_amount":"float","congestion_surcharge":"float"}
@st.cache
def load_cData():
    return pd.read_csv("data-by-day.csv",parse_dates=["date_of_interest"],index_col="date_of_interest",usecols=["date_of_interest","MN_CASE_COUNT","MN_HOSPITALIZED_COUNT","MN_DEATH_COUNT"])
@st.cache
def load_zones():
    return pd.read_csv("taxi+_zone_lookup.csv")
@st.cache
def load_march():
    return pd.read_csv("yellow_tripdata_2020-03.csv",dtype=taxiDatatypes,parse_dates=["tpep_pickup_datetime","tpep_dropoff_datetime"])
@st.cache
def load_april():
    return pd.read_csv("yellow_tripdata_2020-04.csv",dtype=taxiDatatypes,parse_dates=["tpep_pickup_datetime","tpep_dropoff_datetime"])
@st.cache
def load_may():
    return pd.read_csv("yellow_tripdata_2020-05.csv",dtype=taxiDatatypes,parse_dates=["tpep_pickup_datetime","tpep_dropoff_datetime"])
@st.cache
def load_june():
    return pd.read_csv("yellow_tripdata_2020-06.csv",dtype=taxiDatatypes,parse_dates=["tpep_pickup_datetime","tpep_dropoff_datetime"])

cData = load_cData()
zones = load_zones()
march = load_march()
april = load_april()
may = load_may()
june = load_june()

#Let's clean the data of any possible errors and focus on the data that we need to analyze. For this project, we will be looking from the time the governor's office issued a stay-at-home order
def clean(dataFile):
    dataFile = dataFile.dropna()
    dataFile = dataFile[dataFile.tpep_pickup_datetime>='3/22/2020']
    dataFile = dataFile[dataFile.tpep_pickup_datetime<'7/01/2020']
    return(dataFile)

march = clean(march)
april = clean(april)
may = clean(may)
june = clean(june)

cData = cData[cData.index>='3/22/2020']
cData = cData[cData.index<'7/01/2020']

#For our first analysis, we'll need to get each taxi ride that was longer than 10 miles (significant taxi rides) and their locationID's and replace them with the name of the zone
marchID = march[["trip_distance","PULocationID","DOLocationID"]]
marchID = marchID[marchID["trip_distance"]>10]
aprilID = april[["trip_distance","PULocationID","DOLocationID"]]
aprilID = aprilID[aprilID["trip_distance"]>10]
mayID = may[["trip_distance","PULocationID","DOLocationID"]]
mayID = mayID[mayID["trip_distance"]>10]
juneID = june[["trip_distance","PULocationID","DOLocationID"]]
juneID = juneID[juneID["trip_distance"]>10]

#Here is the function to replace the ID's with their corresponding names
def convertZone(month):
    zoneConversion = dict(zip(zones.LocationID,zones.Zone))
    month.PULocationID = month.PULocationID.map(zoneConversion)
    month.DOLocationID = month.DOLocationID.map(zoneConversion)
    return(month)

marchConv = convertZone(marchID)
aprilConv = convertZone(aprilID)
mayConv = convertZone(mayID)
juneConv = convertZone(juneID)

#Now we will start making a graph object and adding these locations to it
marchG = nx.DiGraph()
aprilG = nx.DiGraph()
mayG = nx.DiGraph()
juneG = nx.DiGraph()

#In order to add locations, we add nodes which are the locations, and then the edges, which are the relationships between the locations, or where a taxi picked someone up and where it dropped them off
marchG.add_nodes_from(zones.Zone)
aprilG.add_nodes_from(zones.Zone)
mayG.add_nodes_from(zones.Zone)
juneG.add_nodes_from(zones.Zone)

marEdges = list(zip(marchConv.PULocationID,marchConv.DOLocationID))
aprEdges = list(zip(aprilConv.PULocationID,aprilConv.DOLocationID))
mayEdges = list(zip(mayConv.PULocationID,mayConv.DOLocationID))
junEdges = list(zip(juneConv.PULocationID,juneConv.DOLocationID))

marchG.add_edges_from(marEdges)
aprilG.add_edges_from(aprEdges)
mayG.add_edges_from(mayEdges)
juneG.add_edges_from(junEdges)

#Here we will calculate how dense each month's network is to see how much of the possible relationships of pickup locations and dropoff locations are present
st.subheader("Density of pickup and drop-off locations:")
st.write("March Density: {}".format(nx.density(marchG)))
st.write("April Density: {}".format(nx.density(aprilG)))
st.write("May Density: {}".format(nx.density(mayG)))
st.write("June Density: {}".format(nx.density(juneG)))

#Next we will make a function that will make a histogram for each month based on how many locations each pickup spot went to
def degreeHistogram(month,monthName):
    degrees = nx.degree_histogram(month)
    plt.bar( x=range(len(degrees)), height=degrees )
    plt.xlabel("Number of Destinations, x")
    plt.ylabel("Number of Pickup Locations with x Destinations")
    plt.title("Degree Histogram of Taxi Rides in {} 2020".format(monthName))
    st.pyplot(plt.gcf())
    plt.clf()

#We can also make a function that will draw out the connections between locations
def drawNetwork(month):
    plt.figure(figsize=(10,10))
    nx.draw(month, with_labels=True,node_color="lightgray",node_size=500,font_weight="bold")
    st.pyplot(plt.gcf())
    plt.clf()

st.sidebar.markdown("Which month would you like to see a Network Analysis of?")
choice = st.sidebar.selectbox("Select a month:",("March","April","May","June"))
if(choice=="March"):
    degreeHistogram(marchG,"March")
    st.subheader("Network Drawing of March")
    drawNetwork(marchG)
elif(choice=="April"):
    degreeHistogram(aprilG,"April")
    st.subheader("Network Drawing of April")
    drawNetwork(aprilG)
elif(choice=="May"):
    degreeHistogram(mayG,"May")
    st.subheader("Network Drawing of May")
    drawNetwork(mayG)
elif(choice=="June"):
    degreeHistogram(juneG,"June")
    st.subheader("Network Drawing of June")
    drawNetwork(juneG)

st.sidebar.markdown("Drawing the network graph may take a very long time (up to a few minutes!), please have patience, thank you.")

#Now we will find which locations are most frequently traveled by proportion through betweenness centrality
def bCent(month,monthName):
    bc = nx.betweenness_centrality(month)
    bc = pd.Series(bc)
    st.write("The betweenness centrality for the month {} are as follows:".format(monthName))
    st.write(bc.sort_values(ascending=False).head())

st.subheader("Betweenness Centrality")
bCent(marchG,"March")
bCent(aprilG,"April")
bCent(mayG,"May")
bCent(juneG,"June")

#For another analysis we're doing, we only need certain columns of taxi data, miscellaneous data like ID's and data that is largely consistent across all taxi rides like the mta tax and improvement surcharge are unnecessary.
march = march.drop(columns=["VendorID","RatecodeID","store_and_fwd_flag","PULocationID","DOLocationID","payment_type","mta_tax","improvement_surcharge"])
april = april.drop(columns=["VendorID","RatecodeID","store_and_fwd_flag","PULocationID","DOLocationID","payment_type","mta_tax","improvement_surcharge"])
may = may.drop(columns=["VendorID","RatecodeID","store_and_fwd_flag","PULocationID","DOLocationID","payment_type","mta_tax","improvement_surcharge"])
june = june.drop(columns=["VendorID","RatecodeID","store_and_fwd_flag","PULocationID","DOLocationID","payment_type","mta_tax","improvement_surcharge"])

#We create a function to group the taxi data by the pickup date, so that we know the totals of each column for each day
def groupbyDate(data):
    data["pickupDate"]=data.tpep_pickup_datetime.dt.floor('D')
    data=data.groupby(data.pickupDate).sum()
    return(data)

#We now concatenate the data into one large dataframe containing relevant available taxi data and group the data by each date, summing up each columns data for each date
taxi = pd.concat([march,april,may,june])
taxi = groupbyDate(taxi)

#We merge the taxi data and the COVID-19 data based on the date. Now we have our dataset ready to be analyzed
merged = pd.merge(taxi,cData,left_index=True,right_index=True)

#I am exporting this data in case anyone needs it to follow along with
merged.to_csv("output.csv")

st.header("Analysis of Correlations")

#Let's make a correlation coefficient heatmap to visualize which variables may have a strong correlation to investigate further
corr = np.corrcoef(merged,rowvar=False)
plt.figure(figsize=(15,10))
sns.heatmap(corr,annot=True)
plt.xticks( np.arange(11)+0.5, merged.columns, rotation=35 )
plt.yticks( np.arange(11)+0.5, merged.columns, rotation=0 )
plt.title("Heatmap of Correlation Coefficients")
st.pyplot(plt.gcf())
plt.clf()

#Now we will make scatter plots to see how some of these interesting variables look like when plotted against each other
plt.scatter(merged["passenger_count"],merged["MN_CASE_COUNT"])
plt.title("Passengers and COVID-19 Cases in New York City (per day)")
plt.xlabel("# of Yellow Taxi Passengers (in one day)")
plt.ylabel("# of COVID-19 Cases (in one day)")
st.pyplot(plt.gcf())
plt.clf()

plt.scatter(merged["trip_distance"],merged["MN_CASE_COUNT"])
plt.title("Trip Distance and COVID-19 Cases in New York City (per day)")
plt.xlabel("Total Distance Traveled by Yellow Taxis (miles in one day)")
plt.ylabel("# of COVID-19 Cases (in one day)")
st.pyplot(plt.gcf())
plt.clf()

plt.scatter(merged["passenger_count"],merged["MN_DEATH_COUNT"])
plt.title("Passengers and COVID-19 Deaths in New York City (per day)")
plt.xlabel("# of Yellow Taxi Passengers (in one day)")
plt.ylabel("# of COVID-19 Deaths (in one day)")
st.pyplot(plt.gcf())
plt.clf()

plt.scatter(merged["trip_distance"],merged["MN_DEATH_COUNT"])
plt.title("Trip Distance and COVID-19 Deaths in New York City (per day)")
plt.xlabel("Total Distance Traveled by Yellow Taxis (miles in one day)")
plt.ylabel("# of COVID-19 Deaths (in one day)")
st.pyplot(plt.gcf())
plt.clf()

#We should do some hypothesis tests to see if the difference in population means is statistically significant. We will be using an alpha level of 0.05 to conduct our tests. Any p-values that are less than this alpha level will result in rejecting the null hypothesis for that test and concluding
# that the difference in population means between these variables is statistically significant.
st.subheader("Hypothesis Testing")
alpha = 0.05

#Is there a difference between population means of passengers between days with a high amount of cases (>=100) and days with less cases (<100)?
moreCases = merged[merged["MN_CASE_COUNT"]>=100]
lessCases = merged[merged["MN_CASE_COUNT"]<100]
statistic, pvalue = stats.ttest_ind(moreCases["passenger_count"], lessCases["passenger_count"], equal_var=False)
st.write("The difference in population means of the number of passengers between days with >=100 cases and days with <100 cases is statisically significant: ")
st.write(pvalue < alpha)
st.write("P-value:")
st.write(pvalue)

#Is there a difference between population means of total miles traveled between days with a high amount of cases (>=100) and days with less cases (<100)?
statistic, pvalue = stats.ttest_ind(moreCases["trip_distance"], lessCases["trip_distance"], equal_var=False)
st.write("The difference in population means of the number of miles traveled between days with >=100 cases and days with <100 cases is statisically significant: ")
st.write(pvalue < alpha)
st.write("P-value:")
st.write(pvalue)

#Is there a difference between population means of passengers between days with a high amount of deaths (>=10) and days with less deaths (<10)?
moreDeaths = merged[merged["MN_DEATH_COUNT"]>=10]
lessDeaths = merged[merged["MN_DEATH_COUNT"]<10]
statistic, pvalue = stats.ttest_ind(moreDeaths["passenger_count"], lessDeaths["passenger_count"], equal_var=False)
st.write("The difference in population means of the number of passengers between days with >=10 deaths and days with <10 deaths is statisically significant: ")
st.write(pvalue < alpha)
st.write("P-value:")
st.write(pvalue)

#Is there a difference between population means of total miles traveled between days with a high amount of deaths(>=10) and days with less deaths (<10)?
statistic, pvalue = stats.ttest_ind(moreDeaths["trip_distance"], lessDeaths["trip_distance"], equal_var=False)
st.write("The difference in population means of the number of miles traveled between days with >=10 deaths and days with <10 deaths is statisically significant: ")
st.write(pvalue < alpha)
st.write("P-value:")
st.write(pvalue)

st.header("Link to the Repository:")

st.write("https://github.com/DongsooDKim/nyc-taxis-covid-19")