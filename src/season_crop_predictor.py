# Crop Season Prediction Module

# This module provides functions to predict suitable crops for a given season
# and to determine the season for a given crop, based on Indian agricultural cycles.

SEASON_CROP_MAP = {
    "Kharif": ["Rice", "Maize", "Cotton", "Soybean", "Groundnut"],
    "Rabi": ["Wheat", "Barley", "Mustard", "Gram", "Peas"],
    "Zaid": ["Watermelon", "Cucumber", "Fodder Crops"],
}

CROP_SEASON_MAP = {}
for season, crops in SEASON_CROP_MAP.items():
    for crop in crops:
        CROP_SEASON_MAP.setdefault(crop.lower(), []).append(season)

SEASON_DETAILS = {
    "Kharif": {
        "sowing": "June–July",
        "harvesting": "Sept–Oct",
        "regions": ["Punjab", "Haryana", "Uttar Pradesh", "Bihar", "West Bengal", "Odisha", "Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka", "Maharashtra"],
        "description": "Monsoon season crops, dependent on southwest monsoon rains."
    },
    "Rabi": {
        "sowing": "October–December",
        "harvesting": "February–April",
        "regions": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Maharashtra", "Gujarat", "Bihar", "West Bengal", "Assam"],
        "description": "Winter season crops, grown with the help of irrigation."
    },
    "Zaid": {
        "sowing": "March–June",
        "harvesting": "May–June",
        "regions": ["Gujarat", "Rajasthan", "Uttar Pradesh", "Punjab", "Haryana", "Tamil Nadu", "Andhra Pradesh", "Karnataka"],
        "description": "Summer season crops, grown with the help of irrigation."
    }
}

# Major crop growing regions in India
CROP_REGIONS = {
    "Rice": ["West Bengal", "Punjab", "Uttar Pradesh", "Andhra Pradesh", "Tamil Nadu", "Bihar", "Odisha", "Assam", "Chhattisgarh"],
    "Wheat": ["Uttar Pradesh", "Punjab", "Haryana", "Madhya Pradesh", "Rajasthan", "Bihar", "Gujarat"],
    "Maize": ["Karnataka", "Andhra Pradesh", "Tamil Nadu", "Rajasthan", "Maharashtra", "Bihar", "Uttar Pradesh"],
    "Cotton": ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Punjab", "Haryana", "Rajasthan"],
    "Soybean": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana"],
    "Groundnut": ["Gujarat", "Rajasthan", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Maharashtra"],
    "Barley": ["Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Haryana", "Punjab"],
    "Mustard": ["Rajasthan", "Haryana", "Madhya Pradesh", "Uttar Pradesh", "Gujarat", "West Bengal"],
    "Gram": ["Madhya Pradesh", "Rajasthan", "Maharashtra", "Uttar Pradesh", "Karnataka", "Andhra Pradesh"],
    "Peas": ["Uttar Pradesh", "Madhya Pradesh", "Punjab", "Himachal Pradesh", "Uttarakhand"],
    "Watermelon": ["Andhra Pradesh", "Tamil Nadu", "Karnataka", "Uttar Pradesh", "Odisha"],
    "Cucumber": ["Andhra Pradesh", "Karnataka", "Maharashtra", "Tamil Nadu", "Uttar Pradesh"],
    "Fodder Crops": ["Punjab", "Haryana", "Uttar Pradesh", "Rajasthan", "Gujarat"]
}

def crops_for_season(season):
    """Return list of major crops for a given season."""
    return SEASON_CROP_MAP.get(season.capitalize(), [])

def season_for_crop(crop):
    """Return list of seasons in which a crop can be grown."""
    return CROP_SEASON_MAP.get(crop.lower(), [])

def get_season_details(season):
    """Return detailed information about a season including months and regions."""
    season = season.capitalize()
    if season in SEASON_DETAILS:
        return {
            "sowing": SEASON_DETAILS[season]["sowing"],
            "harvesting": SEASON_DETAILS[season]["harvesting"],
            "regions": SEASON_DETAILS[season]["regions"],
            "description": SEASON_DETAILS[season]["description"]
        }
    return None

def get_crop_regions(crop):
    """Return major growing regions for a specific crop."""
    return CROP_REGIONS.get(crop, ["Information not available"])

def get_crop_details(crop):
    """Get comprehensive details about a crop including seasons and regions."""
    crop_lower = crop.lower()
    seasons = CROP_SEASON_MAP.get(crop_lower, [])
    
    if not seasons:
        return None
        
    season_info = {}
    for season in seasons:
        season_info[season] = {
            "sowing": SEASON_DETAILS[season]["sowing"],
            "harvesting": SEASON_DETAILS[season]["harvesting"]
        }
    
    return {
        "crop": crop,
        "seasons": seasons,
        "season_details": season_info,
        "growing_regions": CROP_REGIONS.get(crop, [])
    }
