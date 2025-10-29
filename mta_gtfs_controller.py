import requests
import gtfs_realtime_pb2
import time
from typing import Optional

class MTAGTFSController:
    def __init__(self):
        """
        Initialize the MTA GTFS Controller for the G line
        """
        self.base_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g"
        self.headers = {
            "Accept": "application/x-protobuf"
        }

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
        
    def fetch_subway_status_data(self) -> Optional[gtfs_realtime_pb2.FeedMessage]:
        """
        Fetch real-time subway status data from the MTA API
        
        Returns:
            FeedMessage: Parsed protobuf message containing subway status data
            None: If there was an error fetching or parsing the data
        """
        status_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"
        try:
            # Make the API request
            response = requests.get(status_url, headers=self.headers)
            
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
                
                position_info = ''
                if vehicle.HasField('position'):
                    pos = vehicle.position
                    position_info = f"Lat: {pos.latitude:.4f}, Lon: {pos.longitude:.4f}"
                
                status = vehicle.current_status
                status_mapping = {
                    0: "INCOMING_AT",
                    1: "STOPPED_AT",
                    2: "IN_TRANSIT_TO"
                }
                status_str = status_mapping.get(status, "UNKNOWN")
                
                print(f"\nTrain ID: {trip_id}")
                print(f"Stop ID: {stop_id}")
                print(f"Status: {status_str}")
                if position_info:
                    print(f"Position: {position_info}")

    def display_status_alerts(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        """
        Display current subway status alerts from the feed
        
        Args:
            feed (FeedMessage): The parsed GTFS feed message
        """
        if not feed:
            print("No status feed data to process")
            return

        print(f"\nStatus Feed timestamp: {time.ctime(feed.header.timestamp)}")
        
        for entity in feed.entity:
            if entity.HasField('alert'):
                alert = entity.alert
                print("\n--- Subway Alert ---")
                for description in alert.description_text.translation:
                    print(f"Description: {description.text}")
                for header in alert.header_text.translation:
                    print(f"Header: {header.text}")
                print("--------------------")



        

def main():
    # Initialize the controller
    controller = MTAGTFSController()
    
    # # Fetch and display the data
    # feed = controller.fetch_realtime_data()
    # if feed:
    #     controller.display_train_positions(feed)
    # else:
    #     print("Failed to fetch GTFS data")

    # Fetch and display subway status alerts
    status_feed = controller.fetch_subway_status_data()
    if status_feed:
        controller.display_status_alerts(status_feed)
    else:
        print("Failed to fetch subway status data")

if __name__ == "__main__":
    main()
