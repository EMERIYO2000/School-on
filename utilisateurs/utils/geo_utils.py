import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en kilomètres entre deux points géographiques.
    """
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')

    # Rayon moyen de la Terre en kilomètres
    R = 6371.0

    # Conversion des degrés en radians
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    # Formule de Haversine
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    distance = R * c
    return round(distance, 2)  # Distance arrondie à 2 décimales