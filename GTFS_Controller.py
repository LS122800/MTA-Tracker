import requests
from google.transit.gtfs_realtime_pb2 import FeedMessage, FeedHeader, FeedEntity
import time
from typing import Optional

class MTAGTFSController:
    def __init__(self, api_key: str):
        """
        Initialize the MTA GTFS Controller
        
        Args:
            api_key (str): Your MTA API key
        """
        self.api_key = api_key
        self.base_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g"
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/x-protobuf"
        }

    def fetch_realtime_data(self) -> Optional[gtfs_realtime_pb2.FeedMessage]:
        """
        Fetch real-time GTFS data from the MTA API
        
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
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error parsing feed: {e}")
            return None

    def process_feed(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        """
        Process and display the feed data
        
        Args:
            feed (FeedMessage): The parsed GTFS feed message
        """
        if not feed:
            print("No feed data to process")
            return

        print(f"Feed timestamp: {time.ctime(feed.header.timestamp)}")
        
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                self._process_trip_update(entity.trip_update)
            elif entity.HasField('vehicle'):
                self._process_vehicle_position(entity.vehicle)
            elif entity.HasField('alert'):
                self._process_alert(entity.alert)

    def _process_trip_update(self, trip_update) -> None:
        """Process trip update information"""
        trip = trip_update.trip
        print(f"\nTrip ID: {trip.trip_id}")
        print(f"Route ID: {trip.route_id}")
        
        for stop_time_update in trip_update.stop_time_update:
            arrival = time.ctime(stop_time_update.arrival.time) if stop_time_update.HasField('arrival') else 'N/A'
            departure = time.ctime(stop_time_update.departure.time) if stop_time_update.HasField('departure') else 'N/A'
            print(f"Stop ID: {stop_time_update.stop_id}")
            print(f"  Arrival: {arrival}")
            print(f"  Departure: {departure}")

    def _process_vehicle_position(self, vehicle) -> None:
        """Process vehicle position information"""
        print(f"\nVehicle Position:")
        print(f"Trip ID: {vehicle.trip.trip_id}")
        print(f"Current Stop ID: {vehicle.stop_id}")
        print(f"Current Status: {vehicle.current_status}")
        if vehicle.HasField('position'):
            print(f"Position: Lat {vehicle.position.latitude}, Lon {vehicle.position.longitude}")

    def _process_alert(self, alert) -> None:
        """Process alert information"""
        print("\nAlert:")
        for text in alert.header_text.translation:
            print(f"Header: {text.text}")
        for text in alert.description_text.translation:
            print(f"Description: {text.text}")


def main():
    # Replace with your actual API key
    API_KEY = "YOUR_API_KEY_HERE"
    
    # Initialize the controller
    controller = MTAGTFSController(API_KEY)
    
    # Fetch and process the data
    feed = controller.fetch_realtime_data()
    if feed:
        controller.process_feed(feed)
    else:
        print("Failed to fetch GTFS data")

if __name__ == "__main__":
    main()
