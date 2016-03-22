from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import csv

star_type_dict = {'A':'c', 'B':'b', 'F':'r', 'K':'k', 'M':'m','G':'g'}
def read_file(fileName,map_object):
	with open(fileName, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar="'")
		counter = 0
		for line in reader:
			if counter != 0:
				longitude = convert_to_degrees(line[1].strip('"'),hours = True) # converts RA field to degrees (longitude)
				latitude = convert_to_degrees(line[2].strip('"')) # converts DECL field to degrees (latitude)
				x_coord,y_coord = map_object(longitude,latitude)
				
				if line[5] == "" or line[5] == None:
					map_object.plot(x_coord, y_coord, marker = ".", color='0.61')
				else:
					star_type = line[5].strip('"') # Analyzes the type attribute
					map_object.plot(x_coord, y_coord, marker = ".", color=star_type_dict[star_type[0]])
			counter += 1
	plt.show()

def convert_to_degrees(s,hours = False):
	x = s.split()
	angle = 0
	if hours:
		angle = angle + float(x[0])*15 # to convert from hours to degrees, multiply by 15
	else:
		angle = float(x[0])
	
	angle = angle + float(x[1])/float(60) # to convert from minutes to degrees, divide by 60
	angle = angle + float(x[2])/float(3600) # to convert from seconds to degrees, divide by 3600
	return angle


m = Basemap(projection='moll',lon_0=0,lat_0=0)
parallels = np.arange(-90.,90,30.)
m.drawparallels(parallels)
m.drawmeridians(np.arange(0.,360.,30.))
m.drawmapboundary()
read_file("sampled_data.csv",m)



