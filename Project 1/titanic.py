#Restart
import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import seaborn as sns
import matplotlib as mlt
"%matplotlib.inline"

import matplotlib.pyplot as plt 
titanic = pd.read_csv(r'Project 1\titanic\train.csv')
print(titanic.head())
print(titanic["Embarked"].head())
print(titanic.info())
print("\n", titanic["Age"].head() ,"\n", titanic["Sex"].head() ,"\n", titanic["Name"].head(),"\n", titanic["Pclass"].head())
# sns.catplot(data = titanic , x = "Sex" , kind ="count" )
# plt.show()

# sns.catplot(x = "Pclass" , kind = "count" , data = titanic , hue = "Sex")
# plt.show()
def male_female(passenger):
    age, sex = passenger
    if age < 16:
        return "child"
    else:
        return sex

# Correctly apply the function to create the 'person' column
titanic["person"] = titanic[["Age", "Sex"]].apply(male_female, axis=1)

# Print the first few rows to verify the new column
print(titanic[["Age", "Sex", "person"]].head())

print(titanic.head())
#sns.catplot(data=titanic , x = "Sex"  , hue = "person" , kind = "count")
# titanic["Age"].hist(bins = 100)
# plt.show()
print(titanic["Age"].mean())
print(titanic["person"].value_counts())

# fig = sns.FacetGrid(data=titanic , hue = "Sex" , aspect=4 )
# fig.map(sns.kdeplot , "Age" , fill = True)

# oldest= titanic["Age"].max()
# fig.set(xlim=(0,oldest))
# fig.add_legend()
# plt.show()

# fig = sns.FacetGrid(data=titanic , hue = "person" , aspect=4 )
# fig.map(sns.kdeplot , "Age" , fill = True)

# oldest= titanic["Age"].max()
# fig.set(xlim=(0,oldest))
# fig.add_legend()
# plt.show()

deck = titanic["Cabin"].dropna()  # Drop rows where Cabin is NaN

# Extract the first letter of each cabin (deck level)
levels = [level[0] for level in deck]  # Extract the first character of each cabin string

# Create a DataFrame for the cabin levels
cabin = pd.DataFrame(levels, columns=["Cabin"])  # Properly assign column name

# Visualize the distribution of cabin levels
# sns.catplot(
#     x="Cabin", 
#     data=cabin, 
#     kind="count", 
#     palette="winter_d", 
#     aspect=1.5
# )

# # Add labels and title
# plt.title("Distribution of Cabin Levels", fontsize=16)
# plt.xlabel("Cabin Deck Level", fontsize=12)
# plt.ylabel("Count", fontsize=12)

# # Show the plot
# plt.tight_layout()
# plt.show()

# cabin = cabin[cabin.Cabin != "T"]
# sns.catplot(
#     x="Cabin", 
#     data=cabin, 
#     kind="count", 
#     palette="summer", 
#     aspect=1.5
# )

# # Add labels and title
# plt.title("Distribution of Cabin Levels", fontsize=16)
# plt.xlabel("Cabin Deck Level", fontsize=12)
# plt.ylabel("Count", fontsize=12)

# # Show the plot
# plt.tight_layout()
# plt.show()

# print(titanic["Embarked"].head())
# sns.catplot(data = titanic , x = "Embarked" , hue = "Pclass" , kind = "count" , hue_order= ["C" , "Q" , "S"])
# plt.tight_layout()
# plt.show()

titanic["Alone"] = titanic.SibSp + titanic.Parch
print(titanic["Alone"])

titanic["Alone"].loc[titanic["Alone"] > 0] = "With Family"
titanic["Alone"].loc[titanic["Alone"] == 0] = "Alone"

print(titanic["Alone"])

# sns.catplot(data = titanic , x = "Alone" , palette= "summer" , kind = "count")
# plt.show()

print(titanic.head())

titanic["Survivor"] = titanic.Survived.map({0: "No" , 1: "Yes"})
print(titanic["Survivor"])

# sns.catplot(hue = "Pclass" ,kind = "count" , x = "Survivor" , data = titanic , palette= "summer")
# plt.show()

# sns.catplot(kind ="point" ,hue = "person" ,x = "Pclass" , y = "Survived" , data = titanic)
# plt.show()

# sns.lmplot(hue = "Pclass" ,x = "Age" ,y = "Survived" ,data = titanic)
# plt.show()

# generations = [10,20,30,40,60,80]
# sns.lmplot(x = "Age", y= "Survived" , data = titanic , hue = "Pclass", x_bins=generations)
# plt.show()

print(titanic.head())