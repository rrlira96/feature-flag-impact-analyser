
import os
import pandas as pd
import csv

directory = 'ci_time'
add_ff_times = []
rm_ff_times = []

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        df = pd.read_csv(f)
        for index, row in df.iterrows():
            if row['is_feature_flag'] == True:
                if row['ff_add_or_remove'] == 'add':
                    add_ff_times.append(row['ci_time'])
                    print('Repo {}, time {}, is_ff {}'.format(row['repository'], row['ci_time'], row['ff_add_or_remove']))
                else:
                    rm_ff_times.append(row['ci_time'])
                    print('Repo {}, time {}, is_ff {}'.format(row['repository'], row['ci_time'], row['ff_add_or_remove']))

                

file = open('ci_time_add_rm_ff.csv', 'w')
writer = csv.writer(file)
header = ['add_ff_times', 'rm_ff_times']
writer.writerow(header)

for i in range(len(add_ff_times)):
    if i >= len(rm_ff_times):
        data = [add_ff_times[i], None]
    else:    
        data = [add_ff_times[i], rm_ff_times[i]]
    writer.writerow(data)

file.close()