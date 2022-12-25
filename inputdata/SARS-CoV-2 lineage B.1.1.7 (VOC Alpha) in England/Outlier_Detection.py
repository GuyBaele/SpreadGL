import pandas as pd

file1 = open("Output_Converted_2nd.csv")
df1 = pd.read_csv(file1, delimiter=",")
arr1 = []
arr2 = []
for i in range(len(df1)):
    arr1.append(df1.loc[i, "start_latitude"])
    arr2.append(df1.loc[i, "end_latitude"])
# print(len(arr1))

file2 = open("metadata_for_check.csv")
df2 = pd.read_csv(file2, delimiter=",")
arr3 = []
arr4 = []
for i in range(len(df2)):
    if pd.isnull(df2.loc[i, "startUTLA"]):
        arr3.append(df2.loc[i, "startLat"])
    if pd.isnull(df2.loc[i, "endUTLA"]):
        arr4.append(df2.loc[i, "endLat"])

# counter = 0
for i in range(len(arr1)):
    if arr1[i] in arr3 or arr2[i] in arr4:
        df1.drop(i, inplace=True)
        # counter += 1
# print(counter)

df1 = df1.drop(columns=['id', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude'])
df1.to_csv("Output_WGS_84_3rd.csv", sep=",", index=False)
# print(df1)
