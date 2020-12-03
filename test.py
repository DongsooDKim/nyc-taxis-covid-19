import zipfile
import pandas as pd

zip = zipfile.ZipFile("yellow_tripdata_2020-03.zip")
zip.extractall()
df = pd.read_csv("yellow_tripdata_2020-03.csv")