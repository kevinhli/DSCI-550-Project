import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import contextily as ctx

HEATMAPS_DIR = Path(__file__).resolve().parent.parent / "results" / "heatmaps"
HEATMAPS_DIR.mkdir(parents=True, exist_ok=True)

def generate_overall_heatmap(df, filename="citations_heatmap.png", title="Parking Citations Heatmap"):
    print("Generating heatmap")

    if len(df) == 0:
        print("Empty")
        return

    df['loc_lat'] = df['loc_lat'].round(3)
    df['loc_long'] = df['loc_long'].round(3)

    grouped = df.groupby(['loc_lat', 'loc_long']).size().reset_index(name='frequency')
    print(f"Number of grouped points: {len(grouped)}")

    gdf = gpd.GeoDataFrame(grouped, geometry=gpd.points_from_xy(grouped['loc_long'], grouped['loc_lat']))
    gdf.set_crs("EPSG:4326", inplace=True)
    gdf.to_crs(epsg=3857, inplace=True)

    if gdf.empty:
        print("Nothing to plot")
        return

    fig, ax = plt.subplots(figsize=(12, 10))
    gdf.plot(
        ax=ax,
        alpha=0.6,
        markersize=gdf['frequency'] * 10,
        column='frequency',
        cmap='Reds',
        legend=True
    )
    plt.title(title)

    try:
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf.crs.to_string(), zoom=10, alpha=0.8)
    except Exception as e:
        print(f"Basemap loading failed: {e}")

    xlim = ax.get_xlim()
    ax.set_xlim(left=xlim[0], right=-1.134e7)

    plt.savefig(HEATMAPS_DIR / filename, dpi=300)
    plt.close()
    print(f"Heatmap saved as {filename}")
