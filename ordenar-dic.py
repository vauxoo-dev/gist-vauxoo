f=file("/home/jage/instancias/clubj/report_picking_out_txt/__openerp__.py", "r")
content=f.read().splitlines()

contador=0
diccionario={}
for line in content:
    if contador==0:
        key=line
        diccionario[key]=[]
    else:
        diccionario[key].append(line)
    contador+=1
    if contador==6:
        contador=0

print diccionario
