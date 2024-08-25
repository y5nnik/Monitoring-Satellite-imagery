import json

# Define the bounding box
min_lon = 56.266878
max_lon = 56.587478
min_lat = 26.475284
max_lat = 26.762784

# Number of divisions in each direction
num_divisions = 10

# Calculate step sizes for each grid cell
lon_step = (max_lon - min_lon) / num_divisions
lat_step = (max_lat - min_lat) / num_divisions

# Create the grid
grid_coordinates = []
for i in range(num_divisions):
    for j in range(num_divisions):
        # Calculate the coordinates for each grid cell
        lon1 = min_lon + i * lon_step
        lon2 = min_lon + (i + 1) * lon_step
        lat1 = min_lat + j * lat_step
        lat2 = min_lat + (j + 1) * lat_step
        
        # Define the polygon for the grid cell
        polygon = [
            [
                [lon1, lat1],
                [lon2, lat1],
                [lon2, lat2],
                [lon1, lat2],
                [lon1, lat1]
            ]
        ]
        
        # Add the polygon to the list
        grid_coordinates.append(polygon)

# Define the final MultiPolygon structure
grid_json = {
    "type": "MultiPolygon",
    "coordinates": grid_coordinates
}

# save the JSON structure in txt file
with open('grid_json.txt', 'w') as f:
    f.write(json.dumps(grid_json, indent=2))
