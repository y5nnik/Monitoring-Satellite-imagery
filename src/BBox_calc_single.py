# Define the bounding box
min_lon = 56.266878
max_lon = 56.587478
min_lat = 26.475284
max_lat = 26.762784

# Number of divisions in each direction (6x6 grid)
num_divisions = 6

# Calculate step sizes for each grid cell
lon_step = (max_lon - min_lon) / num_divisions
lat_step = (max_lat - min_lat) / num_divisions

# Create the grid and store the bounding boxes
bounding_boxes = []
for i in range(num_divisions):
    for j in range(num_divisions):
        # Calculate the coordinates for each grid cell
        lon1 = min_lon + i * lon_step
        lon2 = min_lon + (i + 1) * lon_step
        lat1 = min_lat + j * lat_step
        lat2 = min_lat + (j + 1) * lat_step
        
        # Define the bounding box for the grid cell
        bbox = {
            "min_lon": lon1,
            "min_lat": lat1,
            "max_lon": lon2,
            "max_lat": lat2
        }
        
        # Add the bounding box to the list
        bounding_boxes.append(bbox)

# Print the list of bounding boxes
for index, bbox in enumerate(bounding_boxes):
    print(f"Bounding Box {index + 1}:")
    print(f"  Min Longitude: {bbox['min_lon']}")
    print(f"  Min Latitude: {bbox['min_lat']}")
    print(f"  Max Longitude: {bbox['max_lon']}")
    print(f"  Max Latitude: {bbox['max_lat']}")
    print()
