import requests
import gtfs_realtime_pb2
import time
from typing import Optional
from station_mapping import StationMapping

class MTAGTFSController:
    def __init__(self):
        """
        Initialize the MTA GTFS Controller for the G line
        """
        self.base_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g"
        self.headers = {
            "Accept": "application/x-protobuf"
        }
        # Initialize and load station mapping
        self.station_mapping = StationMapping()
        self.station_mapping.download_and_process_gtfs()

    def fetch_realtime_data(self) -> Optional[gtfs_realtime_pb2.FeedMessage]:
        """
        Fetch real-time GTFS data from the MTA API for the G line
        
        Returns:
            FeedMessage: Parsed protobuf message containing real-time transit data
            None: If there was an error fetching or parsing the data
        """
        try:
            # Make the API request
            response = requests.get(self.base_url, headers=self.headers)
            
            # Check if request was successful
            if response.status_code == 200:
                # Parse the protobuf message
                feed = gtfs_realtime_pb2.FeedMessage()
                feed.ParseFromString(response.content)
                return feed
            else:
                print(f"Error: Received status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error parsing feed: {e}")
            return None

    def display_train_positions(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        """
        Display current train positions from the feed
        
        Args:
            feed (FeedMessage): The parsed GTFS feed message
        """
        if not feed:
            print("No feed data to process")
            return

        print(f"\nFeed timestamp: {time.ctime(feed.header.timestamp)}")
        
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicle = entity.vehicle
                trip_id = vehicle.trip.trip_id if vehicle.HasField('trip') else 'N/A'
                stop_id = vehicle.stop_id if vehicle.HasField('stop_id') else 'N/A'
                
                status = vehicle.current_status
                status_mapping = {
                    0: "approaching",
                    1: "stopped at",
                    2: "en route to"
                }
                status_str = status_mapping.get(status, "location undetermined")
                
                station_name = self.station_mapping.get_station_name(stop_id)
                print(f"\nTrain ID: {trip_id}")
                print(f"Status: {status_str} {station_name}")
                print(f"Stop ID: {stop_id}")

def main():
    # Initialize the controller
    controller = MTAGTFSController()
    
    # Fetch and display the data
    feed = controller.fetch_realtime_data()
    if feed:
        controller.display_train_positions(feed)
    else:
        print("Failed to fetch GTFS data")

if __name__ == "__main__":
    main()
