#!/bin/bash

if [ -f "./import_graph.dot" ]; then
    mv ./import_graph.dot ../data
fi

cp -r ./mathlib4 ../data

tail -f /dev/null