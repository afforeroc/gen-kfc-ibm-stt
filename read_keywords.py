import pandas as pd
import xlrd

data_frame = pd.read_excel('keywords.xls')
keyword_list = str(data_frame.iloc[:,0].values.tolist())
print(keyword_list)
