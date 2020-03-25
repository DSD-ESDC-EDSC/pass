import modules.aceso as aceso
import modules.db as db
import pandas as pd
import numpy as np

logger = db.init_logger()

# TO DO: USE query_execute() in db_init... or migrate that function in db.py for other use cases... TBD

def accessibility(bounds, beta, transportation, threshold, demand_col, supply_col):

    try:
        xmin = float(bounds['_southWest']['lng'])
        ymin = float(bounds['_southWest']['lat'])
        xmax = float(bounds['_northEast']['lng'])
        ymax = float(bounds['_northEast']['lat'])
    except Exception as e:
        logger.error(f'Data provided is not correct: {e}')

    # store in an array the geouids that are contained within the client's window view (bounding box)
    demand_query = """
        SELECT geouid, ST_AsText(ST_Transform(boundary, 4326)) as boundary, %s
        FROM demand
        WHERE ST_Contains(
            ST_Transform(
                ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                , 3347)
            , demand.centroid)
        ORDER BY geouid;
    """ % (demand_col, xmin, ymin, xmax, ymax)

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(demand_query)
        demand = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])
        demand_array = np.array(demand[demand_col])
        geouid_array = np.array(demand['geouid'])

    # store in an array the demand population counts that are contained within the client's window view (bounding box)
    supply_query = """
        SELECT geouid, %s::float
        FROM poi
        WHERE ST_Contains(
            ST_Transform(
                ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                , 3347)
            , poi.point)
        ORDER BY geouid;
    """ % (supply_col, xmin, ymin, xmax, ymax)

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(supply_query)
        poi = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])
        poi_array = np.array(poi['geouid'])
        supply_array = np.array(poi[supply_col])

    # script to derive column and population demand geouids that need to be in data frame
    cols = ", poiuid_".join(poi_array)
    ids = ", ".join(map(str, geouid_array))
    dist = ["poiuid_" + col + " <= " + str(threshold) for col in poi_array]
    where = " OR ".join(dist) # where statement to get all distances equal to or within threshold

    # create data frame of distance matrix by first subsetting it based on the geouids and poiuids
    # filter also by distance threshold
    '''
    dm_query = """
        SELECT geouid, poiuid_%s
        FROM distance_matrix_%s
        WHERE geouid = ANY(ARRAY[%s]) AND (%s) 
        ORDER BY geouid;
    """ % (cols, transportation, ids, where)
    '''
    dm_query = """
        SELECT geouid, poiuid_%s
        FROM distance_matrix_%s
        WHERE (%s) 
        ORDER BY geouid;
    """ % (cols, transportation, where)   

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(dm_query)
        distance_matrix = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])
        # filtering in pandas because db call is giving strange error - FOR CHELSEA 
        distance_matrix = distance_matrix[distance_matrix.geouid.isin(geouid_array)]
        geouid_filtered_array = np.array(distance_matrix['geouid'])
        distance_matrix = distance_matrix.drop('geouid', axis=1)

    
    
    
    # store the population demand geouids that are within the threshold
    ids_filtered = ", ".join(map(str, geouid_filtered_array))
    
    # get the population demand data now with the filtered geouids
    '''
    demand_filtered_query = """
        SELECT geouid, ST_AsText(ST_Transform(boundary, 4326)) as boundary, pop
        FROM demand
        WHERE geouid = ANY(ARRAY[%s]) 
        ORDER BY geouid;
    """ % (ids_filtered)

    demand_filtered_query = """
    SELECT geouid, ST_AsText(ST_Transform(boundary, 4326)) as boundary, pop
    FROM demand
    ORDER BY geouid;
    """

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(demand_filtered_query)
        demand_filtered = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])
        demand_filtered = demand_filtered[demand_filtered.geouid.isin(geouid_filtered_array)]
        demand_filtered_array = np.array(demand_filtered['pop'])
    '''
    demand_filtered = demand[demand.geouid.isin(geouid_filtered_array)]
    demand_filtered_array = np.array(demand_filtered[demand_col])

    # filtering with pandas because db call is giving strange error- FOR CHELSEA 
    
    # geouid_array_len = str(len(geouid_array))
    # demand_array_len = str(len(demand_filtered_array))
    # poi_array_len = str(len(poi_array))
    # supply_array_len = str(len(supply_array))
    # distance_matrix_col_len = str(list(distance_matrix.columns.values))
    # distance_matrix_row_len = str(len(distance_matrix.index))

    # for now just to confirm subsetting is correct and lengths match what is in the distance matrix
    # logger.info(f'ARRAY LENGTH OF DEMAND CENTROID COUNTS: {geouid_array_len}')
    # logger.info(f'ARRAY LENGTH OF DEMAND POPULATION COUNTS BASED ON FILTERED DISTANCE THRESHOLD: {demand_array_len}')
    # logger.info(f'ARRAY LENGTH OF SUPPLY SITE COUNTS: {poi_array_len}')
    # logger.info(f'ARRAY LENGTH OF SUPPLY COUNTS: {supply_array_len}')
    # logger.info(f'COLUMNS OF DISTANCE MATRIX: {distance_matrix_col_len}')
    # logger.info(f'ROWS OF DISTANCE MATRIX: {distance_matrix_row_len}')

    try:
        model = aceso.ThreeStepFCA(decay_function='negative_power', decay_params={'beta': beta})
        demand_filtered['scores'] = model.calculate_accessibility_scores(
            distance_matrix=distance_matrix,
            demand_array=demand_filtered_array,
            supply_array=supply_array
        )
        logger.info(f'Successfully calculated accessibility scores')
    except Exception as e:
        logger.error(f'Unsuccessfully calculated accessibility scores: {e}')
        return e
    
    # TO DO: MAKE SCORE MORE INTERPRETABLE
    demand_filtered['scores'] = demand_filtered['scores'].apply(lambda x: x * 100000)
    
    return demand_filtered
