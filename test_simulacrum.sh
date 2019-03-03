#! /bin/bash

java -cp code/target/BoostSRL-1.0-SNAPSHOT.jar edu.wisc.cs.will.Boosting.RDN.RunBoostedRDN -l -train ~/Downloads/simulacrum/train -trees 10 -target diedofcancer >> train.log 

java -cp code/target/BoostSRL-1.0-SNAPSHOT.jar edu.wisc.cs.will.Boosting.RDN.RunBoostedRDN -i -model ~/Downloads/simulacrum/train/models -trees 10 -test ~/Downloads/simulacrum/test -target diedofcancer -aucJarPath . >> test.log
