import mwapy
from mwapy import ephem_utils,metadata
import sys
import pyfits,numpy,math
import os,time,datetime
from optparse import OptionParser
import ephem
import logging as logger
import matplotlib
if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('agg')
import matplotlib.pyplot as pylab
import mwapy.pb.primarybeammap as primarybeammap
from mpl_toolkits.basemap import Basemap
from astropy.time import Time
from astropy.table import Table

# GBT Redis server
import redis
r = redis.Redis(host='localhost', port=6380, db=0)
gbtRA = r.hget('RA_DRV', 'VALUE')
gbtDEC = r.hget('DEC_DRV', 'VALUE')



figsize=8
dpi=300

def make_error(message, output, figsize=figsize, dpi=dpi):
    mwa=ephem_utils.Obs[ephem_utils.obscode['MWA']]
    fig=pylab.figure(figsize=(figsize,figsize),dpi=dpi)
    ax1=fig.add_subplot(1,1,1)
    
    ax1.cla()
    x=numpy.linspace(-1,1,301)
    y=numpy.linspace(-1,1,301)
    X,Y=numpy.meshgrid(x,y)
    R=numpy.sqrt(X**2+Y**2)
    R[R>=1]=numpy.nan
    R[R<1]=1
    ax1.imshow(R, origin='lower',
               extent=(-1,1,-1,1),
               cmap=pylab.cm.gray_r)
    ax1.text(0,0,
             'Error: %s' % message,
             fontsize=14,horizontalalignment='center')
    ax1.axis('off')
    fig.savefig(output,transparent=True,facecolor='none')
    return None




##################################################
def main():
    
    low=100
    high=10000
    cm=pylab.cm.gray
    
    usage="Usage: %prog [options]\n"
    usage+='\tMakes plot of MWA sky\n'
    parser = OptionParser(usage=usage,
                          version=mwapy.__version__ + ' ' + mwapy.__date__)
    parser.add_option('-o','--out',dest='out',default='/home/webdev/html/status/images/gbtmwasky.png',
                      help='Name for output [default=%default]')
    parser.add_option('-g','--gps',dest='gpstime',default=None,
                      type='int',
                      help='GPS time to process [default=most recent]')
    parser.add_option('--text',dest='text',default=False,
                      action='store_true',
                      help='Include text of target on plot?')
    parser.add_option('--notext',dest='text',default=False,
                      action='store_false',
                      help='Do not include text of target on plot?')

    (options, args) = parser.parse_args()

    basepath=os.path.join(os.path.split(mwapy.__file__)[0],'data')
    
    # read the constellation data
    try:
        fi=open(os.path.join(basepath,'constellationship.fab'))
    except:
        make_error('Could not find constellation data', options.out)
        sys.exit(1)
    Constellations={}
    for l in fi.readlines():
        d=l.split()
        name=d[0]
        n=int(d[1])
        data=numpy.array(map(int,d[2:]))
        Constellations[name]=[n,data]
    fi.close()      

    # read the HIP data on those stars
    try:
        HIP=Table.read(os.path.join(basepath,'HIP_constellations.dat'),
                       format='ascii.commented_header')
    except:
        make_error('Could not find star data', options.out)
        sys.exit(1)

    # Solar system bodies to plot
    # includes size in pixels and color
    Bodies={ephem.Sun: [120, 'y'],
            ephem.Jupiter: [60, 'c'],
            ephem.Moon: [120, 'w'],
            ephem.Mars: [30, 'r'],
            ephem.Venus: [40, 'c'],
            ephem.Saturn: [50, 'b'],
            }

    
    try:
        if options.gpstime is None:
            obsinfo=metadata.fetch_metadata(service='obs')
        else:
            obsinfo=metadata.fetch_metadata(gpstime=options.gpstime,
                                            service='obs')            
            if obsinfo['stoptime']==0:
                make_error('Unable to find observation info for observation %d', (options.gpstime,options.out))
                sys.exit(1)
    except:
        make_error('Unable to find observation info', options.out)
        sys.exit(1)

    try:    
        mwaobs=metadata.MWA_Observation(obsinfo)
    except:
        make_error('Unable to parse observation info', options.out)
        sys.exit(1)

    obstime=Time(mwaobs.observation_number, format='gps',
                 scale='utc')
    
    try:
        radio_image=os.path.join(basepath,'radio408.RaDec.fits')
        f=pyfits.open(radio_image)
    except:
        make_error('Cannot open Haslam image', options.out)
        sys.exit(1)

    skymap=f[0].data[0]
    ra=(f[0].header.get('CRVAL1')+(numpy.arange(1,skymap.shape[1]+1)-f[0].header.get('CRPIX1'))*f[0].header.get('CDELT1'))/15.0
    dec=f[0].header.get('CRVAL2')+(numpy.arange(1,skymap.shape[0]+1)-f[0].header.get('CRPIX2'))*f[0].header.get('CDELT2')
    mwa=ephem_utils.Obs[ephem_utils.obscode['MWA']]
    RA,Dec=numpy.meshgrid(ra*15,dec)

    # determine the LST
    observer=ephem.Observer()
    # make sure no refraction is included
    observer.pressure=0
    observer.long=mwa.long/ephem_utils.DEG_IN_RADIAN
    observer.lat=mwa.lat/ephem_utils.DEG_IN_RADIAN
    observer.elevation=mwa.elev
    observer.date=obstime.datetime.strftime('%Y/%m/%d %H:%M:%S')
    UTs=obstime.datetime.strftime('%H:%M:%S')
    LST_hours=observer.sidereal_time()*ephem_utils.HRS_IN_RADIAN
    LST=ephem_utils.dec2sexstring(LST_hours,digits=0,roundseconds=1)
    
    HA=-RA+LST_hours*15
    Az,Alt=ephem_utils.eq2horz(HA,Dec,mwa.lat)
    
    fig=pylab.figure(figsize=(figsize,figsize),dpi=dpi)
    ax1=fig.add_subplot(1,1,1)

    bmap = Basemap(projection='ortho',lat_0=mwa.lat,lon_0=LST_hours*15-360)
    nx=len(ra)
    ny=len(dec)

    ax1.cla()

    # get the primary beam
    R=primarybeammap.return_beam(Alt,Az,mwaobs.delays,
                                 mwaobs.center_channel*1.28)

    # figure out the constellation
    if mwaobs.ra_phase_center is not None:
        constellation=ephem.constellation((numpy.radians(mwaobs.ra_phase_center),
                                           numpy.radians(mwaobs.dec_phase_center)))
    else:
        racenter=RA[R==R.max()]
        deccenter=Dec[R==R.max()]
        constellation=ephem.constellation((numpy.radians(racenter),
                                           numpy.radians(deccenter)))

    # show the Haslam map
    tform_skymap=bmap.transform_scalar(skymap[:,::-1],ra[::-1]*15,
                                       dec,nx,ny,masked=True)
    bmap.imshow(numpy.ma.log10(tform_skymap[:,::-1]),
                cmap=cm,
                vmin=math.log10(low),vmax=math.log10(high))
    # show the beam
    X,Y=bmap(RA,Dec)
    bmap.contour(bmap.xmax-X,Y,R,[0.5,0.95],colors='w')
    
    X0,Y0=bmap(LST_hours*15-360,mwa.lat)

    # plot the constellations
    ConstellationStars=[]
    for c in Constellations.keys():
        for i in xrange(0,len(Constellations[c][1]),2):
            i1=numpy.where(HIP['HIP']==Constellations[c][1][i])[0][0]
            i2=numpy.where(HIP['HIP']==Constellations[c][1][i+1])[0][0]
            star1=HIP[i1]
            star2=HIP[i2]
            if not i1 in ConstellationStars:
                ConstellationStars.append(i1)
            if not i2 in ConstellationStars:
                ConstellationStars.append(i2)
            ra1,dec1=map(numpy.degrees,(star1['RArad'],star1['DErad']))
            ra2,dec2=map(numpy.degrees,(star2['RArad'],star2['DErad']))
            ra=numpy.array([ra1,ra2])
            dec=numpy.array([dec1,dec2])
            newx,newy=bmap(ra,dec)
            testx,testy=bmap(newx,newy,inverse=True)
            if testx.max()<1e30 and testy.max()<1e30:
                bmap.plot(2*X0-newx,newy,'r-',latlon=False)

    # figure out the coordinates
    # and plot the stars
    ra=numpy.degrees(HIP[ConstellationStars]['RArad'])
    dec=numpy.degrees(HIP[ConstellationStars]['DErad'])
    m=numpy.degrees(HIP[ConstellationStars]['Hpmag'])
    newx,newy=bmap(ra,dec)
    testx,testy=bmap(newx,newy,inverse=True)
    good=(newx > bmap.xmin) & (newx < bmap.xmax) & (newy > bmap.ymin) & (newy < bmap.ymax)
    size=60-15*m
    size[size<=15]=15
    size[size>=60]=60
    bmap.scatter(bmap.xmax-newx[good], newy[good], size[good], 'b',
                 edgecolor='none',
                 alpha=0.7)
     
    # plot the bodies    
    for b in Bodies.keys():
        color=Bodies[b][1]
        size=Bodies[b][0]
        body=b(observer)
        ra,dec=map(numpy.degrees,(body.ra,body.dec))
        newx,newy=bmap(ra,dec)
        testx,testy=bmap(newx,newy,inverse=True)
        if testx<1e30 and testy<1e30:
            bmap.scatter(2*X0-newx,newy,latlon=False,s=size,c=color,alpha=0.5,
                         edgecolor='none')

    # and label some sources
    for source in primarybeammap.sources.keys():
        if source == 'EOR0b':
            continue
        if source=='CenA':
            primarybeammap.sources[source][0]='Cen A'
        if source=='ForA':
            primarybeammap.sources[source][0]='For A'
        r=ephem_utils.sexstring2dec(primarybeammap.sources[source][1])
        d=ephem_utils.sexstring2dec(primarybeammap.sources[source][2])
        horizontalalignment='left'
        x=r
        if (len(primarybeammap.sources[source])>=6 and primarybeammap.sources[source][5]=='c'):    
            horizontalalignment='center'
            x=r
        if (len(primarybeammap.sources[source])>=6 and primarybeammap.sources[source][5]=='r'):    
            horizontalalignment='right'
            x=r      
        fontsize=primarybeammap.defaultsize
        if (len(primarybeammap.sources[source])>=5):
            fontsize=primarybeammap.sources[source][4]
        color=primarybeammap.defaultcolor
        if (len(primarybeammap.sources[source])>=4):
            color=primarybeammap.sources[source][3]
        if color=='k':
            color='w'
        xx,yy=bmap(x*15-360,d)
        try:
            if xx<1e30 and yy<1e30:
                ax1.text(bmap.xmax-xx+2e5,yy,primarybeammap.sources[source][0],
                         horizontalalignment=horizontalalignment,
                         fontsize=fontsize,color=color,
                         verticalalignment='center')
        except:
            pass

        if options.text:
            ax1.text(0, bmap.ymax-2e5,
                     '%s:\n%s at %d MHz\n in the constellation %s' % (obstime.datetime.strftime('%Y-%m-%d %H:%M UT'),
                                                                      mwaobs.filename.replace('_','\_'),
                                                                      mwaobs.center_channel*1.28,
                                                                      constellation[1]),
                     fontsize=10)

        ax1.text(bmap.xmax,Y0,'W',fontsize=12,
                 horizontalalignment='left',verticalalignment='center')
        ax1.text(bmap.xmin,Y0,'E',fontsize=12,
                 horizontalalignment='right',verticalalignment='center')
        ax1.text(X0,bmap.ymax,'N',fontsize=12,
                 horizontalalignment='center',verticalalignment='bottom')         
        ax1.text(X0,bmap.ymin,'S',fontsize=12,
                 horizontalalignment='center',verticalalignment='top')

        try:
            fig.savefig(options.out,transparent=True,facecolor='none')
        except:
            make_error('Cannot save output',options.out)
            
######################################################################

if __name__=="__main__":
    main()

