import mysql.connector
destclass="lssh"+"202"
lssh1 = mysql.connector.connect(
host = "203.145.220.59",
port = "3306",
user = "liaojason2",
password = "Liaojason123!",
database = destclass)
gcpsql= lssh1.cursor()
output=""
sql_select_Query = "select * from body_temperture"
gcpsql.execute(sql_select_Query)
records = gcpsql.fetchall()
output+=" 體溫總表：\n\n"
for row in records:
    output+=str(row[1])+". "+str(row[3])+" "+str(row[4])+"\n"
print(output)