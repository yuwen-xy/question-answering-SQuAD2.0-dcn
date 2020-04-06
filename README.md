### Resuming training from saved state
* `python3 training_pipeline.py "/home/no_eating_no_drinking/model/2020-03-28_22-39-28/epoch0_batch11.par"`

### Generate scores for a model at different stages throughout its training:
* `python3 gen_scores.py <model_path> <dataset_file_path.json> [optional eval freq. measured in global steps]`
* Concrete example: `python3 gen_scores.py ./model/2020-04-07_00-10-37\[LR1-00e-03_Q86821_B64_H200_RS1\]/ preprocessing/data/subset-4/train-subset-4.json`
* The dataset file path needs to be `something.json` and have a corresponding `something-tokenized.json` for this script to work!
* Will generate a file `scores.log` in the model folder.

### Produce answer file for evaluation
* Generate predictions on **SQuAD dev set**: `python3 produce_answers.py model/2020-04-01_01-07-06/epoch0_batch791.par`
* Generate predictions on a different dataset: `python3 produce_answers.py model/2020-04-01_01-07-06/epoch0_batch791.par preprocessing/data/subset-1/train-subset-1-tokenized.json [optional_prediction_file_path]`
* Run evaluation: `python3 evaluate-v2.0.py  preprocessing/data/subset-1/train-subset-1.json predictions.json`

### Existing impl
* Model: https://github.com/atulkum/co-attention/blob/master/code/model.py
* Batcher: https://github.com/atulkum/co-attention/blob/master/code/data_util/data_batcher.py

### Links to our content
* GDrive: https://drive.google.com/open?id=17K0ZFb_OCdvHgSlkNFErzyx--eYZnoiG
* AML GDoc: https://docs.google.com/document/d/1fit7dYVHn0I0PsAA_HCj3AqnxJ7Wzz-78sb--wxKdA4/edit?usp=sharing
* Group Report: https://www.overleaf.com/4391458899tptsptshghhx

### TODOs
- [ ] ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) *Add your **past** contributions or **nearest-future work** here. (everyone)*
- [x] Move tests to seperate file (Richie)
- [x] Implement model (everyone)
- [x] Enable cuda usage (Kuba)
- [x] Get forward pass to run (Kuba)
- [x] Get backward pass to run (Kuba -- this was quick)
- [x] Debug why predicted end indices are all 0 (Richie)
- [x] Complete batching (Asmita)
- [x] Create word2id, id2word, embedding matrix (Asmita)
- [x] Training pipeline (Asmita + Kuba's minor cleanup)
- [x] Model serialisation (Kuba + Richie)
- [x] Debug `retain_graph` error (Dip)
- [x] Debug training issues (Dip with help from Kuba and Richie)
- [ ] Ablation tests:
  - [ ] single iteration for s/e indices instead of 4.
  - [ ] smaller HIDDEN_DIM
  - [ ] try removing some modules or replacing them with something simpler, e.g. coattention with some fully connected layers.
  - [ ] *Think of more ablation tests. Take ones from the paper.*
- [ ] Plots:
  - [x] Automate computation of F1/EM scores throughout a model's evolution (training). (Kuba)
  - [ ] Plotting F1/EM scores on top of loss
  - [ ] Prepare loss tables (discussed in the gdoc)
  - [ ] Plotting scores depending on true span length (Dip)
- [ ] Generate predictions for evaluation (TODO ~~batching if needed~~, better conversion from tokens to answer strings, ~~load serialised model~~) (Dip)

# Dynamic Coattention Networks For Question Answering

This repository contain a reimplementation of this paper https://arxiv.org/abs/1611.01604.

