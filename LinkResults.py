#!/usr/bin/python3

from fatTreeTopo import FatTree #custom class, where data center's topology (fat-tree) is defined through a topology object
import pandas as pd
import os
import ast

def analyze_link_stats():
    topo=FatTree(k=4, bw=[50, 50, 50], loss=[0, 0, 0], delay=['20ms', '20ms', '20ms'], jitter=['0ms', '0ms', '0ms'], max_queue=[50, 50, 50])
    assert isinstance(topo, FatTree), f"Expected instance of FatTree class, got {type(topo)} instead"

    #links_file="./DataFiles/LinkStatsBase.csv"
    #links_file="./DataFiles/LinkStatsEnhanced.csv"
    #links_file = "./DataFiles/LinkStatsGreedy.csv"
    links_file = "./DataFiles/LinkStatsProb.csv"
    links_df=pd.read_csv(links_file)

   #results_files=["./DataFiles/LinkStatsAggregateResultsBase.csv", "./DataFiles/LinkStatsPod0TrendsBase.csv",
    #               "./DataFiles/LinkStatsPod1TrendsBase.csv", "./DataFiles/LinkStatsPod2TrendsBase.csv",
    #                "./DataFiles/LinkStatsPod3TrendsBase.csv", "./DataFiles/LinkStatsCoreTrendsBase.csv"]
    #results_files=["./DataFiles/LinkStatsAggregateResultsEnhanced.csv", "./DataFiles/LinkStatsPod0TrendsEnhanced.csv",
    #              "./DataFiles/LinkStatsPod1TrendsEnhanced.csv", "./DataFiles/LinkStatsPod2TrendsEnhanced.csv",
    #               "./DataFiles/LinkStatsPod3TrendsEnhanced.csv", "./DataFiles/LinkStatsCoreTrendsEnhanced.csv"]
   #results_files = ["./DataFiles/LinkStatsAggregateResultsGreedy.csv", "./DataFiles/LinkStatsPod0TrendsGreedy.csv",
   #                 "./DataFiles/LinkStatsPod1TrendsGreedy.csv", "./DataFiles/LinkStatsPod2TrendsGreedy.csv",
   #                 "./DataFiles/LinkStatsPod3TrendsGreedy.csv", "./DataFiles/LinkStatsCoreTrendGreedy.csv"]
    results_files = ["./DataFiles/LinkStatsAggregateResultsProb.csv", "./DataFiles/LinkStatsPod0TrendsProb.csv",
                     "./DataFiles/LinkStatsPod1TrendsProb.csv", "./DataFiles/LinkStatsPod2TrendsProb.csv",
                     "./DataFiles/LinkStatsPod3TrendsProb.csv", "./DataFiles/LinkStatsCoreTrendsProb.csv"]

    for file in results_files:
        if os.path.isfile(file):
            os.remove(file) #delete the file

    tmp_df=links_df[links_df['query_count']==1]
    if tmp_df.duplicated(subset=["link_name"]).any(): #Ensure no duplicate link_name in tmp_df
        raise ValueError("Error in link stats, some links are seen multiple times")

    links=tmp_df['link_name']
    pod_links={} #dictionary containing links edge-agg, categorized per pod
    agg_core_links=[] #list of core level links

    for link in links:
        src, dst=link.split("-")
        if topo.get_layer(src)==FatTree.server_layer():
            continue
        elif topo.get_layer(src)==FatTree.edge_layer():
            if topo.get_pod_id(src) not in pod_links.keys():
                pod_links[topo.get_pod_id(src)]=[link]
            else:
                pod_links[topo.get_pod_id(src)].append(link)
        elif topo.get_layer(src)==FatTree.agg_layer():
            agg_core_links.append(link)
        else:
            raise ValueError("Error in link stats")

    last_query=links_df['query_count'].max()

    columns1=['query_count',
             'pod0_mean_utilization', 'pod0_max_utilization',
             'pod0_mean_occupation', 'pod0_max_occupation',
             'pod0_mean_congestion', 'pod0_max_congestion',
             'pod0_mean_drop_rate', 'pod0_max_drop_rate',
             'pod0_active_links', 'pod0_congested_links', 'pod0_idle_links',

              'pod1_mean_utilization', 'pod1_max_utilization',
              'pod1_mean_occupation', 'pod1_max_occupation',
              'pod1_mean_congestion', 'pod1_max_congestion',
              'pod1_mean_drop_rate', 'pod1_max_drop_rate',
              'pod1_active_links', 'pod1_congested_links', 'pod1_idle_links',

              'pod2_mean_utilization', 'pod2_max_utilization',
              'pod2_mean_occupation', 'pod2_max_occupation',
              'pod2_mean_congestion', 'pod2_max_congestion',
              'pod2_mean_drop_rate', 'pod2_max_drop_rate',
              'pod2_active_links', 'pod2_congested_links', 'pod2_idle_links',

              'pod3_mean_utilization', 'pod3_max_utilization',
              'pod3_mean_occupation', 'pod3_max_occupation',
              'pod3_mean_congestion', 'pod3_max_congestion',
              'pod3_mean_drop_rate', 'pod3_max_drop_rate',
              'pod3_active_links', 'pod3_congested_links', 'pod3_idle_links',

              'agg_core_mean_utilization', 'agg_core_max_utilization',
              'agg_core_mean_occupation', 'agg_core_max_occupation',
              'agg_core_mean_congestion', 'agg_core_max_congestion',
              'agg_core_mean_drop_rate', 'agg_core_max_drop_rate',
              'agg_core_active_links', 'agg_core_congested_links', 'agg_core_idle_links',]

    columns_pod={}
    for pod in pod_links:
        columns_pod[pod]=['query_count']
        for link in pod_links[pod]:
            columns_pod[pod].append(f'{link}_utilization')
            columns_pod[pod].append(f'{link}_occupation')
            columns_pod[pod].append(f'{link}_congestion')
            columns_pod[pod].append(f'{link}_drop_rate')

    columns_core=['query_count']
    for link in agg_core_links:
        columns_core.append(f'{link}_utilization')
        columns_core.append(f'{link}_occupation')
        columns_core.append(f'{link}_congestion')
        columns_core.append(f'{link}_drop_rate')

    link_results_df=pd.DataFrame(columns=columns1)
    pod0_trends_df=pd.DataFrame(columns=columns_pod[0])
    pod1_trends_df=pd.DataFrame(columns=columns_pod[1])
    pod2_trends_df=pd.DataFrame(columns=columns_pod[2])
    pod3_trends_df=pd.DataFrame(columns=columns_pod[3])
    core_trends_df=pd.DataFrame(columns=columns_core)

    for i in range(1, last_query+1):

        tmp_df=links_df[links_df['query_count']==i]

        pod0_df=tmp_df[tmp_df['link_name'].isin(pod_links[0])]
        pod1_df=tmp_df[tmp_df['link_name'].isin(pod_links[1])]
        pod2_df=tmp_df[tmp_df['link_name'].isin(pod_links[2])]
        pod3_df=tmp_df[tmp_df['link_name'].isin(pod_links[3])]

        agg_core_df=tmp_df[tmp_df['link_name'].isin(agg_core_links)]

        dropped_packets0=pod0_df['dropped_packets'].apply(sum_dropped)
        dropped_packets1=pod1_df['dropped_packets'].apply(sum_dropped)
        dropped_packets2=pod2_df['dropped_packets'].apply(sum_dropped)
        dropped_packets3=pod3_df['dropped_packets'].apply(sum_dropped)
        dropped_packets_core=agg_core_df['dropped_packets'].apply(sum_dropped)

        drop_rates_0=dropped_packets0/(pod0_df['tx_packets']+pod0_df['rx_packets'])
        drop_rates_1=dropped_packets1/(pod1_df['tx_packets']+pod1_df['rx_packets'])
        drop_rates_2=dropped_packets2/(pod2_df['tx_packets']+pod2_df['rx_packets'])
        drop_rates_3=dropped_packets3/(pod3_df['tx_packets']+pod3_df['rx_packets'])

        drop_rates_core=dropped_packets_core/(agg_core_df['tx_packets']+agg_core_df['rx_packets'])

        congested_pod0=len(pod0_df[pod0_df['congestion']>=0.7])
        idle_pod0=len(pod0_df[pod0_df['congestion']<=0.1])

        congested_pod1 = len(pod1_df[pod1_df['congestion']>=0.7])
        idle_pod1 = len(pod1_df[pod1_df['congestion']<=0.1])

        congested_pod2 = len(pod2_df[pod2_df['congestion']>=0.7])
        idle_pod2 = len(pod2_df[pod2_df['congestion']<=0.1])

        congested_pod3 = len(pod3_df[pod3_df['congestion']>=0.7])
        idle_pod3 = len(pod3_df[pod3_df['congestion']<=0.1])

        congested_agg_core=len(agg_core_df[agg_core_df['congestion']>=0.7])
        idle_agg_core=len(agg_core_df[agg_core_df['congestion']<=0.1])

        new_row=pd.DataFrame([{'query_count': i,
                               'pod0_mean_utilization': pod0_df['utilization'].mean(),
                               'pod0_max_utilization': pod0_df['utilization'].max(),
                               'pod0_mean_occupation': pod0_df['occupation'].mean(),
                               'pod0_max_occupation': pod0_df['occupation'].max(),
                               'pod0_mean_congestion': pod0_df['congestion'].mean(),
                               'pod0_max_congestion': pod0_df['congestion'].max(),
                               'pod0_mean_drop_rate': drop_rates_0.mean(),
                               'pod0_max_drop_rate': drop_rates_0.max(),
                               'pod0_active_links': len(pod0_df),
                               'pod0_congested_links': congested_pod0,
                               'pod0_idle_links': idle_pod0,

                               'pod1_mean_utilization': pod1_df['utilization'].mean(),
                               'pod1_max_utilization': pod1_df['utilization'].max(),
                               'pod1_mean_occupation': pod1_df['occupation'].mean(),
                               'pod1_max_occupation': pod1_df['occupation'].max(),
                               'pod1_mean_congestion': pod1_df['congestion'].mean(),
                               'pod1_max_congestion': pod1_df['congestion'].max(),
                               'pod1_mean_drop_rate': drop_rates_1.mean(),
                               'pod1_max_drop_rate': drop_rates_1.max(),
                               'pod1_active_links': len(pod1_df),
                               'pod1_congested_links': congested_pod1,
                               'pod1_idle_links': idle_pod1,

                               'pod2_mean_utilization': pod2_df['utilization'].mean(),
                               'pod2_max_utilization': pod2_df['utilization'].max(),
                               'pod2_mean_occupation': pod2_df['occupation'].mean(),
                               'pod2_max_occupation': pod2_df['occupation'].max(),
                               'pod2_mean_congestion': pod2_df['congestion'].mean(),
                               'pod2_max_congestion': pod2_df['congestion'].max(),
                               'pod2_mean_drop_rate': drop_rates_2.mean(),
                               'pod2_max_drop_rate': drop_rates_2.max(),
                               'pod2_active_links': len(pod2_df),
                               'pod2_congested_links': congested_pod2,
                               'pod2_idle_links': idle_pod2,

                               'pod3_mean_utilization': pod3_df['utilization'].mean(),
                               'pod3_max_utilization': pod3_df['utilization'].max(),
                               'pod3_mean_occupation': pod3_df['occupation'].mean(),
                               'pod3_max_occupation': pod3_df['occupation'].max(),
                               'pod3_mean_congestion': pod3_df['congestion'].mean(),
                               'pod3_max_congestion': pod3_df['congestion'].max(),
                               'pod3_mean_drop_rate': drop_rates_3.mean(),
                               'pod3_max_drop_rate': drop_rates_3.max(),
                               'pod3_active_links': len(pod3_df),
                               'pod3_congested_links': congested_pod3,
                               'pod3_idle_links': idle_pod3,

                               'agg_core_mean_utilization': agg_core_df['utilization'].mean(),
                               'agg_core_max_utilization': agg_core_df['utilization'].max(),
                               'agg_core_mean_occupation': agg_core_df['occupation'].mean(),
                               'agg_core_max_occupation': agg_core_df['occupation'].max(),
                               'agg_core_mean_congestion': agg_core_df['congestion'].mean(),
                               'agg_core_max_congestion': agg_core_df['congestion'].max(),
                               'agg_core_mean_drop_rate': drop_rates_core.mean(),
                               'agg_core_max_drop_rate': drop_rates_core.max(),
                               'agg_core_active_links': len(agg_core_df),
                               'agg_core_congested_links': congested_agg_core,
                               'agg_core_idle_links': idle_agg_core}])

        dict_0={'query_count': i}
        dict_1={'query_count': i}
        dict_2={'query_count': i}
        dict_3={'query_count': i}
        dict_core={'query_count': i}

        for index, row in pod0_df.iterrows():
            dict_0[f"{row['link_name']}_utilization"]=row['utilization']
            dict_0[f"{row['link_name']}_occupation"]=row['occupation']
            dict_0[f"{row['link_name']}_congestion"]=row['congestion']

            dropped_packets=sum_dropped(row['dropped_packets'])
            drop_rate=dropped_packets/(row['tx_packets']+row['rx_packets'])
            dict_0[f"{row['link_name']}_drop_rate"]=drop_rate

        for index, row in pod1_df.iterrows():
            dict_1[f"{row['link_name']}_utilization"]=row['utilization']
            dict_1[f"{row['link_name']}_occupation"]=row['occupation']
            dict_1[f"{row['link_name']}_congestion"] = row['congestion']

            dropped_packets=sum_dropped(row['dropped_packets'])
            drop_rate=dropped_packets/(row['tx_packets']+row['rx_packets'])
            dict_1[f"{row['link_name']}_drop_rate"]=drop_rate

        for index, row in pod2_df.iterrows():
            dict_2[f"{row['link_name']}_utilization"]=row['utilization']
            dict_2[f"{row['link_name']}_occupation"]=row['occupation']
            dict_2[f"{row['link_name']}_congestion"] = row['congestion']

            dropped_packets=sum_dropped(row['dropped_packets'])
            drop_rate=dropped_packets/(row['tx_packets']+row['rx_packets'])
            dict_2[f"{row['link_name']}_drop_rate"]=drop_rate

        for index, row in pod3_df.iterrows():
            dict_3[f"{row['link_name']}_utilization"]=row['utilization']
            dict_3[f"{row['link_name']}_occupation"]=row['occupation']
            dict_3[f"{row['link_name']}_congestion"] = row['congestion']

            dropped_packets=sum_dropped(row['dropped_packets'])
            drop_rate=dropped_packets/(row['tx_packets']+row['rx_packets'])
            dict_3[f"{row['link_name']}_drop_rate"]=drop_rate

        for index, row in agg_core_df.iterrows():
            dict_core[f"{row['link_name']}_utilization"]=row['utilization']
            dict_core[f"{row['link_name']}_occupation"]=row['occupation']
            dict_core[f"{row['link_name']}_congestion"] = row['congestion']

            dropped_packets=sum_dropped(row['dropped_packets'])
            drop_rate=dropped_packets/(row['tx_packets']+row['rx_packets'])
            dict_core[f"{row['link_name']}_drop_rate"]=drop_rate

        link_results_df=pd.concat([link_results_df, new_row], ignore_index=True) #add new row to dataframe
        pod0_trends_df=pd.concat([pod0_trends_df,pd.DataFrame([dict_0])], ignore_index=True)
        pod1_trends_df = pd.concat([pod1_trends_df,pd.DataFrame([dict_1])], ignore_index=True)
        pod2_trends_df = pd.concat([pod2_trends_df,pd.DataFrame([dict_2])], ignore_index=True)
        pod3_trends_df = pd.concat([pod3_trends_df,pd.DataFrame([dict_3])], ignore_index=True)
        core_trends_df = pd.concat([core_trends_df,pd.DataFrame([dict_core])], ignore_index=True)

    file_exists=os.path.isfile(results_files[0]) #checks if the file exists
    link_results_df.to_csv(results_files[0], mode='a', index=False, header=not file_exists) #append to file if it exists, otherwise create a new file

    file_exists=os.path.isfile(results_files[1]) #checks if the file exists
    pod0_trends_df.to_csv(results_files[1], mode='a', index=False, header=not file_exists)

    file_exists = os.path.isfile(results_files[2])  # checks if the file exists
    pod1_trends_df.to_csv(results_files[2], mode='a', index=False, header=not file_exists)

    file_exists = os.path.isfile(results_files[3])  # checks if the file exists
    pod2_trends_df.to_csv(results_files[3], mode='a', index=False, header=not file_exists)

    file_exists = os.path.isfile(results_files[4])  # checks if the file exists
    pod3_trends_df.to_csv(results_files[4], mode='a', index=False, header=not file_exists)

    file_exists = os.path.isfile(results_files[5])  # checks if the file exists
    core_trends_df.to_csv(results_files[5], mode='a', index=False, header=not file_exists)

def sum_dropped(row_field):
    array=ast.literal_eval(row_field)
    return sum(array)

if __name__ == '__main__':
    analyze_link_stats()