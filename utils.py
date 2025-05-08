import json,csv

def write_json(obj_list: list[dict],fn: str):
    with open(fn,'w',encoding='utf-8') as file:
        json.dump({'items':obj_list},file,indent=4)    

def write_csv(header: list,rows: list,fn: str):
    with open(fn,'w',encoding='utf-8') as file:
        writer = csv.writer(file,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(rows)