## Non-Local Covington
This repository includes the code of the Non-Local Covington parser described in NAACL paper [Non-Projective Dependency Parsing with Non-Local Transitions](https://arxiv.org/pdf/1710.09340.pdf). The implementation is based on the Arc-Swift project (https://github.com/qipeng/arc-swift) and reuse part of its code, including data preparation and evaluating scripts.

This implementation requires Tensorflow 1.0 or above, and other Python dependencies are included in `requirements.txt`, which can be installed via `pip` by running:

```
pip install -r requirements.txt
```

### Data preparation
First, we need to create for the training data a file that maps all dependency arc types and all part-of-speech (POS) types into integers. This can be achieved by running the following script under `utils/`

```
./create_mappings.sh <train data> > ../src/mappings.txt
```

We also need to create the oracle sequence of transitions for training our parser. To do this, go to `src/`, and run

```
python gen_oracle_seq.py <train data> train.NCov.seq --transsys NCov --mappings mappings.txt
```

Where `mappings.txt` is the mappings file we just created, `NCov` stands for _Non-Local Covington_, and `train.NCov.seq` is the output file containing oracle transitions for the training data.

You also need to download the pretrained [GloVe vectors] from https://nlp.stanford.edu/projects/glove/.

See https://github.com/qipeng/arc-swift for a more detailed description of data preparation.

### Training

To train the Non-Local Covington parser, simply run:

```
mkdir NCov_models
python train_parser.py <train data> --seq_file train.NCov.seq --wordvec_file glove.6B.100d.txt --vocab_file vocab.pickle --feat_file NCov_feats.pickle --model_dir NCov_models --transsys NCov --mappings_file mappings.txt
```

### Test and evaluation

To evaluate the trained parser, run:

```
python eval_parser.py <dev data> --vocab_file vocab.pickle --model_dir NCov_models --transsys NCov --eval_dataset dev --mappings_file mappings.txt
```

This will generate output files in the model directory with names like `models_NCov/dev_eval_beam_1_output_epoch0.txt`, which contain the predicted dependency parses.

A python implementation of labelled and unlabelled attachment score evaluation is also provided. Just run:

```
cut -d"	" -f1-6 ptb3-wsj-dev.conllx| paste - NCov_models/dev_eval_beam_1_output_epoch0.txt > system_pred.conllx
python eval.py -g <dev data> -s system_pred.conllx
```
By default the script removes punctuation according to the gold Penn Treebank POS tags of the tokens. Use `--language conll` to generate results compatible with the CoNLL official evaluation script. 

## License

All work contained in this package is licensed under the Apache License, Version 2.0. See the included LICENSE file.
