import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df_e1=pd.read_csv("./DataFiles/25-02-2025-1/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e2=pd.read_csv("./DataFiles/25-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e3=pd.read_csv("./DataFiles/26-02-2025-1/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e4=pd.read_csv("./DataFiles/26-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e5=pd.read_csv("./DataFiles/26-02-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e6=pd.read_csv("./DataFiles/26-02-2025-4/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e7=pd.read_csv("./DataFiles/26-02-2025-5/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e8=pd.read_csv("./DataFiles/27-02-2025-1/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e9=pd.read_csv("./DataFiles/27-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e10=pd.read_csv("./DataFiles/27-02-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e11=pd.read_csv("./DataFiles/27-02-2025-4/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e12=pd.read_csv("./DataFiles/27-02-2025-5/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e13=pd.read_csv("./DataFiles/28-02-2025-1/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e14=pd.read_csv("./DataFiles/28-02-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e15=pd.read_csv("./DataFiles/28-02-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e16=pd.read_csv("./DataFiles/28-02-2025-4/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e17=pd.read_csv("./DataFiles/01-03-2025-1/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e18=pd.read_csv("./DataFiles/01-03-2025-2/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e19=pd.read_csv("./DataFiles/01-03-2025-3/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
df_e20=pd.read_csv("./DataFiles/02-03-2025-1/LinkStatsAggregateResultsEnhanced.csv") #.csv file of enhanced controller performance
dfs_e=[df_e1, df_e2, df_e3, df_e4, df_e5, df_e6, df_e7, df_e8, df_e9, df_e10, df_e11, df_e12, df_e13, df_e14, df_e15, df_e16, df_e17, df_e18, df_e19, df_e20]
min_rows=min(df.shape[0] for df in dfs_e)
dfs_e=[df.iloc[:min_rows] for df in dfs_e]

df_g1=pd.read_csv("./DataFiles/25-02-2025-1/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g2=pd.read_csv("./DataFiles/25-02-2025-2/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g3=pd.read_csv("./DataFiles/26-02-2025-1/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g4=pd.read_csv("./DataFiles/26-02-2025-2/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g5=pd.read_csv("./DataFiles/26-02-2025-3/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g6=pd.read_csv("./DataFiles/26-02-2025-4/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g7=pd.read_csv("./DataFiles/26-02-2025-5/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g8=pd.read_csv("./DataFiles/27-02-2025-1/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g9=pd.read_csv("./DataFiles/27-02-2025-2/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g10=pd.read_csv("./DataFiles/27-02-2025-3/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g11=pd.read_csv("./DataFiles/27-02-2025-4/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g12=pd.read_csv("./DataFiles/27-02-2025-5/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g13=pd.read_csv("./DataFiles/28-02-2025-1/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g14=pd.read_csv("./DataFiles/28-02-2025-2/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g15=pd.read_csv("./DataFiles/28-02-2025-3/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g16=pd.read_csv("./DataFiles/28-02-2025-4/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g17=pd.read_csv("./DataFiles/01-03-2025-1/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g18=pd.read_csv("./DataFiles/01-03-2025-2/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g19=pd.read_csv("./DataFiles/01-03-2025-3/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
df_g20=pd.read_csv("./DataFiles/02-03-2025-1/LinkStatsAggregateResultsGreedy.csv") #.csv file of enhanced controller performance
dfs_g=[df_g1, df_g2, df_g3, df_g4, df_g5, df_g6, df_g7, df_g8, df_g9, df_g10, df_g11, df_g12, df_g13, df_g14, df_g15, df_g16, df_g17, df_g18, df_g19, df_g20]
min_rows=min(df.shape[0] for df in dfs_g)
dfs_g=[df.iloc[:min_rows] for df in dfs_g]

df_p1=pd.read_csv("./DataFiles/25-02-2025-1/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p2=pd.read_csv("./DataFiles/25-02-2025-2/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p3=pd.read_csv("./DataFiles/26-02-2025-1/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p4=pd.read_csv("./DataFiles/26-02-2025-2/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p5=pd.read_csv("./DataFiles/26-02-2025-3/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p6=pd.read_csv("./DataFiles/26-02-2025-4/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p7=pd.read_csv("./DataFiles/26-02-2025-5/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p8=pd.read_csv("./DataFiles/27-02-2025-1/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p9=pd.read_csv("./DataFiles/27-02-2025-2/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p10=pd.read_csv("./DataFiles/27-02-2025-3/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p11=pd.read_csv("./DataFiles/27-02-2025-4/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p12=pd.read_csv("./DataFiles/27-02-2025-5/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p13=pd.read_csv("./DataFiles/28-02-2025-1/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p14=pd.read_csv("./DataFiles/28-02-2025-2/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p15=pd.read_csv("./DataFiles/28-02-2025-3/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p16=pd.read_csv("./DataFiles/28-02-2025-4/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p17=pd.read_csv("./DataFiles/01-03-2025-1/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p18=pd.read_csv("./DataFiles/01-03-2025-2/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p19=pd.read_csv("./DataFiles/01-03-2025-3/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
df_p20=pd.read_csv("./DataFiles/02-03-2025-1/LinkStatsAggregateResultsProb.csv") #.csv file of enhanced controller performance
dfs_p=[df_p1, df_p2, df_p3, df_p4, df_p5, df_p6, df_p7, df_p8, df_p9, df_p10, df_p11, df_p12, df_p13, df_p14, df_p15, df_p16, df_p17, df_p18, df_p19, df_p20]
min_rows=min(df.shape[0] for df in dfs_p)
dfs_p=[df.iloc[:min_rows] for df in dfs_p]

x_label=dfs_e[0].columns[0] #X axis label
duration=2100 #Simulation time (in seconds)

x_enhanced=pd.Series(np.linspace(0, duration, len(dfs_e[0][x_label]))) #X axis values for enhanced controller stats
x_greedy=pd.Series(np.linspace(0, duration, len(dfs_g[0][x_label])))
x_prob=pd.Series(np.linspace(0, duration, len(dfs_p[0][x_label])))

#Create folder for saving figures
save_folder="./Plots/MeanHeuristic"
os.makedirs(save_folder, exist_ok=True)

#Performance File
x1=360 #time instant when Elephant Flows are started
x2=360+900 #time instant when no more Elephant Flows are started
x3=360+900+600 #time instant when all Elephant Flows packets have been transmitted

masks=[]
masks.append(x_enhanced<x1)
masks.append((x_enhanced>=x1) & (x_enhanced<x3))
masks.append(x_enhanced>=x3)

file_path=os.path.join(save_folder, "Performance File")
with open(file_path, "w") as stat_file:
    stat_file.write(f"Performance Comparison between benchmark ECMP controller and enhanced ECMP controller\n")
    stat_file.write(f"\n")

################################################################################################herd 0 Mean Utilization 1
y_label_line=dfs_e[0].columns[1] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

#Plot figure
plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Max Utilization 2
y_label_line=dfs_e[0].columns[2] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Mean Occupation 3
y_label_line=dfs_e[0].columns[3] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

sum_series_p=sum([dfs_p[0][y_label_line],
                 dfs_p[1][y_label_line],
                 dfs_p[2][y_label_line],
                 dfs_p[3][y_label_line]])
mean_series_p=sum_series_p/4

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Max Occupation 4
y_label_line=dfs_e[0].columns[4] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Mean Congestion 5
y_label_line=dfs_e[0].columns[5] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Max Congestion 6
y_label_line=dfs_e[0].columns[6] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Mean Drop Rate 7
y_label_line=dfs_e[0].columns[7] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Max Drop Rate 8
y_label_line=dfs_e[0].columns[8] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 0 Active Links
y_label_line=dfs_e[0].columns[9] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################herd 1 Active Links
y_label_line=dfs_e[0].columns[20] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of active Links in Second herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################herd 2 Active Links
y_label_line=dfs_e[0].columns[31] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of active Links in Third herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################herd 3 Active Links
y_label_line=dfs_e[0].columns[42] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of active Links in Fourth herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################herd 0 Congested Links
y_label_line=dfs_e[0].columns[10] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of congested Links in First herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################herd 1 Congested Links
y_label_line=dfs_e[0].columns[21] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of congested Links in Second herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################herd 2 Congested Links
y_label_line=dfs_e[0].columns[32] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of congested Links in Third herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################herd 3 Congested Links
y_label_line=dfs_e[0].columns[43] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
plt.axvline(x=x1, color='r', linestyle='--', label="Start Elephants")
plt.axvline(x=x2, color='g', linestyle='--', label="Stop sending Elephants")
plt.axvline(x=x3, color='purple', linestyle='--', label="Elephants transmission ended")

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of congested Links in Fourth herd")
plt.title(f"{y_label_line} over time")
plt.grid(True)
plt.legend(loc='upper right', fontsize=8, markerscale=0.8)

#Save figure
save_path=os.path.join(save_folder, f"{y_label_line}.png")
plt.savefig(save_path, dpi=300)
plt.close() #Close the figure to free memory

################################################################################################Core Mean Utilization 45
y_label_line=dfs_e[0].columns[45] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Max Utilization 46
y_label_line=dfs_e[0].columns[46] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Mean Occupation 47
y_label_line=dfs_e[0].columns[47] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Max Occupation 48
y_label_line=dfs_e[0].columns[48] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Mean Congestion 49
y_label_line=dfs_e[0].columns[49] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Max Congestion 50
y_label_line=dfs_e[0].columns[50] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Mean Drop Rate 51
y_label_line=dfs_e[0].columns[51] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Max Drop Rate 52
y_label_line=dfs_e[0].columns[52] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Active Links 53
y_label_line=dfs_e[0].columns[53] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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

################################################################################################Core Congested Links 54
y_label_line=dfs_e[0].columns[54] #Y axis label

sum_series_e=sum(df[y_label_line] for df in dfs_e)
mean_series_e=sum_series_e/20

sum_series_g=sum(df[y_label_line] for df in dfs_g)
mean_series_g=sum_series_g/20

sum_series_p=sum(df[y_label_line] for df in dfs_p)
mean_series_p=sum_series_p/20

plt.plot(x_enhanced, mean_series_e, marker='o', linestyle='-', label=f"Enhanced ECMP")
plt.plot(x_greedy, mean_series_g, marker='o', linestyle='-', label=f"Greedy")
plt.plot(x_prob, mean_series_p, marker='o', linestyle='-', label=f"Probabilistic")
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