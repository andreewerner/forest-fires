import pandas as pd
import pickle
import psycopg2

def merge_df():
	'''
	Input: None
	Output: PSQL Data Table
	'''
	conn = psycopg2.connect('dbname=forest_fires')
	cursor = conn.cursor()

	cursor.execute('''CREATE TABLE forest_st_cnty AS
					 (SELECT points.*, polys.fire_name
					 FROM detected_fires_2013 as points
							INNER JOIN daily_fire_shapefiles_2013 as polys
					 ON points.date = polys.date_ 
					 	AND ST_WITHIN(points.wkb_geometry, polys.wkb_geometry));
					''')

	conn.commit()
	conn.close()


def format_df(df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame

	In the years 2008 and prior, the data is formatted slightly differently than later years. The 
	Fire_ and Fire_ID variables from later years are named differently, as are the LAT and LONG 
	variables. For these, we simply need to change names. For the TEMP variable from years 2009+, we need to 
	use the T21 from the years prior to 2008, and for the JULIAN varible in years 2009+, we need to parse
	part of the JDATE variable. 
	'''

	df = df.rename(columns={'MCD14ML_': 'FIRE_', 'MCD14ML_ID': 'FIRE_ID', 'WGS84LAT': 'LAT', 'WGS84LONG': 'LONG', 
							'T21': 'TEMP', 'UTC': 'GMT', 'SATELLITE': 'SAT_SRC', 'CONFIDENCE': 'CONF'})
	df['JULIAN'] = df['JDATE'].apply(lambda x: int(str(x)[-3:]))
	df = df.drop(['T31', 'JDATE'], axis=1)

	return df

def pickle_df_sf(year, df): 
	'''
	Input: Integer, Pandas DataFrame
	Ouput: Pickled file of DataFrame
	'''

	with open('../data/pickled_data/MODIS/' + 'df_' + str(year) + '.pkl', 'w+') as f: 
		pickle.dump(df, f)

if __name__ == '__main__': 
	merge_df()