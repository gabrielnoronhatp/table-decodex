import re
import json
import oracledb
import getpass

# Inicializando o cliente Oracle Lembre-se de mudar aqui para o local do seu arquivo
oracledb.init_oracle_client(lib_dir=r"C:\Users\gabriel.noronha\Downloads\instantclient-basic-windows.x64-23.6.0.24.10\instantclient_23_6")

un = 'consulta'
cs = '//10.2.1.194:1521/TPJPRD'
pw = 'consultawint'


sql = """
SELECT 
    R1.INTEGRADORA AS "COD_INTEGRADORA",
    R1.STATUSORD,
    R1.DESCSTATUSORD,
    R1.IDNOTAAPI,
    R1.DTGERRET AS "DATA_RETORNO",
    R1.LOGSTATUSORD
FROM PCPEDRETORNO R1
WHERE TRUNC(R1.DTGERRET) BETWEEN TO_DATE('01/12/2024', 'DD/MM/YYYY') AND TO_DATE('19/12/2024', 'DD/MM/YYYY')
AND R1.NUMTRANSVENDA IN (133999187, 133999842, 133999636, 133999325)
AND R1.INTEGRADORA = 3723
AND R1.STATUSORD = 'NR'
"""

# Inicializando a lista de dados extraídos
extracted_data = []

try:
    with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
        print("Conexão bem-sucedida!")
        with connection.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall() 

            with open('consulta_log.txt', 'w') as log_file:
                for row in results:

                    log_file.write(', '.join(str(value) for value in row) + '\n')  

            print("Resultados gravados em consulta_log.txt")

          
            for row in results:
                log_data = ', '.join(str(value) for value in row)

              
                id_pattern = r'(\d+),\s*NR,\s*INVOICE_RECEIVED,\s*(\d+),\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),'
                response_pattern = r'\[Resposta da API = (.+?)\]'
                ean_pattern = r'ean:"(\d+)"'
                quantity_pattern = r'ordered_quantity:(\d+)'
                discount_pattern = r'wholesaler_discount:(\d+\.\d{2})'

                id_match = re.search(id_pattern, log_data)
                order_id = id_match.group(1) if id_match else None

                response_match = re.search(response_pattern, log_data)
                response_data = json.loads(response_match.group(1)) if response_match else None

                ean_match = re.search(ean_pattern, log_data)
                quantity_match = re.search(quantity_pattern, log_data)
                discount_match = re.search(discount_pattern, log_data)

                ean = ean_match.group(1) if ean_match else None
                quantity = quantity_match.group(1) if quantity_match else None
                discount = discount_match.group(1) if discount_match else None

              
                extracted_data.append({
                    "Order ID": order_id,
                    "Invoice ID": row[3],  
                    "EAN": ean,
                    "Response Quantity": quantity,
                    "Discount Percentage": discount,
                    "Return Date": row[4]  
                })

except oracledb.DatabaseError as e:
    print(f"Erro ao conectar ou executar a consulta: {e}")

# Gravando os dados extraídos no arquivo de log
with open('extraction_log.txt', 'a') as extraction_file:
    for data in extracted_data:
        extraction_file.write(f"Order ID: {data['Order ID']}\n")
        extraction_file.write(f"Invoice ID: {data['Invoice ID']}\n")
        extraction_file.write(f"EAN: {data['EAN']}\n")
        extraction_file.write(f"Response Quantity: {data['Response Quantity']}\n")
        extraction_file.write(f"Discount Percentage: {data['Discount Percentage']}\n")
        extraction_file.write(f"Return Date: {data['Return Date']}\n")
        extraction_file.write("\n")

# Imprimindo os resultados
for data in extracted_data:
    print(f"Order ID: {data['Order ID']}")
    print(f"Invoice ID: {data['Invoice ID']}")
    print(f"EAN: {data['EAN']}")
    print(f"Response Quantity: {data['Response Quantity']}")
    print(f"Discount Percentage: {data['Discount Percentage']}")
    print(f"Return Date: {data['Return Date']}")
    print("-" * 20)
