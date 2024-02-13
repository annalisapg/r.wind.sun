#!/usr/bin/env python3

import grass.script as gs
import os,sys,re,math,numpy

panels_width=210;
panels_height=420;
angle=0;
orient=210;
panels_center_height=1;
obs_elev=2.70;
resolution=2;
min_dist_from_panel=220;
max_dist_from_panel=12000;
dem='DSM_2M_GAETA_UTM33';
panels='impianti_p1';
impact='impact_impianti1';

#dem = options['DSM_2M_GAETA_UTM33'];
#panels = options['PUNTI_GABBIE'];
#output = options['output'];

def main():
    gs.run_command('g.gisenv',set='OVERWRITE=1');
    gs.mapcalc('n_pann_visib = 0');
    gs.mapcalc('dist_or = 0.0');
    gs.mapcalc('{a} = 0.0'.format(a=impact));
    gs.run_command('g.region',res=resolution);
    gs.run_command('v.drape',input=panels,type='point',elevation=dem,output='panels3D',method='nearest',scale='1.0',layer='1');
    d=gs.read_command('v.to.db',flags='p', map='panels3D', type='point', layer='1', qlayer='1', option='coor', columns='x,y');
    e=re.split('\n',d)[1:-1];
    n=0
    for i in e:
        n= n + 1;
        print(n);
        x=float(re.split('\|',i)[1]);
        y=float(re.split('\|',i)[2]);
        z=float(re.split('\|',i)[3]);
        cat=int(re.split('\|',i)[0]);
        obs_elev= 1.70 + float(panels_center_height);
        gs.run_command('g.remove',type='raster',flags='f',name='los_degree_'+str(cat));
        coordinate=str(x)+','+str(y);
        gs.run_command('r.viewshed',input=dem,output='los_degree_'+str(cat),coordinates=coordinate,observer_elevation=obs_elev,max_distance=max_dist_from_panel);
        gs.mapcalc('los_boolean = {a}/{b}'.format(a='los_degree_'+str(cat),b='los_degree_'+str(cat)));
        gs.run_command('r.null',map='los_boolean',null='0');
        gs.mapcalc('n_pann_visib = n_pann_visib+{a}'.format(a='los_boolean'));
        gs.mapcalc('MASK = if( {a} == 0 ,null(),1)'.format(a='los_boolean'));
        gs.mapcalc('px = x()-{a}'.format(a=x));
        gs.mapcalc('py = y()-{a}'.format(a=y));
        gs.mapcalc('{a} = sqrt(({b})^2+({c})^2)'.format(a='dist_or_'+str(cat),b='px',c='py'));
        gs.mapcalc('{a} = if({a} < {b},{b},{a})'.format(a='dist_or_'+str(cat),b=min_dist_from_panel));
        gs.mapcalc('{a} = (if({b} >= 0 & {c} >= 0,90-atan({c}/{b}),if({b} >= 0 & {c} < 0,90-atan({c}/{b}),if({b} < 0 & {c} < 0,270-atan({c}/{b}),if({b} < 0 & {c} >= 0,270-atan({c}/{b}))))))-{d}'.format(a='azimuth_'+str(cat),b='px',c='py',d=orient));
        gs.mapcalc('{a} = abs(2*({b}*0.5)*cos({c})*({d}/({d}+({b}*0.5)*sin({c}))))'.format(a='apparent_width_'+str(cat),b=panels_width,c='azimuth_'+str(cat),d='dist_or_'+str(cat)));
        gs.mapcalc('{a} = ({b}+{c})-{d}'.format(a='dist_ver_'+str(cat),b=z,c=panels_center_height,d=dem));
        gs.mapcalc('{a} = sqrt(({b})^2+({c})^2)'.format(a='dist_'+str(cat),b='dist_or_'+str(cat),c='dist_ver_'+str(cat)));
        gs.mapcalc('{a} = if({b} < (90+{c}),{b}-90+{c},if({b} = (90+{c}),90,{b}-90-{c}))'.format(a='angle',b='los_degree_'+str(cat),c=angle));
        gs.mapcalc('{a} = 2*(({b}*0.5)*sin(abs({c})))*({d}/({d}+(({b}*0.5)*cos({c}))))'.format(a='apparent_height_'+str(cat),b=panels_height,c='angle',d='dist_'+str(cat)));
        gs.mapcalc('{a} = 2*{b}*{c}'.format(a='circle',b=math.pi,c='dist_or_'+str(cat)));
        gs.mapcalc('{a} = {b}*(tan(60))'.format(a='d',b='dist_or_'+str(cat)));
        gs.mapcalc('{a} = {b}*(tan(75))'.format(a='b',b='dist_or_'+str(cat)));
        gs.mapcalc('{a} = ({b}+{c})*{d}'.format(a='fov_'+str(cat),b='b',c='d',d='circle'));
        gs.mapcalc('{a} = ({b}*{c}/{d})*100'.format(a='imp_'+str(cat),b='apparent_height_'+str(cat),c='apparent_width_'+str(cat),d='fov_'+str(cat)));
        gs.run_command('g.remove',type='raster',name='MASK',flags='f');
        gs.run_command('r.null',map='imp_'+str(cat),null='0');
        gs.mapcalc('{a} = {a}+{b}'.format(a=impact,b='imp_'+str(cat)));
        gs.run_command('r.colors',flags='e',map=impact,color='rainbow');
        gs.run_command('r.univar',map=impact);
        r2remove='apparent_height_'+str(cat)+','+'apparent_width_'+str(cat)+','+'azimuth_'+str(cat)+','+'dist_'+str(cat)+','+'dist_or_'+str(cat)+','+'dist_ver_'+str(cat)+','+'fov_'+str(cat)+','+'imp_'+str(cat)+','+'los_degree_'+str(cat);
        gs.run_command('g.remove',type='raster',flags='f',name=r2remove);
    
    gs.run_command('r.null',map=impact,setnull='0');
    gs.run_command('g.remove',type='raster',flags='f',name='angle,b,circle,d,dist_or,los_boolean,n_pann_visib,px,py');
    gs.run_command('g.remove',type='vector',flags='f',name='panels3D');


if __name__ == '__main__':
    sys.exit(main())
