Big Data and Machine Learning Final Project
===========================================

Graham Jones and Neeraj Kanuri

## Overview

This repository contains a duplication of the work found in [this paper](https://dl.acm.org/doi/10.1145/3306309.3306339)
## Instructions

Run a sample simulation by running `python3 drone_scheduling.py eval7.txt`

To profile the code run the following:

- `python3 -m cProfile -o log.profile drone_scheduling.py eval7.txt LLV`

- `gprof2dot -f pstats log.profile -o graph.dot`

- `dot -Tpng graph.dot > output.png`

- `open output.png`
