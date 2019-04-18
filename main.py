import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

df1 = pd.read_csv('2015-building-energy-benchmarking.csv')
df2016 = pd.read_csv('2016-building-energy-benchmarking.csv')

##Let's separate the location info in the dataframe
location = df1["Location"].str.split(",", n = 8, expand = True)
location.insert(loc = 0, column = "OSEBuildingID",  value = df1["OSEBuildingID"])
location.columns = ['OSEBuildingID','Latitude','Longitude','Address','City','State','Zip Code','Needs Recode']

location['Latitude'] = location['Latitude'].str.replace("{'latitude':",'')
location['Latitude'] = location['Latitude'].str.replace("'",'')
location['Longitude'] = location['Longitude'].str.replace("'longitude':",'')
location['Longitude'] = location['Longitude'].str.replace("'",'')
location['Address'] = location['Address'].str.replace("'human_address':",'')
location['Address'] = location['Address'].str.replace("'{",'')
location['Address'] = location['Address'].str.replace('"address":','')
location['Address'] = location['Address'].str.replace('"','')
location = location.drop(['City','State', 'Needs Recode'],1)
location['Zip Code'] = location['Zip Code'].str.replace('"zip":','')
location['Zip Code'] = location['Zip Code'].str.replace("}'",'')
location['Zip Code'] = location['Zip Code'].str.replace('"','')
df1 = df1.drop(["Location"],1)

##merging the location and the rest of the dataframe
df1 = df1.merge(location,left_on = 'OSEBuildingID', right_on = 'OSEBuildingID')

#Let's define the source to site loss and clean and impute the other rows
df2016 = df2016.dropna(subset=['ENERGYSTARScore'])
df2016 = df2016[df2016['SourceEUIWN(kBtu/sf)'] > 0]
df2016 = df2016[df2016['SiteEUIWN(kBtu/sf)'] > 0]
df2016['lossEUIWN(kBtu/sf)'] = df2016['SourceEUIWN(kBtu/sf)'] / df2016['SiteEUIWN(kBtu/sf)']

for i, row in df2016.iterrows():
    if df2016['SiteEUIWN(kBtu/sf)'][i] <= 0:
        df2016['lossEUIWN(kBtu/sf)'][i] = df2016['SourceEUI(kBtu/sf)'][i] / df2016['SiteEUI(kBtu/sf)'][i]

df1['NumberofFloors'] = df1['NumberofFloors'].fillna(df1['NumberofFloors'].mode()[0])

#Let's define the percentage of the energy use based on the energy source
df2016['Electricity'] = df2016['Electricity(kBtu)']/df2016['SiteEnergyUse(kBtu)']*100
df2016['Steam'] = df2016['SteamUse(kBtu)']/df2016['SiteEnergyUse(kBtu)']*100
df2016['NaturalGas'] = df2016['NaturalGas(kBtu)']/df2016['SiteEnergyUse(kBtu)']*100
#df2['OtherFuelPercentage'] = df2['OtherFuelUse(kBtu)']/df2['SiteEnergyUse(kBtu)']

####-----------------------------------Energy Usage Study-------------------------------###
#Property type energy usage dependency
buildingTypeEnergyStar = df2016.groupby(['PrimaryPropertyType'])['ENERGYSTARScore'].mean().reset_index()
buildingTypeLoss = df2016.groupby(['PrimaryPropertyType'])['lossEUIWN(kBtu/sf)'].mean().reset_index()
buildingTypeEnergyPercentage = df2016.groupby(['PrimaryPropertyType'])['Electricity','Steam',
                                          'NaturalGas'].mean().reset_index()

#Let's look at the location dependcy of the energy usage
#zipCode = df2016.groupby(['ZipCode'])['ENERGYSTARScore'].mean().reset_index()
df2016['Neighborhood'] = map(lambda x: x.lower(), df2016['Neighborhood'])
neighborhoodEnergyStar = df2016.groupby(['Neighborhood'])['ENERGYSTARScore'].mean().reset_index()
neighborhoodLoss = df2016.groupby(['Neighborhood'])['lossEUIWN(kBtu/sf)'].mean().reset_index()
neighborhoodEnergyPercentage = df2016.groupby(['Neighborhood'])['Electricity','Steam',
                                          'NaturalGas'].mean().reset_index()

f, axes = plt.subplots(2, 1,sharex = True, figsize=(5,5))
sns.set(style="whitegrid")
color1 = [[0.6,0.6,0.6],[0.7,0.7,0.7],[0.8,0.8,0.8],[0.5,0.5,0.5],[0,0,0],[0.1,0.1,0.1],[0.3,0.3,0.3],
          [0.9,0.9,0.9],[0.1,0.1,0.1],[0.3,0.3,0.3],[0.2,0.2,0.2],[0.4,0.4,0.4],[0.1,0.1,0.1],[0.4,0.4,0.4],
          [0.3,0.3,0.3],[0.45,0.45,0.45],[0.3,0.3,0.3],[0.7,0.7,0.7],[0.5,0.5,0.5],[0.4,0.4,0.4]]

color2 = [[0.5,0.5,0.5],[0.5,0.5,0.5],[0.6,0.6,0.6],[0.5,0.5,0.5],[0.6,0.6,0.6],[0.6,0.6,0.6],[0,0,0],
          [0.1,0.1,0.1],[0.4,0.4,0.4],[0.4,0.4,0.4],[0.1,0.1,0.1],[0.45,0.45,0.45],[0.15,0.15,0.15]]

ax1 = sns.barplot(y = buildingTypeEnergyStar['PrimaryPropertyType'], x = buildingTypeEnergyStar['ENERGYSTARScore'],
            ax=axes[0], palette=color1)
ax2 = sns.barplot(y = neighborhoodEnergyStar['Neighborhood'], x = neighborhoodEnergyStar['ENERGYSTARScore'], 
            ax=axes[1], palette=color2)

ax1.get_xaxis().set_visible(False)
ax1.set_xlim([0,100])
ax2.set_xlim([0,100])
plt.tight_layout()
plt.show()
#f.savefig('EnergyStarBarplots.eps', format='eps', dpi=1000)

f, axes = plt.subplots(2, 1,sharex = True,figsize=(5,5))
sns.set(style="whitegrid")
color1 = [[0.6,0.6,0.6],[0.6,0.6,0.6],[0.7,0.7,0.7],[0.7,0.7,0.7],[0.85,0.85,0.85],[0,0,0],[0.2,0.2,0.2],
          [0.2,0.2,0.2],[0.3,0.3,0.3],[0.2,0.2,0.2],[0.3,0.3,0.3],[0.05,0.05,0.05],[0.1,0.1,0.1],
          [0.7,0.7,0.7],[0.3,0.3,0.3],[0.8,0.8,0.8],[0.3,0.3,0.3],[0.5,0.5,0.5],[0.5,0.5,0.5],[0.9,0.9,0.9]]

color2 = [[0.6,0.6,0.6],[0.7,0.7,0.7],[0.4,0.4,0.4],[0.5,0.5,0.5],[0.85,0.85,0.85],[0.75,0.75,0.75],
          [0.4,0.4,0.4],[0.7,0.7,0.7],[0,0,0],[0.6,0.6,0.6],[0.4,0.4,0.4],[0.7,0.7,0.7],[0.2,0.2,0.2]]

ax1 = sns.barplot(y = buildingTypeLoss['PrimaryPropertyType'], x = buildingTypeLoss['lossEUIWN(kBtu/sf)'],
            ax=axes[0], palette=color1)
ax2 = sns.barplot(y = neighborhoodLoss['Neighborhood'], x = neighborhoodLoss['lossEUIWN(kBtu/sf)'], 
            ax=axes[1], palette=color2)

ax1.get_xaxis().set_visible(False)
ax1.set_xlim([0,3])
ax2.set_xlim([0,3])
plt.tight_layout()
plt.show()
#f.savefig('EnergyBarplots.eps', format='eps', dpi=1000)

f, axes = plt.subplots(2, 1,figsize=(5,5))
colorStacked = [[0,0,0],[0.4,0.4,0.4],[0.8,0.8,0.8]]
neighborhoodEnergyPercentage = neighborhoodEnergyPercentage[['Electricity','Steam','NaturalGas']]
buildingTypeEnergyPercentage = buildingTypeEnergyPercentage[['Electricity','Steam','NaturalGas']]

ax1 = buildingTypeEnergyPercentage.set_index(buildingTypeLoss['PrimaryPropertyType']).plot.barh(stacked=True, 
                                            ax = axes[0], color=colorStacked)
ax2 = neighborhoodEnergyPercentage.set_index(neighborhoodLoss['Neighborhood']).plot.barh(stacked=True, 
                                            ax = axes[1], color=colorStacked)
ax1.set_xlim([0,100])
ax2.set_xlim([0,100])
ax1.legend(loc = [0.78, 1.02])
ax2.get_legend().remove()
plt.tight_layout()
f.subplots_adjust(top=0.9)
plt.show()
#f.savefig('EnergyPercentageBarplots.eps', format='eps', dpi=1000)

###-----------------------------------CO2 Emission Study-------------------------------###
hmap = df2016.drop(['OSEBuildingID','DataYear','SecondLargestPropertyUseTypeGFA','ThirdLargestPropertyUseTypeGFA',
                 'SiteEUI(kBtu/sf)','SourceEUI(kBtu/sf)','SiteEnergyUse(kBtu)','Electricity(kWh)',
                 'NaturalGas(therms)', 'Comments'], axis = 1)

corrmat = hmap.corr()
fig = plt.figure()
ax = sns.heatmap(corrmat, linewidth = 1, xticklabels=True, yticklabels=True)
plt.axis('equal')
plt.show()


binsYearBuilt = [1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010,2020]
df2016['BinnedYearBuilt'] = pd.cut(df2016['YearBuilt'], bins = binsYearBuilt)
CO2binnedYearBuilt = df2016.groupby(['BinnedYearBuilt'])['GHGEmissionsIntensity'].mean().reset_index()
CO2binnedPercentage = df2016.groupby(['BinnedYearBuilt'])['Electricity','Steam',
                                          'NaturalGas'].mean().reset_index()

sizeBins = [20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000, 70000, 
            80000, 90000, 100000, 250000, 2200000]
df2016['BinnedPropertyGFATotal'] = pd.cut(df1['PropertyGFATotal'], bins = sizeBins)
CO2propertySize = df2016.groupby(['BinnedPropertyGFATotal'])['GHGEmissionsIntensity'].mean().reset_index()
CO2propertyType = df2016.groupby(['PrimaryPropertyType'])['GHGEmissionsIntensity'].mean().reset_index()

areaBuildingType = df2016.groupby(['PrimaryPropertyType'])['PropertyGFATotal'].mean().reset_index()



xticklabels = ['00-10','10-20','20-30','30-40','40-50','50-60','60-70','70-80','80-90','90-00','00-10','10-20']
fig = plt.figure()
ax = sns.boxplot(x="BinnedYearBuilt", y="GHGEmissionsIntensity", data=df2016, palette="Blues")
ax.set_xticklabels(xticklabels, rotation = 45)
#ax.set_xticklabels(xlabels(), rotation=40)
plt.show()
fig.savefig('CO2BoxPlot.eps', format='eps', dpi=1000)


f, axes = plt.subplots(2, 1,figsize=(5,5))
labels = ['Electricity','Steam','NaturalGas']
sizes1 = [CO2binnedPercentage['Electricity'][2],CO2binnedPercentage['Steam'][2],
          CO2binnedPercentage['NaturalGas'][2]]
sizes2 = [CO2binnedPercentage['Electricity'][8],CO2binnedPercentage['Steam'][8],
          CO2binnedPercentage['NaturalGas'][8]]
explode = (0.05, 0, 0)
the_grid = GridSpec(1, 2)
plt.subplot(the_grid[0], aspect=1)
plt.pie(sizes1, explode = explode, labels=labels,colors=[[0.2,0.3,0.5],
        [0.7,0.9,0.9],[0.2,0.5,0.8]], autopct='%1.1f%%', shadow=True, startangle=70, radius = 1)
plt.title('1920-1930')
plt.subplot(the_grid[1], aspect=1)
plt.pie(sizes2, explode = explode, labels=labels,colors=[[0.2,0.3,0.5],
        [0.7,0.9,0.9],[0.2,0.5,0.8]], autopct='%1.1f%%', shadow=True, startangle=70, radius = 1)
plt.title('1980-1990')
#plt.axis('equal')
#plt.tight_layout()
plt.show()
f.savefig('CO2PiePlot.eps', format='eps', dpi=1000)


