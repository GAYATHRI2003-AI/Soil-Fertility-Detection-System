"""
Geospatial utilities for soil fertility mapping and analysis.
Handles map data, coordinate transformations, and spatial analysis.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
import os

class GeoSoilAnalyzer:
    def __init__(self, crs: str = 'EPSG:4326'):
        """
        Initialize the geospatial soil analyzer.
        
        Args:
            crs: Coordinate Reference System (default: WGS84)
        """
        self.crs = crs
        self.india_map = None
        self.soil_data = None
        
    def load_india_shapefile(self, shapefile_path: str) -> None:
        """
        Load India state boundaries from a shapefile.
        
        Args:
            shapefile_path: Path to the shapefile (.shp) containing India state boundaries
        """
        self.india_map = gpd.read_file(shapefile_path).to_crs(self.crs)
    
    def load_soil_data(self, data: pd.DataFrame, 
                      lat_col: str = 'latitude', 
                      lon_col: str = 'longitude') -> None:
        """
        Load soil data with geographic coordinates.
        
        Args:
            data: DataFrame containing soil data
            lat_col: Name of the latitude column
            lon_col: Name of the longitude column
        """
        self.soil_data = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data[lon_col], data[lat_col]),
            crs=self.crs
        )
    
    def create_fertility_map(self, parameter: str, 
                           output_path: Optional[str] = None,
                           title: str = 'Soil Fertility Map') -> None:
        """
        Create a choropleth map of soil fertility parameters.
        
        Args:
            parameter: Soil parameter to visualize (e.g., 'N', 'P', 'K', 'pH')
            output_path: Path to save the output image (optional)
            title: Title for the plot
        """
        if self.india_map is None or self.soil_data is None:
            raise ValueError("India map and soil data must be loaded first")
            
        # Spatial join between points and state boundaries
        joined = gpd.sjoin(self.india_map, self.soil_data, how='left', op='contains')
        
        # Group by state and calculate mean of the parameter
        state_stats = joined.groupby('ST_NM')[parameter].mean().reset_index()
        
        # Merge back with the original map
        result = self.india_map.merge(state_stats, on='ST_NM', how='left')
        
        # Create the plot
        fig, ax = plt.subplots(1, 1, figsize=(15, 15))
        result.plot(column=parameter, 
                   ax=ax, 
                   legend=True,
                   legend_kwds={'label': f"{parameter} Level"},
                   cmap='YlOrRd',  # Yellow-Orange-Red colormap
                   missing_kwds={"color": "lightgrey", "label": "Missing data"})
        
        # Add state boundaries
        self.india_map.boundary.plot(ax=ax, linewidth=1, color='black')
        
        # Add title and labels
        plt.title(title, fontsize=16)
        plt.axis('off')
        
        # Save or show the plot
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def calculate_ndvi(self, nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
        """
        Calculate Normalized Difference Vegetation Index (NDVI).
        
        Args:
            nir_band: Near-Infrared band array
            red_band: Red band array
            
        Returns:
            NDVI array with values between -1 and 1
        """
        # Avoid division by zero
        ndvi = np.where(
            (nir_band + red_band) == 0.0,
            0,
            (nir_band - red_band) / (nir_band + red_band)
        )
        return ndvi
    
    def get_growing_period(self, region: str) -> str:
        """
        Get Length of Growing Period (LGP) based on agro-climatic zone.
        
        Args:
            region: Agro-climatic zone (e.g., 'Hot Semi-Arid')
            
        Returns:
            String describing the growing period
        """
        lgp_map = {
            'Hot Arid': '60-90 days',
            'Hot Semi-Arid': '90-150 days',
            'Hot Sub-humid': '150-180 days',
            'Hot Humid': '180-210 days',
            'Cold Arid': '60-90 days',
            'Cold Semi-Arid': '90-150 days',
            'Cold Sub-humid': '150-180 days',
            'Cold Humid': '180-210 days'
        }
        return lgp_map.get(region, 'Not specified')
