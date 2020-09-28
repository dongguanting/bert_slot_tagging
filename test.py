import os
import tqdm
import argparse
import collections
from typing import Any, Union, Dict, Iterable, List, Optional, Tuple

from allennlp.models.archival import load_archive
from allennlp.predictors import Predictor

from models import BertSlotTagging
from predictors import SlotFillingPredictor
from dataset_readers import MultiFileDatasetReader, parse_ann, parse_seq_out
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer, PretrainedBertIndexer

from allennlp.data import vocabulary
vocabulary.DEFAULT_OOV_TOKEN = "[UNK]"  # set for bert


def main(args):
    archives = [load_archive(output_dir, cuda_device=1) for output_dir in args.output_dir]
    predictors = [Predictor.from_archive(archive=archive, predictor_name="bert_st") for archive in archives]

    for filename in tqdm.tqdm([item for item in os.listdir(args.test_data_dir) if item[-4:] == ".txt"]):
        one_sample_set = collections.defaultdict(int)
        sample_id = filename[:-4]
        for item in parse_ann(os.path.join(args.test_data_dir, filename)):
            for predictor in predictors:
                output_dict = predictor.predict({"sentence": item["sentence"], "sample_id": int(sample_id), "start": item["start"], "end": item["end"]})
                predicted_tags = output_dict["predict_labels"]
                for start_idx, end_idx, label in parse_seq_out(predicted_tags):
                    one_sample_set[(item["start"] + start_idx, item["start"] + end_idx + 1, label, item["sentence"][start_idx:end_idx+1])] += 1
        
        
        with open(os.path.join(args.test_data_dir, f"{sample_id}.ann"), "w") as f:
            idx = 0
            for (start, end, label, value), count in one_sample_set.items():
                if count >= args.ensemble_threshold:
                    f.write(f"T{idx+1}\t{label} {start} {end}\t{value}\n")
                    idx += 1


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--output_dir", type=str, nargs="+", required=True,
                            help="the directory that stores training output")
    arg_parser.add_argument("--test_data_dir", type=str, default="./data/tianchi/chusai_xuanshou")
    arg_parser.add_argument("--ensemble_threshold", type=int, default=1)
    args = arg_parser.parse_args()
    main(args)