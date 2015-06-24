import plotly.plotly as py
import os
import json
import time
import mcp3008
import datetime

with open('./config.json') as config_file:
    plotly_user_config = json.load(config_file)

py.sign_in(plotly_user_config["plotly_username"], plotly_user_config["plotly_api_key"])

url = py.plot([
    {
        'x': [], 'y': [], 'type': 'scatter',
        'stream': {
            'token': plotly_user_config['plotly_streaming_tokens'][0],
            'maxpoints': 200
        }
    }], filename='Bodenfeuchtigkeit Test')

print "View your streaming graph here: ", url

stream = py.Stream(plotly_user_config['plotly_streaming_tokens'][0])
stream.open()

# ANSI escape codes
PREVIOUS_LINE="\x1b[1F"
RED_BACK="\x1b[41;37m"
GREEN_BACK="\x1b[42;30m"
YELLOW_BACK="\x1b[43;30m"
RESET="\x1b[0m"
readings = []

delta = datetime.timedelta(minutes=1)
next_time = datetime.datetime.now()+delta
next_water = datetime.datetime.now()

#the main sensor reading and plotting loop
while True:
    dt = datetime.datetime.now()
    while dt < next_time:
       n = 100-mcp3008.read_pct(5)
       if n>15 and n<85:
		if len(readings) >= 1000:
            		del readings[0];
       		readings.append(n)
       dt = datetime.datetime.now();
    else:
        # Take the average from the readings list to smooth the graph a little
        m = round(2*((sum(readings)/float(len(readings)))),1)             
        readings = []
        # write the data to plotly
        stream.write({'x': datetime.datetime.now(), 'y': m})
        if m < 25:
    		background = RED_BACK
	elif m < 65:
    		background = YELLOW_BACK
	else:
    		background = GREEN_BACK
	print PREVIOUS_LINE + background + "Moisture level: {:>5} ".format(m) + RESET
	dt = datetime.datetime.now();
	next_time = dt + delta;
    	if m<60:
            if dt > next_water:
            	bashCommand = "sudo pilight-send -p mumbi -s 19 -u 1 -t"
                os.system(bashCommand)
            	time.sleep(10)
            	bashCommand = "sudo pilight-send -p mumbi -s 19 -u 1 -f"
                os.system(bashCommand)
            	dt = datetime.datetime.now();
            	next_water = dt + 10* delta
            	next_time = dt + delta

