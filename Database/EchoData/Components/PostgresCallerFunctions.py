from configparser import ConfigParser
from time import time
import pandas as pd
import psycopg2



def ReadDatabaseQuery(query_file, verbose=False, start=time()):
        
    ''' Accepts query file, returns database query '''    
        
    with open(query_file, 'r') as file:
        database_query = file.read()
        
    if verbose:
        print('[@ %7.2f s]: Read databse query from [%s]' %(time()-start, query_file))
    
    return database_query



def QueryDatabase(database_dictionary, database_query, verbose=False, start=time()):
    
    ''' Accepts database dictionary, SQL query string, returns query results '''
    
    try:
        
        # establish connection:
        connection = psycopg2.connect(
            host = database_dictionary['host'],
            database = database_dictionary['database'],
            user = database_dictionary['user'],
            password = database_dictionary['password'],
        )

        # build cursor:
        cursor = connection.cursor()

        # execute query:
        cursor.execute(database_query)
    
        # retreive result:
        result = cursor.fetchall()

        # commit changes:
        connection.commit()
        
        # close cursor:
        cursor.close()
        
    except psycopg2.DatabaseError as error:
        
        # handle exceptions:
        print('[QueryDatabase]: Database error: %s' %error)
        result = None

    finally:
        
        # close connection:
        if connection is not None:
            connection.close()
    
    if verbose:
        print('[@ %7.2f s] [QueryDatabase]: Queried database' %(time()-start))
        
    return result