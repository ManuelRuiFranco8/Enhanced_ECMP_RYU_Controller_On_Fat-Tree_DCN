#!/usr/bin/python3

import pandas as pd
from datetime import datetime as dt #to measure time
import os

#flows_file="./DataFiles/FlowStatsSendEnhanced.csv"
#flows_file="./DataFiles/FlowStatsSendGreedy.csv"
flows_file="./DataFiles/FlowStatsSendProb.csv"
send_df=pd.read_csv(flows_file)
if send_df.duplicated(subset=["flow_name"]).any(): #Ensure no duplicate flow_name in send_df
    raise ValueError("Duplicate flow_name values found in FlowStatsSend.csv")

send_df=send_df[send_df['flow_size']>=100] #filter in only elephant flows
n_send_elephants=len(send_df)

#elephant_file="./DataFiles/DetectedElephants.csv"
#elephant_file="./DataFiles/DetectedGreedy.csv"
elephant_file="./DataFiles/DetectedProb.csv"
elephant_df=pd.read_csv(elephant_file)
if elephant_df.duplicated(subset=["flow_name"]).any(): #Ensure no duplicate flow_name in elephant_df
    raise ValueError("Duplicate flow_name values found in DetectedElephants.csv")

#results_file="./DataFiles/ElephantsDetection.txt"
#results_file="./DataFiles/ElephantsDetectionGreedy.txt"
results_file="./DataFiles/ElephantsDetectionProb.txt"
if os.path.isfile(results_file):
    os.remove(results_file) #delete the file

false_negative=0
for index, row in send_df.iterrows():
    flow_name=row['flow_name']
    src=row['source']
    dst=row['destination']
    level4=row['L4']
    start_time=row['start_time']

    if flow_name in elephant_df['flow_name'].values:
        with open(results_file, "a") as log_file:
            log_file.write(f"{dt.now()} -> Detected elephant flow {flow_name} ({level4}) between {src} and {dst}, started at {start_time}\n")
            log_file.write(f"\n")
    else:
        false_negative+=1
        with open(results_file, "a") as log_file:
            log_file.write(f"{dt.now()} -> Elephant flow {flow_name} ({level4}) between {src} and {dst}, started at {start_time}, was not detected\n")
            log_file.write(f"\n")

n_detected_elephants=n_send_elephants-false_negative #true positives
false_positive=0
for index, row in elephant_df.iterrows():
    flow_name=row['flow_name']

    if flow_name not in send_df['flow_name'].values:
        false_positive+=1
        with open(results_file, "a") as log_file:
            log_file.write(f"{dt.now()} -> Flow {flow_name} wrongly classified as elephant\n")
            log_file.write(f"\n")

precision=n_detected_elephants/(n_detected_elephants+false_positive)
recall=n_detected_elephants/(n_detected_elephants+false_negative)

with open(results_file, "a") as log_file:
    log_file.write(f"{dt.now()} -> Number of transmitted elephant flows: {n_send_elephants}.\n")
    log_file.write(f"{dt.now()} -> True positives (correctly detected elephants): {n_detected_elephants}.\n")
    log_file.write(f"{dt.now()} -> False positives (wrongly detected elephants): {false_positive}. Precision = {precision}\n")
    log_file.write(f"{dt.now()} -> False negatives (undetected elephants): {false_negative}. Recall = {recall}\n")
    log_file.write(f"\n")