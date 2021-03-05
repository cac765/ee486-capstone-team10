import os
import logging

# Instantiate the logger
logging.basicConfig( format='%(levelname)s: %(message)s', level=logging.INFO )

def insert_into_sql(suffix_group: str, table_name: str, values: list):
    """Responsible for posting data to the SQL table by using the correct suffix group."""
    try:
        # Build SQL Query
        sql_cmd = f"insert into {table_name} values("
        for index, value in enumerate(values):
            sql_cmd += f"{value}"
            if index != len(values) - 1:
                sql_cmd += ", "
        sql_cmd += ")"

        # Build OS Command
        os_cmd = f"mysql --defaults-group-suffix={suffix_group} -e \"{sql_cmd}\""

        # Run OS SQL Query
        query = os.popen(os_cmd).read()
        logging.info(query)

    except:
        print(f"[ERROR] Error inserting data into SQL Table: {table_name} with suffix {suffix_group}")

def read_from_sql(suffix_group: str, table_name: str):
    """Responsible for reading data from a sql table. Used for debug."""
    try:
        # Build SQL Query
        sql_cmd = f"select * from {table_name}"

        # Build OS Command
        os_cmd = f"mysql --defaults-group-suffix={suffix_group} -e \"{sql_cmd}\""

        # Run SQL Query
        query = os.popen(os_cmd).read()
        logging.info(query)

    except:
        print(f"[ERROR] Error reading from {table_name} with suffix {suffix_group}")
