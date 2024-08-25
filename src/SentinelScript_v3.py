import os
import tarfile
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from sentinelhub import SHConfig
import requests
from datetime import datetime, timedelta
import config

# Configuration setup
sh_config = SHConfig()
sh_config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
sh_config.sh_base_url = "https://sh.dataspace.copernicus.eu"

def getauth_token():
    client = BackendApplicationClient(client_id=config.CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=sh_config.sh_token_url,
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
    )
    return oauth

oauth = getauth_token()

# Define the bounding box
min_lon = 56.266878
max_lon = 56.587478
min_lat = 26.475284
max_lat = 26.762784

# Number of divisions in each direction (6x6 grid)
num_divisions = 10

# Calculate step sizes for each grid cell
lon_step = (max_lon - min_lon) / num_divisions
lat_step = (max_lat - min_lat) / num_divisions

# Create the grid and store the bounding boxes
bounding_boxes = []
for i in range(num_divisions):
    for j in range(num_divisions):
        lon1 = min_lon + i * lon_step
        lon2 = min_lon + (i + 1) * lon_step
        lat1 = min_lat + j * lat_step
        lat2 = min_lat + (j + 1) * lat_step
        
        bbox = [
            lon1,
            lat1,
            lon2,
            lat2
        ]
        bounding_boxes.append(bbox)

# Function to generate time slots for each week from 2018 to now
def generate_time_slots(start_year, end_year):
    time_slots = []
    current_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 1, 1)
    
    # Skip the first week .. after token issue fix
    current_date += timedelta(days=7)
    
    while current_date < end_date:
        start_slot = current_date.strftime("%Y-%m-%d")
        end_slot = (current_date + timedelta(days=6)).strftime("%Y-%m-%d")
        time_slots.append((start_slot, end_slot))
        current_date += timedelta(days=7)
    
    return time_slots

# Generate time slots from 2018 to now
slots = generate_time_slots(2018, 2024)

def get_request(slot, bbox, output_dir):
    corrected_request = {
        "input": {
            "bounds": {
                "bbox": bbox
            },
            "data": [
                {
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{slot[0]}T00:00:00Z",
                            "to": f"{slot[1]}T23:59:59Z"
                        },
                        "maxCloudCoverage": 20
                    },
                    "processing": {
                        "harmonizeValues": True
                    },
                    "type": "sentinel-2-l2a"
                }
            ]
        },
        "output": {
            "width": 2048,
            "height": 2056,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/png"
                    }
                }
            ]
        },
        "evalscript": '''
        //VERSION=3

        let minVal = 0.0;
        let maxVal = 0.4;

        let viz = new HighlightCompressVisualizer(minVal, maxVal);

        function evaluatePixel(samples) {
            let val = [samples.B08, samples.B04, samples.B03];
            val = viz.processList(val);
            val.push(samples.dataMask);
            return val;
        }

        function setup() {
          return {
            input: [{
              bands: [
                "B03",
                "B04",
                "B08",
                "dataMask"
              ]
            }],
            output: {
              bands: 4
            }
          };
        }
        '''
    }

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    response = oauth.post(url, json=corrected_request, headers={"Accept": "application/tar"})
    
    
    if response.status_code == 200 and response.content:
        # Generate a unique filename based on slot and bbox
        unique_filename = f"image_{slot[0]}_{bbox[0]:.6f}_{bbox[1]:.6f}.png"
        tar_filename = f"tarfile_strait_{slot[0]}_{bbox[0]:.6f}_{bbox[1]:.6f}.tar"
        
        with open(tar_filename, "wb") as tar_file:
            tar_file.write(response.content)

        with tarfile.open(tar_filename) as file:
            # Extract the content and rename the file
            for member in file.getmembers():
                if member.name == 'default.png':
                    member.name = unique_filename
                    file.extract(member, output_dir)

        os.remove(tar_filename)  # Remove the tar file after extraction
        print(f"Image saved as {unique_filename} for slot {slot[0]} - {slot[1]} and bbox {bbox}")
        return True
    else:
        print(f"Failed to fetch data for slot {slot[0]} - {slot[1]} and bbox {bbox}. Status Code: {response.status_code}")
        try:
            error_message = response.json()
            print(f"Error Message: {error_message}")
        except:
            print(f"Response Content: {response.content}")
        return False

# Create directories and loop through each time slot and bounding box
base_output_dir = "./strait_images"

for slot in slots:
    year = slot[0][:4]
    week_number = datetime.strptime(slot[0], "%Y-%m-%d").isocalendar()[1]
    output_dir = os.path.join(base_output_dir, year, f"week_{week_number:02d}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a new token for each week
    oauth = getauth_token()
    
    for bbox in bounding_boxes:
        try:
            get_request(slot, bbox, output_dir)
        except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
            # If token expires during a week, refresh it and retry
            oauth = getauth_token()
            get_request(slot, bbox, output_dir)

