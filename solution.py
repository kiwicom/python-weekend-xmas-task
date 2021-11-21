import csv
import datetime as dt
import json

from argparse import ArgumentParser
from copy import deepcopy


class TripFinder:
    def __init__(self) -> None:
        # Datetime format
        self._datetime_format = '%Y-%m-%dT%H:%M:%S'

        # Read command line arguments
        cmd_line_args = self._command_line_argumnet_parser()
        self.csv_file_name = cmd_line_args['csv_file_name']
        self.trip_origin = cmd_line_args['trip_origin']
        self.trip_destination = cmd_line_args['trip_destination']
        self.bags = cmd_line_args['bags']
        self.stops = cmd_line_args['stops']
        self.return_trip = cmd_line_args['return_trip']

        # Read csv file with flights
        self.flights = self._csv_input_reader()

        # Store (semi)results
        self.trips = []
        self.results = []

    def _command_line_argumnet_parser(self) -> dict:
        """
        Parse command line arguments.

        Example:
        --------
        python -m solution example/example0.csv RFZ WIW --bags=1 --stops=1 --return
        """

        parser = ArgumentParser(description='Process command line params')
        parser.add_argument('csv_file_name', help='Name of the input csv file')
        parser.add_argument('trip_origin', help='Trip origin')
        parser.add_argument('trip_destination', help='Trip destination')
        parser.add_argument(
            '--bags',
            type=int,
            default=0,
            required=False,
            help='Number of bags',
        )
        parser.add_argument(
            '--stops',
            type=int,
            default=0,
            required=False,
            help='Number of stops',
        )
        parser.add_argument(
            '--return',
            action='store_true',
            required=False,
            help='Return trip',
            dest='return_trip',
        )
        args = parser.parse_args()
        return vars(args)

    def _csv_input_reader(self) -> list:
        """
        Read csv input file and store it in list `flights`.
        """

        flights = []
        with open(self.csv_file_name, 'r') as csv_file:
            # Set reader
            csv_reader = csv.reader(csv_file)

            # Loop over the header line
            next(csv_reader)

            # Loop over the file
            for row in csv_reader:
                flight_no = row[0]
                origin = row[1]
                destination = row[2]
                departure = dt.datetime.strptime(row[3], self._datetime_format)
                arrival = dt.datetime.strptime(row[4], self._datetime_format)
                base_price = float(row[5])
                bag_price = float(row[6])
                bags_allowed = int(row[7])

                flights.append(
                    {
                        'flight_no': flight_no,
                        'origin': origin,
                        'destination': destination,
                        'departure': departure,
                        'arrival': arrival,
                        'base_price': base_price,
                        'bag_price': bag_price,
                        'bags_allowed': bags_allowed,
                    }
                )

        return flights

    def find_available_trips(self, trip: list = []) -> None:
        """
        Find all available trips from `trip_origin` to `trip_destination`.
        """

        for flight in self.flights:
            if trip == []:
                if flight['origin'] == self.trip_origin:
                    # If trip itinerary is empty and flight origin equals trip origin
                    self.find_available_trips(
                        [
                            flight,
                        ]
                    )

            elif trip[-1]['destination'] == self.trip_destination:
                self.trips.append(deepcopy(trip))
                break

            elif (
                len(trip) - 1 < self.stops
                and trip[-1]['destination'] == flight['origin']
                and 60 * 60
                <= (flight['departure'] - trip[-1]['arrival']).total_seconds()
                <= 6 * 60 * 60
            ):
                self.find_available_trips(
                    trip
                    + [
                        flight,
                    ]
                )

    def format_results(self) -> None:
        """
        Compute summary statistics, format result in predefined form and sort results on `total_price`.
        """

        for trip in self.trips:

            # Compute summary statistics
            total_base_price = 0
            total_bag_price = 0
            max_bags_allowed = 99
            total_travel_time = str(trip[-1]['arrival'] - trip[0]['departure'])

            for flight in trip:
                total_base_price += flight['base_price']
                total_bag_price += flight['bag_price']
                max_bags_allowed = (
                    flight['bags_allowed']
                    if flight['bags_allowed'] < max_bags_allowed
                    else max_bags_allowed
                )
                flight['departure'] = flight['departure'].strftime(
                    self._datetime_format
                )
                flight['arrival'] = flight['arrival'].strftime(
                    self._datetime_format
                )

            total_price = total_base_price + self.bags * total_bag_price

            # Format result
            result = {
                'flights': trip,
                'bags_allowed': max_bags_allowed,
                'bags_count': self.bags,
                'destination': self.trip_destination,
                'origin': self.trip_origin,
                'total_price': total_price,
                'travel_time': total_travel_time,
            }

            # Check number of allowed bags
            if self.bags <= max_bags_allowed:
                self.results.append(result)

        #  Sort results by `total_price`
        self.results = sorted(
            self.results, key=lambda result: result['total_price']
        )


tf = TripFinder()
tf.find_available_trips()
tf.format_results()

# Print results
print(json.dumps(tf.results, indent=4))
