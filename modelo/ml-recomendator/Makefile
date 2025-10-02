.PHONY: data label split train-rf train-nn eval-rf eval-nn plots all

RAW_WHO= data/raw/who
RAW_SUR= data/raw/surveys
INT= data/interim
PROC= data/processed
MODELS= models
FIG= reports/figures
MET= reports/metrics

ensure-dirs:
	@mkdir -p $(INT) $(PROC) $(MODELS) $(FIG) $(MET)

label: ensure-dirs
	python -m src.pipeline.label_dataset --in $(RAW_SUR) --who $(RAW_WHO) --out $(INT)/children_labeled.csv

split: ensure-dirs
	python -m src.pipeline.split_dataset --in $(INT)/children_labeled.csv --train $(PROC)/train.csv --test $(PROC)/test.csv

train-rf: ensure-dirs
	python -m src.models.train_rf --config configs/rf.yaml --train $(PROC)/train.csv --out $(MODELS)/rf.pkl --pre $(MODELS)/preprocess.joblib --metrics $(MET)/rf_metrics.json

train-nn: ensure-dirs
	python -m src.models.train_nn --config configs/nn.yaml --train $(PROC)/train.csv --out $(MODELS)/nn.pkl --pre $(MODELS)/preprocess.joblib --metrics $(MET)/nn_metrics.json

eval-rf:
	python -m src.models.evaluate_rf --config configs/rf.yaml --test $(PROC)/test.csv --model $(MODELS)/rf.pkl --pre $(MODELS)/preprocess.joblib --metrics $(MET)/rf_eval.json

eval-nn:
	python -m src.models.evaluate_nn --config configs/nn.yaml --test $(PROC)/test.csv --model $(MODELS)/nn.pkl --pre $(MODELS)/preprocess.joblib --metrics $(MET)/nn_eval.json

plots:
	python -m src.visualization.plots_rf --test $(PROC)/test.csv --model $(MODELS)/rf.pkl --pre $(MODELS)/preprocess.joblib --out $(FIG)
	python -m src.visualization.plots_nn --test $(PROC)/test.csv --model $(MODELS)/nn.pkl --pre $(MODELS)/preprocess.joblib --out $(FIG)

all: label split train-rf train-nn eval-rf eval-nn plots
