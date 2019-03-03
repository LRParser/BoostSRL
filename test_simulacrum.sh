#! /bin/bash

java -cp code/target/BoostSRL-1.0-SNAPSHOT.jar edu.wisc.cs.will.Boosting.RDN.RunBoostedRDN -l -train ~/Downloads/simulacrum/train -target diedofcancer > train.log 

java -cp code/target/BoostSRL-1.0-SNAPSHOT.jar edu.wisc.cs.will.Boosting.RDN.RunBoostedRDN -i -model ~/Downloads/simulacrum/train/models -test ~/Downloads/simulacrum/test -target diedofcancer -aucJarPath . > test.log
