from sgp4.api import Satrec
from math import (cos, sin, pi, floor,sqrt, atan2,atan, fabs, asin)
from numpy import (zeros,meshgrid,arange,array,moveaxis)
from datetime import datetime
import time

def gstime(jdut1):
    twopi = 2*pi
    deg2rad = pi/180
    temp = 0.0
    tutl = 0.0
    tut1 = (jdut1 - 2451545.0) / 36525.0
    temp = -6.2e-6* tut1 * tut1 * tut1 + 0.093104 * tut1 * tut1 + (876600.0*3600 + 8640184.812866) * tut1 + 67310.54841  # sec
    temp = floatmod(temp * deg2rad / 240.0, twopi) #360/86400 = 1/240, to deg, to rad
    temp = floatmod(temp * deg2rad / 240.0, twopi) #360/86400 = 1/240, to deg, to rad
     #------------------------ check quadrants ---------------------
    if (temp < 0.0):
        temp += twopi

    return temp # end gstime

def floatmod(a,b):
    return (a - b * floor(a / b))

pm = zeros((3,3))
def polarm(jdut1, pm):
    MJD=0 #Julian Date - 2,400,000.5 days
    A =0.0
    C = 0.0
    xp = 0.0 
    yp = 0.0 #Polar motion coefficient in radians    
    #Predict polar motion coefficients using IERS Bulletin - A (Vol. XXVIII No. 030)
    MJD = jdut1 - 2400000.5
    A = 2 * pi * (MJD - 57226) / 365.25
    C = 2 * pi * (MJD - 57226) / 435    
    xp = (0.1033 + 0.0494*cos(A) + 0.0482*sin(A) + 0.0297*cos(C) + 0.0307*sin(C)) * 4.84813681e-6
    yp = (0.3498 + 0.0441*cos(A) - 0.0393*sin(A) + 0.0307*cos(C) - 0.0297*sin(C)) * 4.84813681e-6    
    pm[0][0] = cos(xp)
    pm[0][1] = 0.0
    pm[0][2] = -sin(xp)
    pm[1][0] = sin(xp) * sin(yp)
    pm[1][1] = cos(yp)
    pm[1][2] = cos(xp) * sin(yp)
    pm[2][0] = sin(xp) * cos(yp)
    pm[2][1] = -sin(yp)
    pm[2][2] = cos(xp) * cos(yp)
    return pm
#TEME to ECEF
rteme = zeros(3)
recef = zeros(3)
def teme2ecef(rteme, jdut1):

    gmst = 0
    st = zeros((3,3))
    rpef = zeros(3)
    vpef = zeros(3)
    pm = zeros((3,3))
    gmst = gstime(jdut1)
    
    #st is the pef - tod matrix
    st[0][0] = cos(gmst)
    st[0][1] = -sin(gmst)
    st[0][2] = 0.0
    st[1][0] = sin(gmst)
    st[1][1] = cos(gmst)
    st[1][2] = 0.0
    st[2][0] = 0.0
    st[2][1] = 0.0
    st[2][2] = 1.0
    
    #Get pseudo earth fixed position vector by multiplying the inverse pef-tod matrix by rteme
    rpef[0] = st[0][0] * rteme[0] + st[1][0] * rteme[1] + st[2][0] * rteme[2]
    rpef[1] = st[0][1] * rteme[0] + st[1][1] * rteme[1] + st[2][1] * rteme[2]
    rpef[2] = st[0][2] * rteme[0] + st[1][2] * rteme[1] + st[2][2] * rteme[2]
    
    #Get polar motion vector
    polarm(jdut1, pm)
    
    #ECEF postion vector is the inverse of the polar motion vector multiplied by rpef
    recef[0] = pm[0][0] * rpef[0] + pm[1][0] * rpef[1] + pm[2][0] * rpef[2]
    recef[1] = pm[0][1] * rpef[0] + pm[1][1] * rpef[1] + pm[2][1] * rpef[2]
    recef[2] = pm[0][2] * rpef[0] + pm[1][2] * rpef[1] + pm[2][2] * rpef[2]
    
    #Earth's angular rotation vector (omega)
    #Note: I don't have a good source for LOD. Historically it has been on the order of 2 ms so I'm just using that as a constant. The effect is very small.
    #omegaearth[0] = 0.0
    #omegaearth[1] = 0.0
    #omegaearth[2] = 7.29211514670698e-05 * (1.0  - 0.0015563/86400.0)
    
    #Pseudo Earth Fixed velocity vector is st'*vteme - omegaearth X rpef
    #vpef[0] = st[0][0] * vteme[0] + st[1][0] * vteme[1] + st[2][0] * vteme[2] - (omegaearth[1]*rpef[2] - omegaearth[2]*rpef[1])
    #vpef[1] = st[0][1] * vteme[0] + st[1][1] * vteme[1] + st[2][1] * vteme[2] - (omegaearth[2]*rpef[0] - omegaearth[0]*rpef[2])
    #vpef[2] = st[0][2] * vteme[0] + st[1][2] * vteme[1] + st[2][2] * vteme[2] - (omegaearth[0]*rpef[1] - omegaearth[1]*rpef[0])
    
    #ECEF velocty vector is the inverse of the polar motion vector multiplied by vpef
    #vecef[0] = pm[0][0] * vpef[0] + pm[1][0] * vpef[1] + pm[2][0] * vpef[2]
    #vecef[1] = pm[0][1] * vpef[0] + pm[1][1] * vpef[1] + pm[2][1] * vpef[2]
    #vecef[2] = pm[0][2] * vpef[0] + pm[1][2] * vpef[1] + pm[2][2] * vpef[2]
    return recef

def magnitude(vector):
    return sqrt(sum(pow(element, 2) for element in vector))

def sgn( x):
    if (x < 0.0):
        return -1.0
    else:
        return 1.0
def ijk2ll(r):
    latlongh = zeros(3)
    twopi = 2.0*pi
    small = 0.00000001        #small value for tolerances
    re = 6378.137               #radius of earth in km
    eesqrd = 0.006694385000     #eccentricity of earth sqrd
    magr =0.0
    temp =0.0
    rtasc = 0.0
    magr = magnitude(r)
    temp = sqrt(r[0]*r[0] + r[1]*r[1])
    
    if(fabs(temp) < small):
        rtasc = sgn(r[2]) * pi * 0.5

    else:
        rtasc = atan2(r[1], r[0])
    
    latlongh[1] = rtasc
    
    if (fabs(latlongh[1]) >= pi):
        if (latlongh[1] < 0.0):
            latlongh[1] += twopi
        else:
            latlongh[1] -= twopi
    latlongh[0] = asin(r[2] / magr)
    
    #Iterate to find geodetic latitude
    i = 1
    olddelta = latlongh[0] + 10.0
    sintemp= 0.0
    c = 0
    while ( (fabs(olddelta - latlongh[0]) >= small) and (i < 10) ):
        olddelta = latlongh[0]
        sintemp = sin(latlongh[0])
        c = re / sqrt(1.0 - eesqrd*sintemp*sintemp)
        latlongh[0] = atan( (r[2] + c*eesqrd*sintemp) / temp )
        i+=1
    
    if (0.5*pi - fabs(latlongh[0]) > pi/180.0):
        latlongh[2] = (temp/cos(latlongh[0])) - c
    else:
        latlongh[2] = r[2]/sin(latlongh[0]) - c*(1.0 - eesqrd)
    return latlongh


def get_patch_coords(r_patch,c_patch):
    r_patch = r_patch//240
    c_patch = c_patch//180
    # assigned regular string date
    date_time = datetime.now() 

    # displaying unix timestamp after conversion
    unix_timestamp = time.mktime(date_time.timetuple())
    def getCurrentJulianFromUnix():
        return ( unix_timestamp / 86400.0 ) + 2440587.5

    tle_file = 'SAT.TLE'
    fp= open(tle_file, 'r')
    tle_data = [line.strip() for line in fp]
    platform_1 = Satrec.twoline2rv(tle_data[1], tle_data[2])
    fp.close()
    #need to convert regular time to julian
    jd, fr = getCurrentJulianFromUnix(), 0.0
    e, r, v = platform_1.sgp4(jd, fr)
    #convert TEME to ECEF
    recef = teme2ecef(r, jd )
    #convert ECEF to geodetic
    latlongh = ijk2ll(recef)
    latitude = latlongh[0] * 180/pi
    longitude =  (latlongh[1] * 180/pi)
    orb_height = latlongh[2]
    '''
    Image size  6480 by 4860 and tile size 240 by 180
        Assume satellite lat and long is center of frame
        Horizontal dist in patches to center of 1st patch is (6480/240)/2 = 13
        Vertical dist in patches to center of 1st patch  is (4860/180)/2 = 13
        H Distance per patch = 240*30 = 7200m
        V Distance per patch = 180*30 = 54000m
        Assume 111000m per latitude
        Assume 111321 per longitude
      '''
    lat_1st_patch = latitude - ((13.5*7200.0)/111000.0)
    long_1st_patch = longitude - ((13.5*5400.0)/111321.0)

    lat_last_patch = latitude + ((13.5*7200.0)/111000.0)
    long_last_patch = longitude + ((13.5*5400.0)/111321.0)

    lat_step = 7200.0/111000.0
    long_step = 5400.0/111321.0

    lats = arange(lat_1st_patch,lat_last_patch,lat_step)
    longs = arange(long_1st_patch,long_last_patch,long_step)
    coords = array(meshgrid(lats,longs,indexing='ij'))
    coords = moveaxis(coords, 0, 2) 

    return coords[:][r_patch][c_patch]
