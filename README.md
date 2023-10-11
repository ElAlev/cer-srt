# Complex Event Recognition with Symbolic Register Transducers

This repository contains the code needed to reproduce the experiments found in the paper Complex Event Recognition with Symbolic Register Transducers.
The original source code has been obtained from [https://github.com/CORE-cer/CORE-experiments](https://github.com/CORE-cer/CORE-experiments).
It has been adapted appropriately so that the engines can run relational patterns.

# How to run

## Requirements

- Python >= 3.8
- Java >= 11

## Building the systems

Under the ```jars``` folder, you may find the executables used to run the experiments presented in the paper.
Under the ```sources``` folder, you may find the source code used to create the executables.
If you wish to modify the behavior of the engines, you may do so and then create a new fat jar.

## Running the experiments

The experiments scripts are located in the ```scripts``` folder. You may run each script with python. The results are stored under the ```results``` folder.
There are 7 scripts:
 - stock_reg.py: Runs experiments on the stock market dataset for sequential (relational) patterns.
 - stock_kleene.py: Runs experiments on the stock market dataset for (relational) patterns with Kleene operators.
 - stock_kleene_nested.py: Runs experiments on the stock market dataset for (relational) patterns with nested Kleene operators.
 - stock_other.py: Runs experiments on the stock market dataset for (relational) patterns with various operators.
 - smart_homes_reg.py: Runs experiments on the smart homes dataset for sequential (relational) patterns.
 - smart_homes_kleene.py: Runs experiments on the smart homes dataset for (relational) patterns with Kleene operators.
 - smart_homes_kleene_nested.py: Runs experiments on the smart homes dataset for (relational) patterns with nested Kleene operators.
 - taxis_reg.py: Runs experiments on the taxis dataset for sequential (relational) patterns.
 - taxis_kleene.py: Runs experiments on the taxis dataset for (relational) patterns with Kleene operators.
 - taxis_kleene_nested.py: Runs experiments on the taxis dataset for (relational) patterns with nested Kleene operators.

Before running a script, you need to set the ```WORKING_FOLDER``` variable inside the script. It should point to your local folder where you have downloaded the becnhmark suite.
You also need to unzip the ```streams.zip``` file and move the datasets to the appropriate folder (e.g., the ```taxi.stream``` file under the ```taxistream``` folder).
