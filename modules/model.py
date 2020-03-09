from aceso import decay, gravity
import db

def accessibiltiy(bounds, beta, transportation, threshold):

    # prepare params (query db based on params):
    # SELECT demand WHERE
    # SELECT poi where
    # distance_matrix... HOW DO WE GET DATA WITHIN SPECIFIC BOUDNS? GET POI UIDs then join table based on that? I have some script for this already, will find

    # run models
    # scores should append to demand df

    #scores = gravity.calculate_accessibility_scores(
    #     self,
    #     distance_matrix,
    #     demand_array=None,
    #     supply_array=None
    # )

    # return scores
