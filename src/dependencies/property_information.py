import requests
from urllib.parse import quote
import time
from opensearchpy import OpenSearch
import json

import src.dependencies.fire_and_rescue as fire_and_rescue


def send_slack_notification(message):
    webhook_url = "https://hooks.slack.com/services/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"
    slack_data = {'text': message}
    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


client = OpenSearch(
    hosts=[{"host": "opensearch.dev-op.co.uk", "port": 443}],
    http_auth=("admin", "admin"),
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


def get_lon_lat_from_uprn(uprn):
    # lookup the uprn in the uprn index
    response = client.search(
        index="uprns",
        body={
            "query": {
                "match": {
                    "UPRN": uprn
                }
            }
        }
    )
    if response['hits']['total']['value'] == 0:
        return None
    else:
        return {
            "lat": float(response['hits']['hits'][0]['_source']['location']['lat']),
            "lon": float(response['hits']['hits'][0]['_source']['location']['lon'])
        }


def get_boundaries(lat, lon):
    response = client.search(
        index="inspirepolygons-*",
        body={
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "geo_shape": {
                            "location": {
                                "shape": {
                                    "type": "point",
                                    "coordinates": [lon, lat]
                                },
                                "relation": "intersects"
                            }
                        }
                    }
                }
            }
        }
    )
    return response

# get all points from listed index that are within 500m of the polygon
# response = client.search(
#     index="listed-*",
#     body={
#         "query": {
#             "bool": {
#                 "must": {
#                     "match_all": {}
#                 },
#                 "filter": {
#                     "geo_distance": {
#                         "distance": "500m",
#                         "location": {
#                             "lat": 51.507351,
#                             "lon": -0.127144
#                         }
#                     }
#                 }
#             }
#         }
#     }
# )

# function to get all listed buildings within 500m of a polygon


def get_listed_buildings(lon, lat):
    response = client.search(
        index="listedproperties",
        body={
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "geo_distance": {
                            "distance": "500m",
                            "location": {
                                "lat": lat,
                                "lon": lon
                            }
                        }
                    }
                }
            }
        }
    )

    print(response)

    return response


def get_historicalfloods(lat, lon):
    response = client.search(
        index="historicfloods",
        body={
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },                    
                    "filter": {
                        "geo_distance": {
                            "distance": "500m",
                            "location": {
                                "lat": lat,
                                "lon": lon
                            }
                        }
                    }
                }
            }
        }
    )
    print(response)

    return response



# def get_dayroadnoise(lat, lon):
#     response = client.search(
#         index="dayroadnoise",
#         body={
#             "query": {
#                 "bool": {
#                     "must": {
#                         "match_all": {}
#                     },
#                     "filter": {
#                         "geo_distance": {
#                             "distance": "500m",
#                             "location": {
#                                 "lat": lat,
#                                 "lon": lon
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     )
#     return response


# def get_nightroadnoise(lat, lon):
#     response = client.search(
#         index="nightroadnoise",
#         body={
#             "query": {
#                 "bool": {
#                     "must": {
#                         "match_all": {}
#                     },
#                     "filter": {
#                         "geo_distance": {
#                             "distance": "500m",
#                             "location": {
#                                 "lat": lat,
#                                 "lon": lon
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     )
#     return response


# def get_railnoise(lat, lon):
#     response = client.search(
#         index="railnoise",
#         body={
#             "query": {
#                 "bool": {
#                     "must": {
#                         "match_all": {}
#                     },
#                     "filter": {
#                         "geo_distance": {
#                             "distance": "500m",
#                             "location": {
#                                 "lat": lat,
#                                 "lon": lon
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     )
#     return response


def get_fire_and_rescue_authority(lat, lon):
    response = client.search(
        index="fire_rescue_authorities",
        _source_includes=["name"],
        body={
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "geo_shape": {
                            "location": {
                                "shape": {
                                    "type": "point",
                                    "coordinates": [lon, lat]
                                },
                                "relation": "intersects"
                            }
                        }
                    }
                }
            }
        }
    )

    if response is not None:
        # if hits is empty, return 404
        if len(response['hits']['hits']) == 0:
            return "Not found"
        output = response['hits']['hits'][0]['_source']['name']

        # if output has & in it, replace with and
        if "&" in output:
            output = output.replace("&", "and")

        return output
    return "Not found"


def get_fire_and_rescue_data(authority):
    try:
        if authority == "London Fire and Emergency Planning Authority":
            authority = "Greater London"
        elif authority == "Royal Berkshire":
            authority = "Berkshire"
        elif authority == "Buckinghamshire and Milton Keynes":
            authority = "Buckinghamshire"
        elif authority == "Stoke-on-Trent and Staffordshire":
            authority = "Staffordshire"
        elif authority == "Nottinghamshire and City of Nottingham":
            authority = "Nottinghamshire"
        elif authority == "County Durham and Darlington":
            authority = "Durham"
        elif authority == "Isles of Scilly":
            authority = "Isles Of Scilly"

        output = {}
        output = fire_and_rescue.data[authority]
        return output
    except:
        message = "Error getting fire and rescue data for " + authority
        print(message)
        send_slack_notification(message)
        return None
