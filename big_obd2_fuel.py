import csv
import os

#TO GATHER
def gather():
    folder_path = "VED_DynamicData_Part1"
    vehicle_id = 399 #CHANGE THIS AND THE COMMENT WITH THE SMILEY FACE WHEN SWAPPING VEHICLES
    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r') as file:
            print(f"reading {filename}, searching for vehicle ID {vehicle_id}")
            csv_reader = csv.DictReader(file)
            data_list = []

            for row in csv_reader:
                try:
                    if int(row['VehId']) == vehicle_id:
                        data_list.append(row) 
                except (KeyError, ValueError):
                    continue
                    
        with open('vehicles_VED/vehicle4_id399.csv', 'a', newline='') as csvfile: # :) CHANGE FILENAME HERE
                fieldnames = ['DayNum', 'VehId', 'Trip', 'Timestamp(ms)', 'Latitude[deg]', 'Longitude[deg]', 'Vehicle Speed[km/h]', 'MAF[g/sec]', 'Engine RPM[RPM]', 'Absolute Load[%]', 'OAT[DegC]', 'Fuel Rate[L/hr]', 'Air Conditioning Power[kW]', 'Air Conditioning Power[Watts]', 'Heater Power[Watts]', 'HV Battery Current[A]', 'HV Battery SOC[%]', 'HV Battery Voltage[V]', 'Short Term Fuel Trim Bank 1[%]', 'Short Term Fuel Trim Bank 2[%]', 'Long Term Fuel Trim Bank 1[%]', 'Long Term Fuel Trim Bank 2[%]']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                #writer.writeheader() #writes fieldnames
                writer.writerows(data_list)
#gather()


#TO TAKE
def extraction():
    folder = "vehicles_VED"
   
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename), 'r') as file:
            print(f"reading {filename}")
            csv_reader = csv.DictReader(file)
                
            total_distance = 0
            idling_time = 0
            fuel_used = 0
            co2_emissions = 0
            fuel_density = 820 #grams | 750 for diesel, 820 for gasoline
            airfuel_ratio = 14.7 #14.5 for diesel, 14.7 for gasoline
                
            previous_timestamp = None
            previous_trip = None
            previous_date = None
            vehicle_id = None  # set in-loop
            
            for row in csv_reader:
                try:
                    maf = float(row['MAF[g/sec]'])
                    speed_kmh = int(row['Vehicle Speed[km/h]'])
                    timestamp = int(row['Timestamp(ms)'])
                    trip = int(row['Trip'])
                    date = float(row['DayNum'])
                    vehicle_id = int(row['VehId'])

                    #fuel flow (liter per hour)                        
                    fuel_flow_lph = (maf * 3600) / (airfuel_ratio * fuel_density)
                    co2_emissions += maf / airfuel_ratio

                    #new trip, reset counters
                    if previous_trip is not None and previous_trip != trip:
                        with open('vehicles_VED/features.txt', 'a') as f:
                            f.write(
                                f"Date: {previous_date} | Trip: {previous_trip} | Vehicle ID: {vehicle_id} "
                                f"| Total Distance: {total_distance:.3f} km | Total Time: {(previous_timestamp / 1000):.3f} secs "
                                f"| Total Idling Time: {idling_time:.3f} secs | Total Fuel Consumed: {fuel_used:.3f} L "
                                f"| Total CO2 Emissions: {co2_emissions:.3f} g\n"
                            )
                        total_distance = idling_time = fuel_used = co2_emissions = 0

                
                    if previous_timestamp is not None and previous_trip == trip:
                        time_delta_s = (timestamp - previous_timestamp) / 1000.0  # seconds
                        time_delta_hr = time_delta_s / 3600.0
                        
                        #idling
                        if speed_kmh == 0:
                            idling_time += time_delta_s
                            fuel_used += fuel_flow_lph * time_delta_hr
                        else:
                            #distance
                            speed_kms = speed_kmh / 3600.0
                            distance = speed_kms * time_delta_s
                            total_distance += distance

                            #fuel
                            #https://www.researchgate.net/publication/285614280_Assessing_the_impact_of_driving_behavior_on_instantaneous_fuel_consumption#pf4
                            #https://onlinelibrary.wiley.com/doi/full/10.1155/2020/9450178
                            fuel_per_km = fuel_flow_lph / speed_kmh
                            fuel_used += fuel_per_km * distance

                    previous_timestamp = timestamp
                    previous_trip = trip
                    previous_date = date

                except (KeyError, ValueError):
                    continue   
                   
extraction()

    