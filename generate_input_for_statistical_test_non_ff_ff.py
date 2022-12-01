
import os
import pandas as pd
import csv

directory = 'ci_time'
non_ff_times = []
ff_times = []

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        df = pd.read_csv(f)
        for index, row in df.iterrows():
            if row['is_feature_flag'] == True:
                if row['ff_add_or_remove'] == 'add':
                    ff_times.append(row['ci_time'])
                    print('Repo {}, time {}, is_ff {}'.format(row['repository'], row['ci_time'], row['is_feature_flag']))
                else:
                    non_ff_times.append(row['ci_time'])
            else:
                non_ff_times.append(row['ci_time'])
                

file = open('ci_time_add_ff.csv', 'w')
writer = csv.writer(file)
header = ['non_ff_time', 'ff_time']
writer.writerow(header)

for i in range(len(non_ff_times)):
    if i >= len(ff_times):
        data = [non_ff_times[i], None]
    else:    
        data = [non_ff_times[i], ff_times[i]]
    writer.writerow(data)

file.close()