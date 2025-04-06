import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from MeanStatsPlotsHeuristics import y_label_line

df_b1=pd.read_csv("./DataFiles/19-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b2=pd.read_csv("./DataFiles/19-02-2025-2/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b3=pd.read_csv("./DataFiles/20-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b4=pd.read_csv("./DataFiles/20-02-2025-2/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b5=pd.read_csv("./DataFiles/20-02-2025-3/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b6=pd.read_csv("./DataFiles/20-02-2025-4/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b7=pd.read_csv("./DataFiles/21-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b8=pd.read_csv("./DataFiles/21-02-2025-2/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b9=pd.read_csv("./DataFiles/21-02-2025-3/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b10=pd.read_csv("./DataFiles/21-02-2025-4/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b11=pd.read_csv("./DataFiles/21-02-2025-5/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b12=pd.read_csv("./DataFiles/22-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b13=pd.read_csv("./DataFiles/22-02-2025-2/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b14=pd.read_csv("./DataFiles/23-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b15=pd.read_csv("./DataFiles/23-02-2025-2/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b16=pd.read_csv("./DataFiles/24-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b17=pd.read_csv("./DataFiles/24-02-2025-2/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b18=pd.read_csv("./DataFiles/24-02-2025-3/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b19=pd.read_csv("./DataFiles/24-02-2025-4/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
df_b20=pd.read_csv("./DataFiles/25-02-2025/LinkStatsAggregateResultsBase.csv") #.csv file of base controller performance
dfs_b=[df_b1, df_b2, df_b3, df_b4, df_b5, df_b6, df_b7, df_b8, df_b9, df_b10, df_b11, df_b12, df_b13, df_b14, df_b15, df_b16, df_b17, df_b18, df_b19, df_b20]
min_rows=min(df.shape[0] for df in dfs_b)
dfs_b=[df.iloc[:min_rows] for df in dfs_b]

df_e1=pd.read_csv("./DataFiles/19-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e2=pd.read_csv("./DataFiles/19-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e3=pd.read_csv("./DataFiles/20-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e4=pd.read_csv("./DataFiles/20-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e5=pd.read_csv("./DataFiles/20-02-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e6=pd.read_csv("./DataFiles/20-02-2025-4/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e7=pd.read_csv("./DataFiles/21-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e8=pd.read_csv("./DataFiles/21-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e9=pd.read_csv("./DataFiles/21-02-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e10=pd.read_csv("./DataFiles/21-02-2025-4/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e11=pd.read_csv("./DataFiles/21-02-2025-5/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e12=pd.read_csv("./DataFiles/22-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e13=pd.read_csv("./DataFiles/22-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e14=pd.read_csv("./DataFiles/23-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e15=pd.read_csv("./DataFiles/23-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e16=pd.read_csv("./DataFiles/24-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e17=pd.read_csv("./DataFiles/24-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e18=pd.read_csv("./DataFiles/24-02-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e19=pd.read_csv("./DataFiles/24-02-2025-4/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e20=pd.read_csv("./DataFiles/25-02-2025/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
dfs_e=[df_e1, df_e2, df_e3, df_e4, df_e5, df_e6, df_e7, df_e8, df_e9, df_e10, df_e11, df_e12, df_e13, df_e14, df_e15, df_e16, df_e17, df_e18, df_e19, df_e20]
min_rows=min(df.shape[0] for df in dfs_e)
dfs_e=[df.iloc[:min_rows] for df in dfs_e]

x_label=dfs_e[0].columns[0] #X axis label
duration=len(dfs_b[0][x_label])*60 #Simulation time (in seconds)

x_base=pd.Series(np.linspace(0, duration, len(dfs_b[0][x_label]))) #X axis values for base controller stats
x_enhanced=pd.Series(np.linspace(0, duration, len(dfs_e[0][x_label]))) #X axis values for enhanced controller stats

#Create folder for saving figures
save_folder="./Plots/Mean"
os.makedirs(save_folder, exist_ok=True)

#Performance File
x1=180 #time instant when Elephant Flows are started
x2=180+600 #time instant when no more Elephant Flows are started
x3=180+600+600 #time instant when all Elephant Flows packets have been transmitted

masks=[]
masks.append(x_base<x1)
masks.append((x_base>=x1) & (x_base<x3))
masks.append(x_base>=x3)

file_path=os.path.join(save_folder, "Performance File")
with open(file_path, "w") as stat_file:
    stat_file.write(f"Performance Comparison between benchmark ECMP controller and enhanced ECMP controller\n")
    stat_file.write(f"\n")

################################################################################################herd 0 Mean Utilization 1
y_label_line=dfs_b[0].columns[1] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

#Plot figure
plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Utilization Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Utilization Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Max Utilization 2
y_label_line=dfs_b[0].columns[2] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20


sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Utilization Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Utilization Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Mean Occupation 3
y_label_line=dfs_b[0].columns[3] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Occupation Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Occupation Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Max Occupation 4
y_label_line=dfs_b[0].columns[4] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Occupation Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Occupation Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Mean Congestion 5
y_label_line=dfs_b[0].columns[5] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Congestion Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Congestion Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Max Congestion 6
y_label_line=dfs_b[0].columns[6] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Congestion Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Congestion Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Mean Drop Rate 7
y_label_line=dfs_b[0].columns[7] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Drop Rate Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper left', fontsize=7, markerscale=0.7)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Drop Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Max Drop Rate 8
y_label_line=dfs_b[0].columns[8] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Drop Rate (percentage) in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper left', fontsize=7, markerscale=0.7)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Drop Rate Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################herd 0 Active Links 9
y_label_line=dfs_b[0].columns[9] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of active Links in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Active Links Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")


################################################################################################herd 0 Congested Links 10
y_label_line=dfs_b[0].columns[10] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b.astype(int), marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e.astype(int), marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of congested links in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Congested Links Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")


################################################################################################herd 0 Idle Link 11
y_label_line=dfs_b[0].columns[11] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b.astype(int), marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e.astype(int), marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of Idle Links in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Idle Links Comparison in herd 0\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask].astype(int))
    max_e=np.max(mean_series_e[mask].astype(int))

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")


################################################################################################Core Mean Utilization 45
y_label_line=dfs_b[0].columns[45] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Utilization Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Utilization Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Max Utilization 46
y_label_line=dfs_b[0].columns[46] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Utilization Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Utilization Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Mean Occupation 47
y_label_line=dfs_b[0].columns[47] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Occupation Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Occupation Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Max Occupation 48
y_label_line=dfs_b[0].columns[48] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Occupation Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Occupation Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")


################################################################################################Core Mean Congestion 49
y_label_line=dfs_b[0].columns[49] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Congestion Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Congestion Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Max Congestion 50
y_label_line=dfs_b[0].columns[50] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Congestion Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='lower center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Congestion Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")
################################################################################################Core Mean Drop Rate 51
y_label_line=dfs_b[0].columns[51] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Mean Drop Rate Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper left', fontsize=7, markerscale=0.7)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Mean Drop Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Max Drop Rate 52
y_label_line=dfs_b[0].columns[52] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b, marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Max Drop Rate Rate (percentage) at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper left', fontsize=7, markerscale=0.7)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Max Drop Rate Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Active Links 53
y_label_line=dfs_b[0].columns[53] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b.astype(int), marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e.astype(int), marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of active Links at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Active Links Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Congested Links 54
y_label_line=dfs_b[0].columns[54] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b.astype(int), marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e.astype(int), marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of congested links at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Congested Links Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask])
    max_e=np.max(mean_series_e[mask])

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")

################################################################################################Core Idle Link 55
y_label_line=dfs_b[0].columns[55] #Y axis label

sum_series_b=sum(df[y_label_line] for df in dfs_b)
mean_series_b=sum_series_b/20

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

plt.plot(x_base, mean_series_b.astype(int), marker='o', linestyle='-', label=f"Base ECMP")
plt.plot(x_enhanced, mean_series_e.astype(int), marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of Idle Links at Core Level")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper center', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

#Save Performance Indexes
mean_series_e=np.interp(x_base, x_enhanced, mean_series_e) #interpolation of mean_series_e over x_base points

with open(file_path, "a") as stat_file:
    stat_file.write(f"Idle Links Comparison at Core Level\n")
    stat_file.write(f"\n")

for mask in masks:
    max_b=np.max(mean_series_b[mask].astype(int))
    max_e=np.max(mean_series_e[mask].astype(int))

    average_percentage_diff=(np.mean(mean_series_e[mask])-np.mean(mean_series_b[mask]))/np.mean(mean_series_b[mask])*100

    with open(file_path, "a") as stat_file:
        stat_file.write(f"Max value for benchmark controller: {max_b}\n")
        stat_file.write(f"Max value for enhanced controller: {max_e}\n")
        stat_file.write(f"Average percentage difference between enhanced controller and benchmark controller: {average_percentage_diff}\n")
        stat_file.write(f"\n")

with open(file_path, "a") as stat_file:
    stat_file.write(f"\n")
