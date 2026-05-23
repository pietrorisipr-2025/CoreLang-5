import csv, json, sys
def load_impacts(csv_path):
    items=[]; 
    with open(csv_path, newline='', encoding='utf-8') as f:
        r=csv.DictReader(f)
        for row in r:
            impact=float(row.get('impact_score', row.get('Savings_MB','0')))
            name=row.get('Block') or row.get('Name') or row.get('Category') or 'Unknown'
            items.append((name,impact))
    return items
def assign_priorities(items):
    items=sorted(items,key=lambda x:x[1],reverse=True); total=sum(x[1] for x in items) or 1.0; cum=0.0; out=[]
    for i,(name,imp) in enumerate(items,1):
        cum+=imp; band='A' if cum/total<=0.8 else ('B' if cum/total<=0.95 else 'C')
        out.append({'name':name,'impact':imp,'priority_band':band,'priority':i})
    return out
def main():
    if len(sys.argv)<3: print('Uso: pareto_packer <impacts.csv> <out.json>'); sys.exit(2)
    pr=assign_priorities(load_impacts(sys.argv[1]))
    with open(sys.argv[2],'w',encoding='utf-8') as f: json.dump(pr,f,indent=2,ensure_ascii=False)
    print('Scritto', sys.argv[2])
if __name__=='__main__': main()
