import pandas as pd

# Load data from the CSV file to a DataFrame.
file1 = open("Output_Converted_2nd.csv")
df1 = pd.read_csv(file1, delimiter=",")
arr1 = []
arr2 = []
# Record the latitude values of the starting & ending points.
for i in range(len(df1)):
    arr1.append(df1.loc[i, "start_latitude"])
    arr2.append(df1.loc[i, "end_latitude"])

# Load metadata to a DataFrame.
file2 = open("metadata_for_check.csv")
df2 = pd.read_csv(file2, delimiter=",")
arr3 = []
arr4 = []
# Only keep the records without any information about UTLA (English Upper Tier Local Authorities).
for i in range(len(df2)):
    if pd.isnull(df2.loc[i, "startUTLA"]):
        arr3.append(df2.loc[i, "startLat"])
    if pd.isnull(df2.loc[i, "endUTLA"]):
        arr4.append(df2.loc[i, "endLat"])

# Make the comparison. Once the starting or ending points have no information regarding UTLA, the record of that branch will be dropped.
for i in range(len(arr1)):
    if arr1[i] in arr3 or arr2[i] in arr4:
        df1.drop(i, inplace=True)

# Clean the result and export the output as a CSV file using the name of 'Output_WGS_84_3rd.csv'.
df1 = df1.drop(columns=['id', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude'])
df1.to_csv("Output_WGS_84_3rd.csv", sep=",", index=False)
