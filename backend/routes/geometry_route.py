from typing import Optional

import geopandas as gpd
from pydantic import BaseModel
from shapely.geometry import Point, mapping
from fastapi import APIRouter, HTTPException

from core import setting

router = APIRouter()

GEO_TINH_PATH = setting.base_dir / "artifacts" / "geotinh.geojson"
GEO_XA_PATH = setting.base_dir / "artifacts" / "geoxa.geojson"

gdf_tinh: Optional[gpd.GeoDataFrame] = None
gdf_xa: Optional[gpd.GeoDataFrame] = None
_load_errors = {}
try:
    gdf_tinh = gpd.read_file(str(GEO_TINH_PATH))
except Exception as e:
    _load_errors['tinh'] = str(e)

try:
    gdf_xa = gpd.read_file(str(GEO_XA_PATH))
except Exception as e:
    _load_errors['xa'] = str(e)


class SearchGeometryRequest(BaseModel):
    lat: float
    lon: float
    level: str  # 'tinh' or 'xa'


@router.post("/search_geometry")
def search_geometry(req: SearchGeometryRequest):
    """Search which polygon (province or commune) contains the given lat/lon.
    Request body: { "lat": <float>, "lon": <float>, "level": "tinh"|"xa" }
    """
    level = req.level.lower()
    if level not in ("tinh", "xa"):
        raise HTTPException(status_code=400, detail="'level' must be 'tinh' or 'xa'")

    if level == "tinh":
        if gdf_tinh is None:
            raise HTTPException(status_code=500, detail=f"failed to load geotinh.geojson: {_load_errors.get('tinh')}")
        gdf = gdf_tinh
    else:
        if gdf_xa is None:
            raise HTTPException(status_code=500, detail=f"failed to load geoxa.geojson: {_load_errors.get('xa')}")
        gdf = gdf_xa

    point = Point(req.lon, req.lat)

    # Use spatial index for performance when available; fallback to scanning all geometries.
    try:
        sindex = getattr(gdf, 'sindex', None)
        if sindex is not None:
            candidate_idx = list(gdf.sindex.intersection(point.bounds))
            candidates = gdf.iloc[candidate_idx]
        else:
            candidates = gdf
    except Exception:
        candidates = gdf

    # contains may fail if geometries/CRS mismatched; assume inputs are lon/lat and geojson is in degrees
    matched = candidates[candidates.contains(point)]

    if matched.empty:
        return {"level": level, "found": False, "properties": None, "geometry": None}

    row = matched.iloc[0]
    # Return all properties (except geometry) and geometry as GeoJSON
    props = row.drop(labels='geometry').to_dict()
    geom_geojson = mapping(row.geometry)

    return {"level": level, "found": True, "properties": props, "geometry": geom_geojson}

