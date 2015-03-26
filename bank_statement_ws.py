# -*- encoding: utf-8 -*-
import oerplib
import time
import csv
import argparse
import base64

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--db", help="DataBase Name", required=True)
PARSER.add_argument("-r", "--user", help="OpenERP User", required=True)
PARSER.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
PARSER.add_argument("-p", "--port",
                    type=int,
                    help="Port, 8069 for default", default="8069")
PARSER.add_argument("-s", "--server",
                    help="Server IP, 127.0.0.1 for default",
                    default="127.0.0.1")
ARGS = PARSER.parse_args()

if ARGS.db is None or ARGS.user is None or ARGS.passwd is None:
    print "Must be specified DataBase, User and Password"
    quit()

BANK_ST_LINE = [640, 785, 920, 797, 928, 675, 676, 677, 678, 940, 941, 688, 726, 734, 611, 742, 746, 631, 639]
#BANK_ST_LINE = [112]
DB_NAME = ARGS.db
USER = ARGS.user
PASSW = ARGS.passwd
SERVER = ARGS.server
PORT = ARGS.port

OERP_CONNECT = oerplib.OERP(SERVER,
                            database=DB_NAME,
                            protocol='xmlrpc', port=PORT)

UID_CONF = OERP_CONNECT.login(USER, PASSW)

# ID de account bank statement line
# Editar vista agregando campo "id" para obtener el valor
for bank_line in BANK_ST_LINE:
    print bank_line
    st_line = OERP_CONNECT.browse('account.bank.statement.line', bank_line)

    print st_line,"wwwwwwwwwwwwwwwww"
    move_bank_statement = []

    for move_line_id in st_line.journal_entry_id.line_id:
        if move_line_id.reconcile_id:
            for move_reconcile in move_line_id.reconcile_id.line_id:
                if move_line_id.id != move_reconcile.id:
                    # Creamos tipo de diccionario para que pueda ser procesado
                    # por la funcion que hace la conciliacion(pago)
                    # Funcion process_reconciliation
                    # Donde @counterpart_move_line_id es aml de provicion(factura)
                    # credit/debit la cantidad que se esta pagando
                    move_bank_statement.append({
                        'counterpart_move_line_id': move_reconcile.id,
                        'credit': move_reconcile.debit,
                        'debit': move_reconcile.credit,
                        'name': move_line_id.name})

    # Al ejecutarse esta funcion desconcilia los movimientos que gurdamos en
    # @move_bank_statement tambien elimina la poliza
    # Se pone en un try la funcion por que hay un "bug" con oerplib cuando
    # la funcion no tiene "Return" marca error el webservices.
    try:
        OERP_CONNECT.execute(
            'account.bank.statement.line',
            'cancel',
            [st_line.id])
    except:
        print "Error en return de metodo cancel"

    # Ejecuta el proceso de conciliacion de bank statement
    # Mismo "Bug" la funcion no tiene "Return" por eso esta en un try
    try:
        OERP_CONNECT.execute(
            'account.bank.statement.line',
            'process_reconciliation',
            st_line.id,
            move_bank_statement)
    except:
        print "Error en return de metodo process_reconciliation"
