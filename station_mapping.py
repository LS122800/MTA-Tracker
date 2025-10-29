import requests
from typing import Dict

class StationMapping:
    def __init__(self):
        self.station_names: Dict[str, str] = {}
        
    def download_and_process_gtfs(self) -> None:
        """
        Downloads and processes the station data from NY Open Data API to create
        a mapping of stop_ids to station names
        """
        # URL for NY Open Data API endpoint
        api_url = "https://data.ny.gov/resource/39hk-dx4f.json"
        
        try:
            # Download the station data
            response = requests.get(api_url)
            if response.status_code == 200:
                stations = response.json()
                
                # Process each station
                for station in stations:
                    stop_id = station.get('gtfs_stop_id', '')
                    if stop_id:
                        # Get station info
                        station_name = station.get('stop_name', '')
                        borough = station.get('borough', '')
                        
                        if station_name:
                            # Store with borough info
                            full_name = f"{station_name} ({borough})" if borough else station_name
                            self.station_names[stop_id] = full_name
                            
                print(f"Successfully loaded {len(self.station_names)} station mappings")
            else:
                print(f"Failed to download GTFS data. Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error processing GTFS data: {e}")
    
    def get_station_name(self, stop_id: str) -> str:
        """
        Get the station name for a given stop ID
        
        Args:
            stop_id (str): The stop ID (e.g., 'G22S' or 'F27N')
            
        Returns:
            str: The station name or the original stop_id if not found
        """
        # Remove N/S suffix if present (as static GTFS might not include direction)
        base_stop_id = stop_id.rstrip('NS')
        return self.station_names.get(base_stop_id, stop_id)

def main():
    # Test the mapping
    mapping = StationMapping()
    mapping.download_and_process_gtfs()
    
    # Test some G line stop IDs
    test_stops = ['F27N', 'G22S', 'G28S', 'G32S']
    print("\nTesting stop ID to station name mapping:")
    for stop in test_stops:
        print(f"Stop ID: {stop} -> Station: {mapping.get_station_name(stop)}")
    
    # Print all available G line station mappings
    print("\nAll available G line station mappings:")
    g_stops = {k: v for k, v in mapping.station_names.items() if k.startswith('G')}
    for stop_id, name in sorted(g_stops.items()):
        print(f"{stop_id}: {name}")

if __name__ == "__main__":
    main()