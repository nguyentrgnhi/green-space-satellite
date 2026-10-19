"""Collect monthly green area and cloud cover for a region from Google Earth Engine.

    export EE_PROJECT=your-google-cloud-project      # an Earth Engine enabled project
    python src/collect_green_area.py --region saigon_outskirts --satellite sentinel2 --out data/raw/

For every Landsat-8 or Sentinel-2 image in each month it computes NDVI, counts the pixels with
NDVI > 0.3 as "green" and converts them to square kilometres, and records the image's cloud cover.
Requires `earthengine-api` and a one-time `earthengine authenticate`.

Note: the original study used the Landsat Collection 1 data set below, which Google has since
deprecated. To rerun it today, switch to Collection 2 (LANDSAT/LC08/C02/T1_L2, bands SR_B5 / SR_B4).
"""
import argparse
import calendar
import os
from pathlib import Path

import ee
import pandas as pd

from regions import REGIONS

SATELLITES = {
    "landsat8": {"label": "Landsat-8", "collection": "LANDSAT/LC08/C01/T1_SR", "nir": "B5", "red": "B4",
                 "cloud_property": "CLOUD_COVER", "scale": 30},
    "sentinel2": {"label": "Sentinel-2", "collection": "COPERNICUS/S2_HARMONIZED", "nir": "B8", "red": "B4",
                  "cloud_property": "CLOUDY_PIXEL_PERCENTAGE", "scale": 10},
}
NDVI_GREEN_THRESHOLD = 0.3


def collect(region_name, satellite, start_year, end_year):
    sat = SATELLITES[satellite]
    boundary = ee.Geometry.Polygon(REGIONS[region_name])

    def describe(image):
        ndvi = image.normalizedDifference([sat["nir"], sat["red"]]).rename("NDVI")
        green_km2 = ndvi.gt(NDVI_GREEN_THRESHOLD).multiply(ee.Image.pixelArea()).divide(1e6)
        area = green_km2.reduceRegion(reducer=ee.Reducer.sum(), geometry=boundary, scale=sat["scale"]).get("NDVI")
        return ee.Feature(None, {"date": image.date().format("YYYY-MM-dd"),
                                 "cloudCover": image.get(sat["cloud_property"]), "greenArea": area})

    rows = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            last_day = calendar.monthrange(year, month)[1]
            images = (ee.ImageCollection(sat["collection"])
                      .filterBounds(boundary)
                      .filterDate(f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}"))
            if satellite == "sentinel2":
                images = images.filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", 100))
            for feature in images.map(describe).getInfo()["features"]:
                p = feature["properties"]
                rows.append({"city": region_name, "month": month, "year": year, "date": p["date"],
                             "cloud cover percentage": p["cloudCover"], "green area": p["greenArea"],
                             "Satellite": sat["label"]})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--region", choices=sorted(REGIONS), required=True)
    parser.add_argument("--satellite", choices=sorted(SATELLITES), required=True)
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2021)
    parser.add_argument("--out", default="data/raw")
    args = parser.parse_args()

    ee.Initialize(project=os.environ["EE_PROJECT"])
    df = collect(args.region, args.satellite, args.start_year, args.end_year)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{args.region}_{args.satellite}.csv"
    df.to_csv(path, index=False)
    print(f"{len(df)} images -> {path}")


if __name__ == "__main__":
    main()
