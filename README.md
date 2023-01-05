# QuISPR: QuISP Runner

## Prerequisites
* Poetry

## Getting Started
```sh
# install dependencies
$ poetry install

# activate virtual env 
# (if you don't want to make your environment dirty)
$ poetry shell

# install quispr command in editable mode
$ pip install -e .

# then you can use the "quispr" command
# show help
$ quispr --help
```
## Usage
```sh
# validate your plan file 
$ quispr plan ./simulation.plan

# run all simulations
$ quispr run ./simulation.plan -r ../your-quisp-repository -o ../output-dir

# run simulations with 16 workers
$ quispr run ./simulation.plan -r ../your-quisp-repository -o ../output-dir -p 16

# run all simulations in a ini file
$ quispr run ../quisp/quisp/simulations/test.ini

# and you can type Ctrl-C to stop the simulations

# then you can resume the stopped simulation
$ quispr resume

# you can check the stopped simulations status
$ quispr status
```

## Results Directory
```
results/{TIMESTAMP}-{TITLE}
├── results          // dir for the simulation outputs
├── ned              // dir for all copied ned files
├── topology         // dir basic network topology definitions
├── analysis.ipynb   // jupyter notebook for instant analysis
├── commit.txt       // git commit hash and name for the quisp repo
├── omnetpp.ini      // generated ini by plan
├── quisp_bin        // quisp executable
├── results.pickle   // all results as dict
└── simulation.plan  // the plan file

```
