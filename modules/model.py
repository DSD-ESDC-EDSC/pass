import modules.aceso as aceso
import modules.db as db
import pandas as pd
import numpy as np

logger = db.init_logger()

# TO DO: USE query_execute() in db_init... or migrate that function in db.py for other use cases... TBD

def accessibility(bounds, beta, transportation, threshold):

    try:
        xmin = float(bounds['_southWest']['lng'])
        ymin = float(bounds['_southWest']['lat'])
        xmax = float(bounds['_northEast']['lng'])
        ymax = float(bounds['_northEast']['lat'])
    except Exception as e:
        logger.error(f'Data provided is not correct: {e}')

    # store in an array the geouids that are contained within the client's window view (bounding box)
    demand_query = """
        SELECT geouid, pop
        FROM demand
        WHERE ST_Contains(
            ST_Transform(
                ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                , 3347)
            , demand.centroid)
        ORDER BY geouid;
    """ % (xmin, ymin, xmax, ymax)

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(demand_query)
        demand = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])
        demand_array = np.array(demand['pop'])
        geouid_array = np.array(demand['geouid'])

    # store in an array the demand population counts that are contained within the client's window view (bounding box)
    supply_query = """
        SELECT geouid, supply
        FROM poi
        WHERE ST_Contains(
            ST_Transform(
                ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                , 3347)
            , poi.point)
        ORDER BY geouid;
    """ % (xmin, ymin, xmax, ymax)

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(supply_query)
        poi = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])
        poi_array = np.array(poi['geouid'])
        supply_array = np.array(poi['supply'])

    cols = ", poiuid_".join(poi_array)
    ids = ", ".join(map(str, geouid_array))

    # create data frame of distance matrix by first subsetting it based on the geouids and poiuids
    dm_query =  """
        SELECT geouid, poiuid_%s
        FROM distance_matrix_%s
        WHERE geouid = ANY(ARRAY[%s])
        ORDER BY geouid;
    """ % (cols, transportation, ids)

    with db.DbConnect() as db_conn:
        db_conn.cur.execute(dm_query)
        distance_matrix = pd.DataFrame(db_conn.cur.fetchall(), columns=[desc[0] for desc in db_conn.cur.description])

    geouid_array_len = str(len(geouid_array))
    demand_array_len = str(len(demand_array))
    poi_array_len = str(len(poi_array))
    supply_array_len = str(len(supply_array))
    distance_matrix_len = str(list(distance_matrix.columns.values))

    # for now just to confirm subsetting is correct and lengths match what is in the distance matrix
    logger.info(f'ARRAY LENGTH OF DEMAND CENTROID COUNTS: {geouid_array_len}')
    logger.info(f'ARRAY LENGTH OF DEMAND POPULATION COUNTS: {demand_array_len}')
    logger.info(f'ARRAY LENGTH OF SUPPLY SITE COUNTS: {poi_array_len}')
    logger.info(f'ARRAY LENGTH OF SUPPLY COUNTS: {supply_array_len}')
    logger.info(f'COLUMNS OF DISTANCE MATRIX: {distance_matrix_len}')

    # run models
    # scores should append to demand df
    print(type(demand_array))
    print(type(distance_matrix["poiuid_" + str(poi_array[0])]))
    print(type(beta))

    # TO DO: FIGURE OUT DATA TYPE ISSUES CAUSING ERRORS

    model = aceso.ThreeStepFCA(decay_function="negative_power", decay_params={"beta": 1.3})
    demand["scores"] = model.calculate_accessibility_scores(
        distance_matrix=distance_matrix,
        demand_array=demand_array,
        supply_array=supply_array
    )
    print(demand["scores"])

    # return scores
