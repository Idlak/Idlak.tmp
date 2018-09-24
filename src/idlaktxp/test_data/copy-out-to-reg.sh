#!/bin/sh
for entry in `ls -a $1`
do
    if [[ $entry =~ .*out-to-reg.* ]]
    then
       echo "$entry not a test"
    elif [[ $entry =~ .*outv.* ]]
    then
       echo "cp $entry ${entry//outv/reg}"
       cp $entry ${entry//outv/reg}
    elif [[ $entry =~ .*out.* ]]
    then
       echo "cp $entry ${entry//out/reg}"
       cp $entry ${entry//out/reg}
    fi
done
