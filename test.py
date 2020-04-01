import argparse
from typing import Any, Union, Dict, Iterable, List, Optional, Tuple

from allennlp.models.archival import load_archive
from allennlp.predictors import Predictor

from models import KnowledgeEnhancedSlotTaggingModel
from predictors import SlotFillingPredictor
from dataset_readers import MultiFileDatasetReader
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer, PretrainedBertIndexer

from allennlp.data import vocabulary
vocabulary.DEFAULT_OOV_TOKEN = "[UNK]"  # set for bert


def main(args):
    archive = load_archive(args.output_dir)
    predictor = Predictor.from_archive(archive=archive, predictor_name="bert_st")

    while True:
        try:
            sentence = input(">>> ")
            if not sentence.strip():
                continue
            output_dict = predictor.predict({"sentence": sentence.strip()})
            print(f"\t\t\t{' '.join(output_dict['tokens'])}")
            print(f"\t\t\t{' '.join(output_dict['predict_labels'])}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--output_dir", type=str, default="./output/bert-large-atis/",
                            help="the directory that stores training output")
    args = arg_parser.parse_args()
    main(args)