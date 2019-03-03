import pandas as pd
import re

# Randomly shuffle all the patients
df = pd.read_csv("sim_av_patient.csv").sample(frac=1).reset_index(drop=True)

tumour = pd.read_csv("sim_av_tumour.csv")
tumour["AGE"] = pd.cut(tumour["AGE"],10,labels=[str(i) for i in range(10)])

sact_tumour = pd.read_csv("sim_sact_tumour.csv")
sact_patient = pd.read_csv("sim_sact_patient.csv")
sact_tumour = pd.read_csv("sim_sact_tumour.csv")


sact_regimen = pd.read_csv("sim_sact_regimen.csv",encoding="latin1")
sact_cycle = pd.read_csv("sim_sact_cycle.csv")
sact_drug_detail = pd.read_csv("sim_sact_drug_detail.csv")
sact_outcome = pd.read_csv("sim_sact_outcome.csv")

num_pos = 0
num_neg = 0
num_exs = 5000
pat_cols = None
tum_cols = None

mtum_cols = None
mreg_cols = None
mout_cols = None


with open("train/train_facts.txt","w") as facts:
    with open("train/train_pos.txt","w") as f_pos:
        with open("train/train_neg.txt","w") as f_neg:

            for idx, row in df.iterrows():

                label = str(row["DEATHCAUSECODE_UNDERLYING"])
                if "C18" in label:
                    label = "1"
                    out = f_pos
                    num_pos = num_pos + 1

                else:
                    label = "0"
                    out = f_neg
                    num_neg = num_neg + 1
                patid = row["PATIENTID"]
                linknum = row["LINKNUMBER"]
                if label == "1" and num_pos < num_exs or label == "0" and num_neg < num_exs:
                    out.write("diedofcancer"+"(id"+str(patid)+").\n")
                    pat_cols = [x for x in df.columns.values if x not in ["PATIENTID","LINKNUMBER"] and "VITAL" not in x and "DEATH" not in x]
                    for col in pat_cols:
                        val = re.sub(r'\W+', 'AN', str(row[col]))
                        facts.write(col.lower() + "(id" + str(patid) + "," + val + ").\n")

                    tumours = tumour[tumour["PATIENTID"] == patid]
                    for idx, trow in tumours.iterrows():
                        tid = trow["TUMOURID"]
                        facts.write("has_tumour(id" + str(patid) + "," + "tumourid"+str(tid)+ ").\n")
                        tum_cols = [x for x in tumours.columns.values if x not in ["PATIENTID", "TUMOURID","LINKNUMBER"] and x not in pat_cols and "DATE" not in x]

                        for col in tum_cols:
                            val = re.sub(r'\W+', 'AN', str(trow[col]))
                            facts.write(col.lower() + "(tumourid" + str(tid) + "," + val + ").\n")

                    rel_pats = sact_patient[sact_patient["LINK_NUMBER"] == linknum].reset_index()
                    if len(rel_pats > 0):
                        merged_id = rel_pats.iloc[0]["MERGED_PATIENT_ID"]

                        sact_tumours = sact_tumour[sact_tumour["MERGED_PATIENT_ID"] == merged_id]

                        for idx, mtrow in sact_tumours.iterrows():
                            mtid = mtrow["MERGED_TUMOUR_ID"]
                            facts.write("has_mergedtumour(id" + str(patid) + "," + "mergedtumourid"+str(mtid)+ ").\n")
                            mtum_cols = [x for x in sact_tumours.columns.values if x not in ["MERGED_TUMOUR_ID", "MERGED_PATIENT_ID"] and x not in pat_cols and x not in tum_cols and "DATE" not in x]

                            for col in mtum_cols:
                                val = re.sub(r'\W+', 'AN', str(mtrow[col]))

                                facts.write(col.lower() + "(mergedtumourid" + str(mtid) + "," + val + ").\n")

                            # Facts for Regimen
                            sact_regimens = sact_regimen[sact_regimen["MERGED_TUMOUR_ID"] == mtid]
                            for idx, mrrow in sact_regimens.iterrows():
                                mrid = mrrow["MERGED_REGIMEN_ID"]
                                facts.write(
                                    "has_mergedregimen(mergedtumourid" + str(mtid) + "," + "mergedregimenid" + str(mrid) + ").\n")
                                mreg_cols = [x for x in sact_regimens.columns.values if x not in ["MERGED_TUMOUR_ID", "MERGED_REGIMEN_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and "DATE" not in x]

                                for col in mreg_cols:
                                    val = re.sub(r'\W+', 'AN', str(mrrow[col]))

                                    facts.write(col.lower() + "(mergedregimenid" + str(mrid) + "," + \
                                                val + ").\n")


                                sact_cycles = sact_cycle[sact_cycle["MERGED_REGIMEN_ID"] == mrid]
                                for idx, mcrow in sact_cycles.iterrows():
                                    mcid = mcrow["MERGED_CYCLE_ID"]
                                    facts.write(
                                        "has_mergedcycle(mergedregimenid" + str(mrid) + "," + "mergedcycleid" + str(
                                            mcid) + ").\n")
                                    mcyc_cols = [x for x in sact_cycles.columns.values if
                                                 x not in ["MERGED_TUMOUR_ID", "MERGED_CYCLE_ID"
                                                           "MERGED_REGIMEN_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and x not in mreg_cols and "DATE" not in x]
                                    for col in mcyc_cols:
                                        val = re.sub(r'\W+', 'AN', str(mcrow[col]))

                                        facts.write(col.lower() + "(mergedcycleid" + str(mcid) + "," + \
                                                    val + ").\n")

                                    sact_drug_details = sact_drug_detail[sact_drug_detail["MERGED_CYCLE_ID"] == mcid]
                                    for idx, mdrow in sact_drug_details.iterrows():
                                        mddid = mdrow["MERGED_DRUG_DETAIL_ID"]
                                        facts.write(
                                            "has_mergeddrugdetail(mergedcycleid" + str(mcid) + "," + "mergeddrugdetailid" + str(
                                                mddid) + ").\n")
                                        mdd_cols = [x for x in sact_drug_details.columns.values if
                                                     x not in ["MERGED_TUMOUR_ID", "MERGED_CYCLE_ID", "MERGED_DRUG_DETAIL_ID",
                                                                                   "MERGED_REGIMEN_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and x not in mreg_cols and "DATE" not in x]
                                        for col in mdd_cols:
                                            val = re.sub(r'\W+', 'AN', str(mdrow[col]))

                                            facts.write(col.lower() + "(mergeddrugdetailid" + str(mddid) + "," + \
                                                        val + ").\n")


                                sact_outcomes = sact_outcome[sact_outcome["MERGED_REGIMEN_ID"] == mrid]
                                for idx, orow in sact_outcomes.iterrows():
                                    oid = orow["MERGED_OUTCOME_ID"]
                                    facts.write(
                                        "has_mergedoutcome(mergedregimenid" + str(mrid) + "," + "mergedoutcomeid" + str(oid) + ").\n")
                                    mout_cols = [x for x in sact_outcomes.columns.values if x not in ["MERGED_TUMOUR_ID",
                                                                                                      "MERGED_REGIMEN_ID","MERGED_OUTCOME_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and x not in mreg_cols and "DATE" not in x]

                                    for col in mout_cols:
                                        val = re.sub(r'\W+', 'AN', str(orow[col]))

                                        facts.write(
                                            col.lower() + "(mergedoutcomeid" + str(oid) + "," + \
                                            val + ").\n")

                if num_pos >= num_exs and num_neg >= num_exs:
                    break

num_pos = 0
num_neg = 0

with open("test/test_facts.txt","w") as facts:
    with open("test/test_pos.txt","w") as f_pos:
        with open("test/test_neg.txt","w") as f_neg:

            df = df.reindex(index=df.index[::-1])

            for idx, row in df.iterrows():

                label = str(row["DEATHCAUSECODE_UNDERLYING"])
                if "C18" in label:
                    label = "1"
                    out = f_pos
                    num_pos = num_pos + 1

                else:
                    label = "0"
                    out = f_neg
                    num_neg = num_neg + 1
                patid = row["PATIENTID"]
                linknum = row["LINKNUMBER"]
                if label == "1" and num_pos < num_exs or label == "0" and num_neg < num_exs:
                    out.write("diedofcancer"+"(id"+str(patid)+").\n")
                    pat_cols = [x for x in df.columns.values if x not in ["PATIENTID","LINKNUMBER"] and "VITAL" not in x and "DEATH" not in x]
                    for col in pat_cols:
                        val = re.sub(r'\W+', 'AN', str(row[col]))
                        facts.write(col.lower() + "(id" + str(patid) + "," + val + ").\n")

                    tumours = tumour[tumour["PATIENTID"] == patid]
                    for idx, trow in tumours.iterrows():
                        tid = trow["TUMOURID"]
                        facts.write("has_tumour(id" + str(patid) + "," + "tumourid"+str(tid)+ ").\n")
                        tum_cols = [x for x in tumours.columns.values if x not in ["PATIENTID", "TUMOURID","LINKNUMBER"] and x not in pat_cols and "DATE" not in x]

                        for col in tum_cols:
                            val = re.sub(r'\W+', 'AN', str(trow[col]))
                            facts.write(col.lower() + "(tumourid" + str(tid) + "," + val + ").\n")

                    rel_pats = sact_patient[sact_patient["LINK_NUMBER"] == linknum].reset_index()
                    if len(rel_pats > 0):
                        merged_id = rel_pats.iloc[0]["MERGED_PATIENT_ID"]

                        sact_tumours = sact_tumour[sact_tumour["MERGED_PATIENT_ID"] == merged_id]

                        for idx, mtrow in sact_tumours.iterrows():
                            mtid = mtrow["MERGED_TUMOUR_ID"]
                            facts.write("has_mergedtumour(id" + str(patid) + "," + "mergedtumourid"+str(mtid)+ ").\n")
                            mtum_cols = [x for x in sact_tumours.columns.values if x not in ["MERGED_TUMOUR_ID", "MERGED_PATIENT_ID"] and x not in pat_cols and x not in tum_cols and "DATE" not in x]

                            for col in mtum_cols:
                                val = re.sub(r'\W+', 'AN', str(mtrow[col]))

                                facts.write(col.lower() + "(mergedtumourid" + str(mtid) + "," + val + ").\n")

                            # Facts for Regimen
                            sact_regimens = sact_regimen[sact_regimen["MERGED_TUMOUR_ID"] == mtid]
                            for idx, mrrow in sact_regimens.iterrows():
                                mrid = mrrow["MERGED_REGIMEN_ID"]
                                facts.write(
                                    "has_mergedregimen(mergedtumourid" + str(mtid) + "," + "mergedregimenid" + str(mrid) + ").\n")
                                mreg_cols = [x for x in sact_regimens.columns.values if x not in ["MERGED_TUMOUR_ID", "MERGED_REGIMEN_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and "DATE" not in x]

                                for col in mreg_cols:
                                    val = re.sub(r'\W+', 'AN', str(mrrow[col]))

                                    facts.write(col.lower() + "(mergedregimenid" + str(mrid) + "," + \
                                                val + ").\n")


                                sact_cycles = sact_cycle[sact_cycle["MERGED_REGIMEN_ID"] == mrid]
                                for idx, mcrow in sact_cycles.iterrows():
                                    mcid = mcrow["MERGED_CYCLE_ID"]
                                    facts.write(
                                        "has_mergedcycle(mergedregimenid" + str(mrid) + "," + "mergedcycleid" + str(
                                            mcid) + ").\n")
                                    mcyc_cols = [x for x in sact_cycles.columns.values if
                                                 x not in ["MERGED_TUMOUR_ID", "MERGED_CYCLE_ID"
                                                           "MERGED_REGIMEN_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and x not in mreg_cols and "DATE" not in x]
                                    for col in mcyc_cols:
                                        val = re.sub(r'\W+', 'AN', str(mcrow[col]))

                                        facts.write(col.lower() + "(mergedcycleid" + str(mcid) + "," + \
                                                    val + ").\n")

                                    sact_drug_details = sact_drug_detail[sact_drug_detail["MERGED_CYCLE_ID"] == mcid]
                                    for idx, mdrow in sact_drug_details.iterrows():
                                        mddid = mdrow["MERGED_DRUG_DETAIL_ID"]
                                        facts.write(
                                            "has_mergeddrugdetail(mergedcycleid" + str(mcid) + "," + "mergeddrugdetailid" + str(
                                                mddid) + ").\n")
                                        mdd_cols = [x for x in sact_drug_details.columns.values if
                                                     x not in ["MERGED_TUMOUR_ID", "MERGED_CYCLE_ID", "MERGED_DRUG_DETAIL_ID",
                                                                                   "MERGED_REGIMEN_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and x not in mreg_cols and "DATE" not in x]
                                        for col in mdd_cols:
                                            val = re.sub(r'\W+', 'AN', str(mdrow[col]))

                                            facts.write(col.lower() + "(mergeddrugdetailid" + str(mddid) + "," + \
                                                        val + ").\n")


                                sact_outcomes = sact_outcome[sact_outcome["MERGED_REGIMEN_ID"] == mrid]
                                for idx, orow in sact_outcomes.iterrows():
                                    oid = orow["MERGED_OUTCOME_ID"]
                                    facts.write(
                                        "has_mergedoutcome(mergedregimenid" + str(mrid) + "," + "mergedoutcomeid" + str(oid) + ").\n")
                                    mout_cols = [x for x in sact_outcomes.columns.values if x not in ["MERGED_TUMOUR_ID",
                                                                                                      "MERGED_REGIMEN_ID","MERGED_OUTCOME_ID"] and x not in pat_cols and x not in tum_cols and x not in mtum_cols and x not in mreg_cols and "DATE" not in x]

                                    for col in mout_cols:
                                        val = re.sub(r'\W+', 'AN', str(orow[col]))

                                        facts.write(
                                            col.lower() + "(mergedoutcomeid" + str(oid) + "," + \
                                            val + ").\n")

                if num_pos >= num_exs and num_neg >= num_exs:
                    break

with open("train/train_bk.txt","w") as f:
    f.write("import: \"../simulacrum_bk.txt\".\n")

with open("test/test_bk.txt","w") as f:
    f.write("import: \"../simulacrum_bk.txt\".\n")

with open("simulacrum_bk.txt","w") as f:
    f.write("setParam: maxTreeDepth = 100.\n")
    f.write("setParam: nodeSize = 5.\n")
    #f.write("setParam: numOfClauses = 4).\n")
    #f.write("setParam: numOfClauses = 4).\n")
    #setParam: minLCTrees = 5;
    #setParam: incrLCTrees = 5;
    f.write("bridger: has_tumour/2.\n")
    for col in pat_cols:
        f.write("mode: "+col.lower()+"(+id,#var"+col.lower()+").\n")
    f.write("mode: has_tumour(+id,-tumourid).\n")
    for col in tum_cols:
        f.write("mode: " + col.lower() + "(+tumourid,#var" + col.lower() + ").\n")
    f.write("bridger: has_mergedtumour/2.\n")

    for col in mtum_cols:
        f.write("mode: " + col.lower() + "(+mergedtumourid,#var" + col.lower() + ").\n")
    f.write("mode: has_mergedtumour(+id,-mergedtumourid).\n")


    f.write("bridger: has_mergedregimen/2.\n")
    for col in mreg_cols:
        f.write("mode: " + col.lower() + "(+mergedregimenid,#var" + col.lower() + ").\n")
    f.write("mode: has_mergedregimen(+mergedtumourid,-mergedregimenid).\n")


    f.write("bridger: has_mergedcycle/2.\n")
    for col in mcyc_cols:
        f.write("mode: " + col.lower() + "(+mergedcycleid,#var" + col.lower() + ").\n")
    f.write("mode: has_mergedcycle(+mergedregimenid,-mergedcycleid).\n")

    f.write("bridger: has_mergeddrugdetail/2.\n")
    for col in mdd_cols:
        f.write("mode: " + col.lower() + "(+mergeddrugdetailid,#var" + col.lower() + ").\n")
    f.write("mode: has_mergeddrugdetail(+mergedcycleid,-mergeddrugdetailid).\n")

    f.write("bridger: has_mergedoutcome/2.\n")
    for col in mout_cols:
        f.write("mode: " + col.lower() + "(+mergedoutcomeid,#var" + col.lower() + ").\n")
    f.write("mode: has_mergedoutcome(+mergedregimenid,-mergedoutcomeid).\n")

    f.write("mode: diedofcancer(+id).")
