#!/bin/bash

input=$1

echo "digraph \"model\" {"
echo "concentrate=true  node [fontname=\"sans-serif\"];"

# provided variables
cat $input | \
    grep "^itomsOf" | \
    sed -e "s/^itomsOf(//g" | \
    awk -F, '
{
    # $1 .. variable
    gsub(/ /, "", $1)
    printf "  \"%s\" [style=filled,fillcolor=lightgrey];\n",$1
    # all other fields are itoms - we dont display
}
'

# relations and edges
cat $input | \
    grep "^function" | \
    sed -e "s/^function(//g" -e "s/).$//g" -e "s/\[//g" -e "s/\]//g" | \
    awk -F, '
{
    # $1 .. output
    # $2 .. relation
    gsub(/ /, "", $1)
    gsub(/ /, "", $2)
    printf "  %s [shape=box];\n",$2
    # all other fields are the list elements of the 3rd parameter
    # = inputs of the function
    for(i = 3; i <= NF; i++) {
        # input to relation
        gsub(/ /, "", $i)
        printf "  %-10s -> %-10s;\n",$i,$2
    }
    # relation to output
    printf "  %-10s -> %-10s;\n",$2,$1
}
'

echo "}"
