import requests, json, sys

'''
Script used to get VEP output singly for a list of RS IDs in a file.
Only to be used when the POST method in "run_snp_to_gene_pipeline.py" fails due to a bas RS ID.
'''

input_file = sys.argv[1]
rs_ids = [rs_id.strip() for rs_id in open(input_file, 'r').read().split('\n')]
server = "https://rest.ensembl.org"
for rs_id in rs_ids:
    ext = "/vep/human/id/%s?" % rs_id
    req = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
    if not req.ok:
        print "%s\tBAD RS ID" % rs_id
    decoded = req.json()
    print "%s\t%s" % (rs_id, json.dumps(decoded))