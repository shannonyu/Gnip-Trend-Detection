#!/usr/bin/env python

import pickle
import sys
import argparse
import logging
import ConfigParser

import models
import time_bucket

def analyze(generator, model, logr):
    """
    This function loops over the items generated by the generator from the first argument.
    The expected format for each item is: [TimeBucket] [count]
    Each count is used to update the model, and the model result is added to the return list.
    """
    plotable_data = [] 
    for line in generator:
        time_bucket = line[0]
        count = line[1]
        model.update(count=count, time_bucket=time_bucket)
        plotable_data.append( (time_bucket, count, model.get_result()) )
        logr.debug("{0} {1:>8} {2:.2f}".format(time_bucket, str(count), model.get_result())) 
    return plotable_data

if __name__ == "__main__":
    
    logr = logging.getLogger("analyzer")
    if logr.handlers == []:
        fmtr = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s') 
        hndlr = logging.StreamHandler()
        hndlr.setFormatter(fmtr)
        logr.addHandler(hndlr) 

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",dest="input_file_name",default="output.pkl") 
    parser.add_argument("-d",dest="analyzed_data_file",default=None) 
    parser.add_argument("-c",dest="config_file_name",default=None,help="get configuration from this file")
    parser.add_argument("-v",dest="verbose",action="store_true",default=False)
    args = parser.parse_args()

    if args.config_file_name is not None:
        config = ConfigParser.SafeConfigParser()
        config.read(args.config_file_name)
        model_name = config.get("analyze","model_name")
        model_config = dict(config.items(model_name + "_model"))
    else:
        model_config = {"alpha":0.99,"mode":"lc","period_list":["hour"]}
        model_name = "Poisson"
    
    if args.verbose:
        logr.setLevel(logging.DEBUG)

    model = getattr(models,model_name)(config=model_config) 
    generator = pickle.load(open(args.input_file_name))
    plotable_data = analyze(generator,model,logr)
    if args.analyzed_data_file is not None:
        pickle.dump(plotable_data,open(args.analyzed_data_file,"w"))

