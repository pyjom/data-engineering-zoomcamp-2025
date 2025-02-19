import pandas as pd 
from sqlalchemy import create_engine
from time import time
import argparse, os



def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    # Download the CSV

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000, compression='gzip')

    df = next(df_iter)

    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()

            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print('Inserted another chunk, took %.3f second' % (t_end - t_start))
        except StopIteration:
            break    


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(
                        prog='postgres-etl-v1',
                        description='Ingest CSV data to Postgres',
                        epilog='pyjom2025m1')

    parser.add_argument('--user', help='user name for postgres') 
    parser.add_argument('--password', help='password for postgres') 
    parser.add_argument('--host', help='host for postgres') 
    parser.add_argument('--port', help='port for postgres') 
    parser.add_argument('--db', help='db for postgres') 
    parser.add_argument('--table_name', help='table_name for postgres')        
    parser.add_argument('--url', help='url for postgres') 

    args = parser.parse_args()
    main(args)