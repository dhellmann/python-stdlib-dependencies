#!/bin/bash -x

python ./graph.py ensurepip > ensurepip-full.dot
dot -O -Tpng ensurepip-full.dot

python ./graph.py -s ensurepip > ensurepip-simplified.dot
dot -O -Tpng ensurepip-simplified.dot
