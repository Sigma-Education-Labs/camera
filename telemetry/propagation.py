
from math import atan2, cos, fabs, pi, sin, sqrt

deg2rad = pi / 180.0;
_nan = float('NaN')
false = (_nan, _nan, _nan)
true = True
twopi = 2.0 * pi

def _initl(
       # not needeed. included in satrec if needed later
       # satn,
       # sgp4fix assin xke and j2
       # whichconst,
       xke, j2,
       ecco,   epoch,  inclo,   no,
       method,
       opsmode,
       ):

     # sgp4fix use old way of finding gst

     #  ----------------------- earth constants ----------------------
     x2o3   = 2.0 / 3.0;

     #  ------------- calculate auxillary epoch quantities ----------
     eccsq  = ecco * ecco;
     omeosq = 1.0 - eccsq;
     rteosq = sqrt(omeosq);
     cosio  = cos(inclo);
     cosio2 = cosio * cosio;

     #  ------------------ un-kozai the mean motion -----------------
     ak    = pow(xke / no, x2o3);
     d1    = 0.75 * j2 * (3.0 * cosio2 - 1.0) / (rteosq * omeosq);
     del_  = d1 / (ak * ak);
     adel  = ak * (1.0 - del_ * del_ - del_ *
             (1.0 / 3.0 + 134.0 * del_ * del_ / 81.0));
     del_  = d1/(adel * adel);
     no    = no / (1.0 + del_);

     ao    = pow(xke / no, x2o3);
     sinio = sin(inclo);
     po    = ao * omeosq;
     con42 = 1.0 - 5.0 * cosio2;
     con41 = -con42-cosio2-cosio2;
     ainv  = 1.0 / ao;
     posq  = po * po;
     rp    = ao * (1.0 - ecco);
     method = 'n';

     #  sgp4fix modern approach to finding sidereal time
     if opsmode == 'a':

         #  sgp4fix use old way of finding gst
         #  count integer number of days from 0 jan 1970
         ts70  = epoch - 7305.0;
         ds70 = (ts70 + 1.0e-8) // 1.0;
         tfrac = ts70 - ds70;
         #  find greenwich location at epoch
         c1    = 1.72027916940703639e-2;
         thgr70= 1.7321343856509374;
         fk5r  = 5.07551419432269442e-15;
         c1p2p = c1 + twopi;
         gsto  = (thgr70 + c1*ds70 + c1p2p*tfrac + ts70*ts70*fk5r) % twopi
         if gsto < 0.0:
             gsto = gsto + twopi;

     else:
        gsto = _gstime(epoch + 2433281.5);

     return (
       no,
       method,
       ainv,  ao,    con41,  con42, cosio,
       cosio2,eccsq, omeosq, posq,
       rp,    rteosq,sinio , gsto,
       )

def sgp4init(
       whichconst,   opsmode,   satn,   epoch,
       xbstar,   xndot,   xnddot,   xecco,   xargpo,
       xinclo,   xmo,   xno_kozai,
       xnodeo,  satrec,
       ):

     """
     /* ------------------------ initialization --------------------- */

     """
     temp4    =   1.5e-12;

     #  ----------- set all near earth variables to zero ------------
     satrec.isimp   = 0;   satrec.method = 'n'; satrec.aycof    = 0.0;
     satrec.con41   = 0.0; satrec.cc1    = 0.0; satrec.cc4      = 0.0;
     satrec.cc5     = 0.0; satrec.d2     = 0.0; satrec.d3       = 0.0;
     satrec.d4      = 0.0; satrec.delmo  = 0.0; satrec.eta      = 0.0;
     satrec.argpdot = 0.0; satrec.omgcof = 0.0; satrec.sinmao   = 0.0;
     satrec.t       = 0.0; satrec.t2cof  = 0.0; satrec.t3cof    = 0.0;
     satrec.t4cof   = 0.0; satrec.t5cof  = 0.0; satrec.x1mth2   = 0.0;
     satrec.x7thm1  = 0.0; satrec.mdot   = 0.0; satrec.nodedot  = 0.0;
     satrec.xlcof   = 0.0; satrec.xmcof  = 0.0; satrec.nodecf   = 0.0;

     #  ------------------------ earth constants -----------------------
     #  sgp4fix identify constants and allow alternate values
     #  this is now the only call for the constants
     (satrec.tumin, satrec.mu, satrec.radiusearthkm, satrec.xke,
       satrec.j2, satrec.j3, satrec.j4, satrec.j3oj2) = whichconst;

 	 # -------------------------------------------------------------------------

     satrec.error = 0;
     satrec.operationmode = opsmode;
     satrec.satnum = satn;

     satrec.bstar   = xbstar;
    # sgp4fix allow additional parameters in the struct
     satrec.ndot    = xndot;
     satrec.nddot   = xnddot;
     satrec.ecco    = xecco;
     satrec.argpo   = xargpo;
     satrec.inclo   = xinclo;
     satrec.mo	    = xmo;
	# sgp4fix rename variables to clarify which mean motion is intended
     satrec.no_kozai= xno_kozai;
     satrec.nodeo   = xnodeo;

    # single averaged mean elements
     satrec.am = 0.0
     satrec.em = 0.0
     satrec.im = 0.0
     satrec.Om = 0.0
     satrec.mm = 0.0
     satrec.nm = 0.0

    # ------------------------ earth constants ----------------------- */
	# sgp4fix identify constants and allow alternate values no longer needed
	# getgravconst( whichconst, tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2 );
     ss     = 78.0 / satrec.radiusearthkm + 1.0;
     #  sgp4fix use multiply for speed instead of pow
     qzms2ttemp = (120.0 - 78.0) / satrec.radiusearthkm;
     qzms2t = qzms2ttemp * qzms2ttemp * qzms2ttemp * qzms2ttemp;
     x2o3   =  2.0 / 3.0;

     satrec.init = 'y';
     satrec.t	 = 0.0;

    # sgp4fix remove satn as it is not needed in initl
     (
       satrec.no_unkozai,
       method,
       ainv,  ao,    satrec.con41,  con42, cosio,
       cosio2,eccsq, omeosq, posq,
       rp,    rteosq,sinio , satrec.gsto,
       ) = _initl(
           satrec.xke, satrec.j2, satrec.ecco, epoch, satrec.inclo, satrec.no_kozai, satrec.method,
           satrec.operationmode
         );
     satrec.a    = pow( satrec.no_unkozai*satrec.tumin , (-2.0/3.0) );
     satrec.alta = satrec.a*(1.0 + satrec.ecco) - 1.0;
     satrec.altp = satrec.a*(1.0 - satrec.ecco) - 1.0;


     if omeosq >= 0.0 or satrec.no_unkozai >= 0.0:

         satrec.isimp = 0;
         if rp < 220.0 / satrec.radiusearthkm + 1.0:
             satrec.isimp = 1;
         sfour  = ss;
         qzms24 = qzms2t;
         perige = (rp - 1.0) * satrec.radiusearthkm;

         #  - for perigees below 156 km, s and qoms2t are altered -
         if perige < 156.0:

             sfour = perige - 78.0;
             if perige < 98.0:
                 sfour = 20.0;
             #  sgp4fix use multiply for speed instead of pow
             qzms24temp =  (120.0 - sfour) / satrec.radiusearthkm;
             qzms24 = qzms24temp * qzms24temp * qzms24temp * qzms24temp;
             sfour  = sfour / satrec.radiusearthkm + 1.0;

         pinvsq = 1.0 / posq;

         tsi  = 1.0 / (ao - sfour);
         satrec.eta  = ao * satrec.ecco * tsi;
         etasq = satrec.eta * satrec.eta;
         eeta  = satrec.ecco * satrec.eta;
         psisq = fabs(1.0 - etasq);
         coef  = qzms24 * pow(tsi, 4.0);
         coef1 = coef / pow(psisq, 3.5);
         cc2   = coef1 * satrec.no_unkozai * (ao * (1.0 + 1.5 * etasq + eeta *
                        (4.0 + etasq)) + 0.375 * satrec.j2 * tsi / psisq * satrec.con41 *
                        (8.0 + 3.0 * etasq * (8.0 + etasq)));
         satrec.cc1   = satrec.bstar * cc2;
         cc3   = 0.0;
         if satrec.ecco > 1.0e-4:
             cc3 = -2.0 * coef * tsi * satrec.j3oj2 * satrec.no_unkozai * sinio / satrec.ecco;
         satrec.x1mth2 = 1.0 - cosio2;
         satrec.cc4    = 2.0* satrec.no_unkozai * coef1 * ao * omeosq * \
                           (satrec.eta * (2.0 + 0.5 * etasq) + satrec.ecco *
                           (0.5 + 2.0 * etasq) - satrec.j2 * tsi / (ao * psisq) *
                           (-3.0 * satrec.con41 * (1.0 - 2.0 * eeta + etasq *
                           (1.5 - 0.5 * eeta)) + 0.75 * satrec.x1mth2 *
                           (2.0 * etasq - eeta * (1.0 + etasq)) * cos(2.0 * satrec.argpo)));
         satrec.cc5 = 2.0 * coef1 * ao * omeosq * (1.0 + 2.75 *
                        (etasq + eeta) + eeta * etasq);
         cosio4 = cosio2 * cosio2;
         temp1  = 1.5 * satrec.j2 * pinvsq * satrec.no_unkozai;
         temp2  = 0.5 * temp1 * satrec.j2 * pinvsq;
         temp3  = -0.46875 * satrec.j4 * pinvsq * pinvsq * satrec.no_unkozai;
         satrec.mdot     = satrec.no_unkozai + 0.5 * temp1 * rteosq * satrec.con41 + 0.0625 * \
                            temp2 * rteosq * (13.0 - 78.0 * cosio2 + 137.0 * cosio4);
         satrec.argpdot  = (-0.5 * temp1 * con42 + 0.0625 * temp2 *
                             (7.0 - 114.0 * cosio2 + 395.0 * cosio4) +
                             temp3 * (3.0 - 36.0 * cosio2 + 49.0 * cosio4));
         xhdot1            = -temp1 * cosio;
         satrec.nodedot = xhdot1 + (0.5 * temp2 * (4.0 - 19.0 * cosio2) +
                              2.0 * temp3 * (3.0 - 7.0 * cosio2)) * cosio;
         xpidot            =  satrec.argpdot+ satrec.nodedot;
         satrec.omgcof   = satrec.bstar * cc3 * cos(satrec.argpo);
         satrec.xmcof    = 0.0;
         if satrec.ecco > 1.0e-4:
             satrec.xmcof = -x2o3 * coef * satrec.bstar / eeta;
         satrec.nodecf = 3.5 * omeosq * xhdot1 * satrec.cc1;
         satrec.t2cof   = 1.5 * satrec.cc1;
         #  sgp4fix for divide by zero with xinco = 180 deg
         if fabs(cosio+1.0) > 1.5e-12:
             satrec.xlcof = -0.25 * satrec.j3oj2 * sinio * (3.0 + 5.0 * cosio) / (1.0 + cosio);
         else:
             satrec.xlcof = -0.25 * satrec.j3oj2 * sinio * (3.0 + 5.0 * cosio) / temp4;
         satrec.aycof   = -0.5 * satrec.j3oj2 * sinio;
         #  sgp4fix use multiply for speed instead of pow
         delmotemp = 1.0 + satrec.eta * cos(satrec.mo);
         satrec.delmo   = delmotemp * delmotemp * delmotemp;
         satrec.sinmao  = sin(satrec.mo);
         satrec.x7thm1  = 7.0 * cosio2 - 1.0;

         #----------- set variables if not deep space -----------
         if satrec.isimp != 1:

           cc1sq          = satrec.cc1 * satrec.cc1;
           satrec.d2    = 4.0 * ao * tsi * cc1sq;
           temp           = satrec.d2 * tsi * satrec.cc1 / 3.0;
           satrec.d3    = (17.0 * ao + sfour) * temp;
           satrec.d4    = 0.5 * temp * ao * tsi * (221.0 * ao + 31.0 * sfour) * \
                            satrec.cc1;
           satrec.t3cof = satrec.d2 + 2.0 * cc1sq;
           satrec.t4cof = 0.25 * (3.0 * satrec.d3 + satrec.cc1 *
                            (12.0 * satrec.d2 + 10.0 * cc1sq));
           satrec.t5cof = 0.2 * (3.0 * satrec.d4 +
                            12.0 * satrec.cc1 * satrec.d3 +
                            6.0 * satrec.d2 * satrec.d2 +
                            15.0 * cc1sq * (2.0 * satrec.d2 + cc1sq));

     sgp4(satrec, 0.0, whichconst);

     satrec.init = 'n';

     # sgp4fix return boolean. satrec.error contains any error codes
     return true;

def sgp4(satrec, tsince, whichconst=None):

     mrt = 0.0

     """
     /* ------------------ set mathematical constants --------------- */
     // sgp4fix divisor for divide by zero check on inclination
     // the old check used 1.0 + cos(pi-1.0e-9), but then compared it to
     // 1.5 e-12, so the threshold was changed to 1.5e-12 for consistency
     """
     temp4 =   1.5e-12;
     twopi = 2.0 * pi;
     x2o3  = 2.0 / 3.0;
     #  sgp4fix identify constants and allow alternate values
     # tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2 = whichconst
     vkmpersec     = satrec.radiusearthkm * satrec.xke/60.0;

     #  --------------------- clear sgp4 error flag -----------------
     satrec.t     = tsince;
     satrec.error = 0;
     satrec.error_message = None

     #  ------- update for secular gravity and atmospheric drag -----
     xmdf    = satrec.mo + satrec.mdot * satrec.t;
     argpdf  = satrec.argpo + satrec.argpdot * satrec.t;
     nodedf  = satrec.nodeo + satrec.nodedot * satrec.t;
     argpm   = argpdf;
     mm      = xmdf;
     t2      = satrec.t * satrec.t;
     nodem   = nodedf + satrec.nodecf * t2;
     tempa   = 1.0 - satrec.cc1 * satrec.t;
     tempe   = satrec.bstar * satrec.cc4 * satrec.t;
     templ   = satrec.t2cof * t2;

     if satrec.isimp != 1:

         delomg = satrec.omgcof * satrec.t;
         #  sgp4fix use mutliply for speed instead of pow
         delmtemp =  1.0 + satrec.eta * cos(xmdf);
         delm   = satrec.xmcof * \
                  (delmtemp * delmtemp * delmtemp -
                  satrec.delmo);
         temp   = delomg + delm;
         mm     = xmdf + temp;
         argpm  = argpdf - temp;
         t3     = t2 * satrec.t;
         t4     = t3 * satrec.t;
         tempa  = tempa - satrec.d2 * t2 - satrec.d3 * t3 - \
                          satrec.d4 * t4;
         tempe  = tempe + satrec.bstar * satrec.cc5 * (sin(mm) -
                          satrec.sinmao);
         templ  = templ + satrec.t3cof * t3 + t4 * (satrec.t4cof +
                          satrec.t * satrec.t5cof);

     nm    = satrec.no_unkozai;
     em    = satrec.ecco;
     inclm = satrec.inclo;

     if nm <= 0.0:

         satrec.error_message = ('mean motion {0:f} is less than zero'
                                 .format(nm))
         satrec.error = 2;
         #  sgp4fix add return
         return false, false;

     am = pow((satrec.xke / nm),x2o3) * tempa * tempa;
     nm = satrec.xke / pow(am, 1.5);
     em = em - tempe;

     #  fix tolerance for error recognition
     #  sgp4fix am is fixed from the previous nm check
     if em >= 1.0 or em < -0.001:  # || (am < 0.95)

         satrec.error_message = ('mean eccentricity {0:f} not within'
                                 ' range 0.0 <= e < 1.0'.format(em))
         satrec.error = 1;
         #  sgp4fix to return if there is an error in eccentricity
         return false, false;

     #  sgp4fix fix tolerance to avoid a divide by zero
     if em < 1.0e-6:
         em  = 1.0e-6;
     mm     = mm + satrec.no_unkozai * templ;
     xlm    = mm + argpm + nodem;
     emsq   = em * em;
     temp   = 1.0 - emsq;

     nodem  = nodem % twopi if nodem >= 0.0 else -(-nodem % twopi)
     argpm  = argpm % twopi
     xlm    = xlm % twopi
     mm     = (xlm - argpm - nodem) % twopi

     # sgp4fix recover singly averaged mean elements
     satrec.am = am;
     satrec.em = em;
     satrec.im = inclm;
     satrec.Om = nodem;
     satrec.om = argpm;
     satrec.mm = mm;
     satrec.nm = nm;

     #  ----------------- compute extra mean quantities -------------
     sinim = sin(inclm);
     cosim = cos(inclm);

     #  -------------------- add lunar-solar periodics --------------
     ep     = em;
     xincp  = inclm;
     argpp  = argpm;
     nodep  = nodem;
     mp     = mm;
     sinip  = sinim;
     cosip  = cosim;

     #  -------------------- long period periodics ------------------
     if satrec.method == 'd':

         sinip =  sin(xincp);
         cosip =  cos(xincp);
         satrec.aycof = -0.5*satrec.j3oj2*sinip;
         #  sgp4fix for divide by zero for xincp = 180 deg
         if fabs(cosip+1.0) > 1.5e-12:
             satrec.xlcof = -0.25 * satrec.j3oj2 * sinip * (3.0 + 5.0 * cosip) / (1.0 + cosip);
         else:
             satrec.xlcof = -0.25 * satrec.j3oj2 * sinip * (3.0 + 5.0 * cosip) / temp4;

     axnl = ep * cos(argpp);
     temp = 1.0 / (am * (1.0 - ep * ep));
     aynl = ep* sin(argpp) + temp * satrec.aycof;
     xl   = mp + argpp + nodep + temp * satrec.xlcof * axnl;

     #  --------------------- solve kepler's equation ---------------
     u    = (xl - nodep) % twopi
     eo1  = u;
     tem5 = 9999.9;
     ktr = 1;
     #    sgp4fix for kepler iteration
     #    the following iteration needs better limits on corrections
     while fabs(tem5) >= 1.0e-12 and ktr <= 10:

         sineo1 = sin(eo1);
         coseo1 = cos(eo1);
         tem5   = 1.0 - coseo1 * axnl - sineo1 * aynl;
         tem5   = (u - aynl * coseo1 + axnl * sineo1 - eo1) / tem5;
         if fabs(tem5) >= 0.95:
             tem5 = 0.95 if tem5 > 0.0 else -0.95;
         eo1    = eo1 + tem5;
         ktr = ktr + 1;

     #  ------------- short period preliminary quantities -----------
     ecose = axnl*coseo1 + aynl*sineo1;
     esine = axnl*sineo1 - aynl*coseo1;
     el2   = axnl*axnl + aynl*aynl;
     pl    = am*(1.0-el2);
     if pl < 0.0:

         satrec.error_message = ('semilatus rectum {0:f} is less than zero'
                                 .format(pl))
         satrec.error = 4;
         #  sgp4fix add return
         return false, false;

     else:

         rl     = am * (1.0 - ecose);
         rdotl  = sqrt(am) * esine/rl;
         rvdotl = sqrt(pl) / rl;
         betal  = sqrt(1.0 - el2);
         temp   = esine / (1.0 + betal);
         sinu   = am / rl * (sineo1 - aynl - axnl * temp);
         cosu   = am / rl * (coseo1 - axnl + aynl * temp);
         su     = atan2(sinu, cosu);
         sin2u  = (cosu + cosu) * sinu;
         cos2u  = 1.0 - 2.0 * sinu * sinu;
         temp   = 1.0 / pl;
         temp1  = 0.5 * satrec.j2 * temp;
         temp2  = temp1 * temp;

         #  -------------- update for short period periodics ------------
         if satrec.method == 'd':

             cosisq                 = cosip * cosip;
             satrec.con41  = 3.0*cosisq - 1.0;
             satrec.x1mth2 = 1.0 - cosisq;
             satrec.x7thm1 = 7.0*cosisq - 1.0;

         mrt   = rl * (1.0 - 1.5 * temp2 * betal * satrec.con41) + \
                 0.5 * temp1 * satrec.x1mth2 * cos2u;
         su    = su - 0.25 * temp2 * satrec.x7thm1 * sin2u;
         xnode = nodep + 1.5 * temp2 * cosip * sin2u;
         xinc  = xincp + 1.5 * temp2 * cosip * sinip * cos2u;
         mvt   = rdotl - nm * temp1 * satrec.x1mth2 * sin2u / satrec.xke;
         rvdot = rvdotl + nm * temp1 * (satrec.x1mth2 * cos2u +
                 1.5 * satrec.con41) / satrec.xke;

         #  --------------------- orientation vectors -------------------
         sinsu =  sin(su);
         cossu =  cos(su);
         snod  =  sin(xnode);
         cnod  =  cos(xnode);
         sini  =  sin(xinc);
         cosi  =  cos(xinc);
         xmx   = -snod * cosi;
         xmy   =  cnod * cosi;
         ux    =  xmx * sinsu + cnod * cossu;
         uy    =  xmy * sinsu + snod * cossu;
         uz    =  sini * sinsu;
         vx    =  xmx * cossu - cnod * sinsu;
         vy    =  xmy * cossu - snod * sinsu;
         vz    =  sini * cossu;

         #  --------- position and velocity (in km and km/sec) ----------
         _mr = mrt * satrec.radiusearthkm
         r = (_mr * ux, _mr * uy, _mr * uz)
         v = ((mvt * ux + rvdot * vx) * vkmpersec,
              (mvt * uy + rvdot * vy) * vkmpersec,
              (mvt * uz + rvdot * vz) * vkmpersec)

     #  sgp4fix for decaying satellites
     if mrt < 1.0:

         satrec.error_message = ('mrt {0:f} is less than 1.0 indicating'
                                 ' the satellite has decayed'.format(mrt))
         satrec.error = 6;

     return r, v;

def gstime(jdut1):

     tut1 = (jdut1 - 2451545.0) / 36525.0;
     temp = -6.2e-6* tut1 * tut1 * tut1 + 0.093104 * tut1 * tut1 + \
             (876600.0*3600 + 8640184.812866) * tut1 + 67310.54841;  #  sec
     temp = (temp * deg2rad / 240.0) % twopi # 360/86400 = 1/240, to deg, to rad

     #  ------------------------ check quadrants ---------------------
     if temp < 0.0:
         temp += twopi;

     return temp;

# The routine was originally marked private, so make it available under
# the old name for compatibility:
_gstime = gstime
def getgravconst(whichconst):

       if whichconst == 'wgs72old':
           mu     = 398600.79964;        #  in km3 / s2
           radiusearthkm = 6378.135;     #  km
           xke    = 0.0743669161;
           tumin  = 1.0 / xke;
           j2     =   0.001082616;
           j3     =  -0.00000253881;
           j4     =  -0.00000165597;
           j3oj2  =  j3 / j2;

           #  ------------ wgs-72 constants ------------
       elif whichconst == 'wgs72':
           mu     = 398600.8;            #  in km3 / s2
           radiusearthkm = 6378.135;     #  km
           xke    = 60.0 / sqrt(radiusearthkm*radiusearthkm*radiusearthkm/mu);
           tumin  = 1.0 / xke;
           j2     =   0.001082616;
           j3     =  -0.00000253881;
           j4     =  -0.00000165597;
           j3oj2  =  j3 / j2;

       elif whichconst == 'wgs84':
           #  ------------ wgs-84 constants ------------
           mu     = 398600.5;            #  in km3 / s2
           radiusearthkm = 6378.137;     #  km
           xke    = 60.0 / sqrt(radiusearthkm*radiusearthkm*radiusearthkm/mu);
           tumin  = 1.0 / xke;
           j2     =   0.00108262998905;
           j3     =  -0.00000253215306;
           j4     =  -0.00000161098761;
           j3oj2  =  j3 / j2;

       return tumin, mu, radiusearthkm, xke, j2, j3, j4, j3oj2