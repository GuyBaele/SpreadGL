import pandas as pd

file1 = open("/InputPath/Output_Combined_3rd.csv")
df1 = pd.read_csv(file1, delimiter=",")
arr1 = []
arr2 = []
for i in range(len(df1)):
    arr1.append(df1.loc[i, "uk_start_latitude"])
    arr2.append(df1.loc[i, "uk_end_latitude"])
print(len(arr1))

file2 = open("/InputPath/metadata_for_check.csv")
df2 = pd.read_csv(file2, delimiter=",")
arr3 = []
arr4 = []
for i in range(len(df2)):
    if pd.isnull(df2.loc[i, "startUTLA"]):
        arr3.append(df2.loc[i, "startLat"])
    if pd.isnull(df2.loc[i, "endUTLA"]):
        arr4.append(df2.loc[i, "endLat"])

counter = 0
for i in range(len(arr1)):
    if arr1[i] in arr3 or arr2[i] in arr4:
        df1.drop(i, inplace=True)
        counter += 1
print(counter) 
print(df1)

df1 = df1.drop(columns=['uk_start_latitude', 'uk_start_longitude', 'uk_end_latitude', 'uk_end_longitude'])
df1.to_csv("/OutputPath/Final_Output_4th.csv", sep=",", index=False)
