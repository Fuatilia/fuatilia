import json
from fuzzywuzzy import fuzz

f_finance_bill = open('app/scripts/finance_bill_2nd_reading_votes.json')
f_affordable_housing = open('app/scripts/affordable_housing_votes.json')

threshold = 90 # for fuzzyWuzzy

names_without_descrepancies = []

finance_bill_data = json.load(f_finance_bill)
affordable_housing_data = json.load(f_affordable_housing)

actual_afh_names = list(affordable_housing_data.keys())
afh_names = [rep_name.lower().replace('hon','').replace('mp','' ).replace('cbs','' ).lstrip().rstrip()
             for rep_name in actual_afh_names]


print("Total count for housing levy data ",len(actual_afh_names) )
print("Total count for finance bill data ", len(finance_bill_data.keys()))

new_compilation = {}
match_count = 0
# On iterating use this as the "global" interchange variable
# for names in affordable housing
afh_name_to_use = ''

for fbill_name in finance_bill_data.keys():
    percent_match = 0
    for ind, afhbill_name in enumerate(afh_names):
        match_ratio = fuzz.partial_ratio(fbill_name.lower().replace('hon.','').replace('mp','' ).replace('cbs','' ).lstrip().rstrip(), afhbill_name)

        if match_ratio>threshold and match_ratio>percent_match:
            percent_match = match_ratio
            afh_name_to_use = actual_afh_names[ind]
        

    if percent_match>threshold: 
        match_count +=1
        names_without_descrepancies.append(afh_name_to_use)
        print(fbill_name.lower(), percent_match, afh_name_to_use.lower().replace('hon','').replace('mp',''))
        # print(finance_bill_data[fbill_name], affordable_housing_data[afhbill_name])

        new_compilation[fbill_name] = {
            "AFFORDABLE HOUSING":{
                'vote': affordable_housing_data[afh_name_to_use]['AFFORDABLE HOUSING']['vote']
            },
            "FINANCE BILL 2ND READING":{
                'vote':finance_bill_data[fbill_name]
            },
            
        }
    else:
        new_compilation[fbill_name] = {
            "AFFORDABLE HOUSING":{
                'vote': 'N/A'
            },
            "FINANCE_BILL 2ND READING":{
                'vote':finance_bill_data[fbill_name]
            },
        }

with open("app/scripts/afh_fb2r_combination.json", "w") as outfile: 
    json.dump(new_compilation, outfile, indent=4)


names_with_descrepancies = list(set(actual_afh_names) - set(names_without_descrepancies))

print("Total entries => ", len(new_compilation.keys()))
print("Total matches found => ",match_count)
print("{0} names with descrepancies (Names in AFH-Bill missing in Finance Bill)=> {1}".format( 
      len(set(names_with_descrepancies)),set(names_with_descrepancies))
      )

# Closing file
f_finance_bill.close()
f_affordable_housing.close()