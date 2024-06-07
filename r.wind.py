#!/usr/bin/env python3

############################################################################
#
# MODULE:       r.wind
#
# AUTHOR(S):    Annalisa Minelli, Ivan Marchesini
#
# PURPOSE:      Creates visual impact raster map of aerogenerators
#
# COPYRIGHT:    (C) 2024 by GRASS development team
#
#               This program is free software under the GNU General
#               Public License (>=v3). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

#%Module
#%  description: Calculates visual impact raster map of aerogenerators calculating objects distorsions starting from a DEM and a .dxf model of a wind turbine
#%  keyword: visibility
# % keyword: viewshed
# % keyword: impact
# % keyword: aerogenerators
# % keyword: mapcalculation
#%End 
#%option G_OPT_R_INPUT
#% key: dem
#% description: DEM of the zone
#%end
#%option G_OPT_R_OUTPUT
#% key: impact
#% description: Impact output map
#%end
#%option G_OPT_V_INPUT
#% key: input
#% description: Vector file of points where to place aerogenerators
#% guisection: Wind
#%end
#%option 
#% key: machine
#% type: string
#% key_desc: name
#% description: Ascii file of the aerogenerator model to simulate
#% required: yes
#% guisection: Wind
#%end
#%option
#% key: high
#% type: double
#% description: Aerogenerator's height [m]
#% required: yes
#% guisection: Wind
#%end
#%option
#% key: wind
#% type: integer
#% description: Wind direction in degree starting from North
# % options: 0-360
# % answer: 0
#% required: yes
#% guisection: Wind
#%end
#%option
#% key: f
#% type: double
#% description: Maximum distance for computing visual impact [m]
#% required: yes
#% guisection: Wind
#%end
#%option G_OPT_V_OUTPUT
#% key: windfarm2
#% type: string
#% description: Output vector map 2D of aerogenerators
#% required: yes
#% guisection: Wind
#%end
#%option G_OPT_V_OUTPUT
#% key: windfarm3
#% type: string
#% description: Output vector map 3D of aerogenerators
#% required: yes
#% guisection: Wind
#%end
# %option
# % key: resolution
# % type: integer
# % description: Output impact map resolution
# % required: yes
#%end

import sys,os,re,numpy,math
import grass.script as gs


def main():
	dem=options["dem"];
	impact=options["impact"];
	input=options["input"];
	machine=options["machine"];
	high=options["high"];
	wind=options["wind"];
	f=options["f"];
	windfarm2=options["windfarm2"];
	windfarm3=options["windfarm3"];
	resolution=options["resolution"];
	gs.run_command('g.gisenv',set='OVERWRITE=1');



	res_dem=float(re.split('=',re.split('\n',gs.read_command('r.info',flags='g',map=dem))[4])[1]);
	gs.mapcalc('fdem = float({a})'.format(a=dem));
	gs.run_command('v.in.ascii', flags='z', input=machine,output='line',format='standard',separator='|',skip='0',x='1',y='2',z='0',cat='0');
	gs.run_command('g.copy',vect='line,face');
	a=gs.read_command('v.info',flags='g',map='line');
	t=float((re.split('=',re.split('\n',a)[4]))[1]);
	b=float((re.split('=',re.split('\n',a)[5]))[1]);
	e=float((re.split('=',re.split('\n',a)[2]))[1]);
	w=float((re.split('=',re.split('\n',a)[3]))[1]);

	att=(t - b ) - ( e - w )*0.577350269;
	pala_att=(e - w)/1.5;
	scal=float(high)/att;
	wind=int(wind);
	orien=180 - wind;
	gs.run_command('g.remove',type='vector',name='line_model,face_model,pointD');
	gs.run_command('v.transform',input='line',output='line_model',xshift='0.0',yshift='0.0',zshift='0.0',xscale=scal,yscale=scal,zscale=scal,zrotation=orien);
	gs.run_command('v.transform',input='face',output='face_model',xshift='0.0',yshift='0.0',zshift='0.0',xscale=scal,yscale=scal,zscale=scal,zrotation=orien);
	
#added to move the imported machine in the right location
	region_from=gs.read_command('v.info',flags='g',map='line_model');
	ov=float((re.split('=',re.split('\n',region_from)[3]))[1]);
	so=float((re.split('=',re.split('\n',region_from)[1]))[1]);
	es=float((re.split('=',re.split('\n',region_from)[2]))[1]);
	no=float((re.split('=',re.split('\n',region_from)[0]))[1]);
#reading parameters from the center of origin region
	region_center=gs.read_command('g.region',vect='line_model',flags='pcg');
	es_ce=float((re.split('=',re.split('\n',region_center)[11]))[1]);
	no_ce=float((re.split('=',re.split('\n',region_center)[12]))[1]);
#reading the bottom value of the original imported machine
	bo=float((re.split('=',re.split('\n',region_from)[5]))[1]);
#writing the string with the original bounding box
	bbox_from=str(str(ov)+','+str(so)+','+str(es)+','+str(no));
	
	fdiam=( e - w ) * scal * 5;
	gs.run_command('g.region',vect='face_model');
	center=gs.read_command('g.region', flags='cg', vect='face_model');
	#central coordinates of imported dxf model
	east=float(re.split('=',(re.split('\n',center)[0]))[1]);
	north=float(re.split('=',(re.split('\n',center)[1]))[1]);

	info=gs.read_command('v.info', flags='g', map='face_model');
	add=abs(float(re.split('=',re.split('\n',info)[5])[1]));
	gs.run_command('g.region',rast='fdem',res=res_dem);
	gs.run_command('v.drape',input=input,type='point',rast='fdem',scale='1.0',method='nearest',output='pointD');
	a=gs.read_command('v.to.db',flags='pc', map='pointD', type='point', layer='1', qlayer='1', option='coor', units='meters', columns='est,nord,z');
	b=re.split('\n',a)[1:-1];
	n=int(re.split('\|',b[-1])[0]);
	bibidi='';
	bobidi='';
	stringa_linee='';
	stringa_facce='';
	for i in b:
		gs.run_command('g.region',vect=input);
		est=float(re.split('\|',i)[1]);
		nord=float(re.split('\|',i)[2]);
		more=float(re.split('\|',i)[3]);
		addmore=add+more;
		
		k=str(re.split('\|',i)[0]);
		palo_facce='palo_facce_'+k;
		palo_linee='palo_linee_'+k;
		copy_line=str('line_model,'+palo_linee);
		copy_face=str('face_model,'+palo_facce);
		
#writing down the string with displacement parameters
		move_to=str(str(est-es_ce)+','+str(nord-no_ce)+','+str(addmore));
#copying the original model and move it to the right location
		gs.run_command('g.copy',vect=copy_line);
		gs.run_command('g.copy',vect=copy_face);
		gs.run_command('v.edit',tool='move',map=palo_linee,bbox=bbox_from,move=move_to);
		gs.run_command('v.edit',tool='move',map=palo_facce,bbox=bbox_from,move=move_to);
		if k == n :
			stringa_linee=stringa_linee+palo_linee;
			stringa_facce=stringa_facce+palo_facce;
		else:
			stringa_linee=stringa_linee+palo_linee+',';
			stringa_facce=stringa_facce+palo_facce+',';
		
		gs.run_command('v.patch',input=stringa_linee,output=windfarm2);
		gs.run_command('v.patch',input=stringa_facce,output=windfarm3);
	gs.run_command('g.region',vect=windfarm3,n='n'+'+'+str(f),s='s'+'-'+str(f),e='e'+'+'+str(f),w='w'+'-'+str(f));
	tdiam=( e - w ) * scal * 3;
	sdiam=( e - w ) * scal * 7;
	gs.run_command('v.buffer',input=input,output='buf3',type='point,line,area',layer='1',distance=tdiam,scale='1.0',tolerance='0.01');
	gs.run_command('v.buffer',input=input,output='buf5',type='point,line,area',layer='1',distance=fdiam,scale='1.0',tolerance='0.01');
	gs.run_command('v.buffer',input=input,output='buf7',type='point,line,area',layer='1',distance=sdiam,scale='1.0',tolerance='0.01');
	gs.run_command('v.patch',input='buf7,buf5,buf3',output='areas');
	pala_scal= pala_att * scal;
	h=1;
	for i in b:
		gs.run_command('g.region',flags='a',vect=input,res=res_dem,n='n'+'+'+str(f),s='s'+'-'+str(f),e='e'+'+'+str(f),w='w'+'-'+str(f));
		ca=int(re.split('\|',i)[0]);
		xcoor=float(re.split('\|',i)[1]);
		ycoor=float(re.split('\|',i)[2]);
		more=float(re.split('\|',i)[3]);
		
		gs.mapcalc('{a} = x() - {b}'.format(a='px',b=xcoor));
		gs.mapcalc('{a} = y() - {b}'.format(a='py',b=ycoor));
		gs.mapcalc('{a} = sqrt((({b})^2) + (({c})^2))'.format(a='dist_or',b='px',c='py'));
		m_u= float(high) + pala_scal;
		m_l= float(high);
		m_h= (m_u * 0.5) + (m_l * 0.5);
		moree= more + m_h;
		coordinate=str(xcoor)+','+str(ycoor);
		
		gs.run_command('r.viewshed',input=dem,output='step_up',coordinates=coordinate,observer_elevation=m_u,max_dist=f);		
		gs.run_command('r.viewshed',input=dem,output='step_low',coordinates=coordinate,observer_elevation=m_l,max_dist=f);		
		gs.run_command('r.viewshed',input=dem,output='step_half',coordinates=coordinate,observer_elevation=m_h,max_dist=f);		
		gs.mapcalc('{a} = sqrt(((abs({b}+{c}-{d}))^2)+(({e})^2))'.format(a='dist_up',b=more,c=m_u,d=dem,e='dist_or'));		
		gs.mapcalc('{a} = sqrt(((abs({b}+{c}-{d}))^2)+(({e})^2))'.format(a='dist_low',b=more,c=m_l,d=dem,e='dist_or'));		
		gs.mapcalc('{a} = sqrt(((abs({b}-{c}))^2)+(({d})^2))'.format(a='dist_half',b=moree,c=dem,d='dist_or'));	
		gs.mapcalc('{a} = {b}-{c}'.format(a='gamma_up',b='step_half',c='step_up'));		
		gs.mapcalc('{a} = {b}-{c}'.format(a='gamma_low',b='step_low',c='step_half'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*tan({e}),{f}*tan({g}))'.format(a='half_len',b=dem,c=moree,d='dist_half',e='gamma_low',f='dist_half',g='gamma_up'));		
		gs.mapcalc('{a} = if({b} <= {c}, abs({d}+{e}-{f}), abs({g}+{h}-{f}))'.format(a='disl',b=dem,c=moree,d=more,e=m_l,f=dem,g=more,h=m_u));		
		gs.mapcalc('{a} = sqrt((({b})^2)+(({c})^2))*({d}/{e})'.format(a='c_1',b='disl',c='dist_or',d='gamma_low',e='gamma_low'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*cos({e}), {f}*cos({g}))'.format(a='h_1',b=dem,c=moree,d='c_1',e='gamma_low',f='c_1',g='gamma_up'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}, {e}/cos({f}))'.format(a='r',b=dem,c=moree,d='c_1',e='h_1',f='gamma_low'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}, {d}*{e}/{f})'.format(a='pala',b=dem,c=moree,d=pala_scal,e='r',f='dist_low'));		
		gs.mapcalc('{a} = {b}*{c}/{d}'.format(a='base_1',b='half_len',c='h_1',d='dist_half'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*tan({e}), {f}*tan({g}))'.format(a='base_2',b=dem,c=moree,d='h_1',e='gamma_up',f='h_1',g='gamma_low'));		
		gs.mapcalc('{a} = {b}+{c}'.format(a='len',b='base_1',c='base_2'));
		gs.mapcalc('{a} = {b}*{c}*{d}/2'.format(a=str(h)+'area_semi',b=math.pi,c='len',d='pala'));
		
		m_l= float(high) - pala_scal;
		m_h= float(high);
		moree= more + m_h;

		gs.run_command('r.viewshed',input=dem,output='step_up',coordinates=coordinate,observer_elevation=m_u,max_dist=f);		
		gs.run_command('r.viewshed',input=dem,output='step_low',coordinates=coordinate,observer_elevation=m_l,max_dist=f);		
		gs.run_command('r.viewshed',input=dem,output='step_half',coordinates=coordinate,observer_elevation=m_h,max_dist=f);		
		gs.mapcalc('{a} = sqrt(((abs({b}+{c}-{d}))^2)+(({e})^2))'.format(a='dist_up',b=more,c=m_u,d=dem,e='dist_or'));
		gs.mapcalc('{a} = sqrt(((abs({b}+{c}-{d}))^2)+(({e})^2))'.format(a='dist_low',b=more,c=m_l,d=dem,e='dist_or'));		
		gs.mapcalc('{a} = sqrt(((abs({b}-{c}))^2)+(({d})^2))'.format(a='dist_half',b=moree,c=dem,d='dist_or'));		
		gs.mapcalc('{a} = {b}-{c}'.format(a='gamma_up1',b='step_half',c='step_up'));		
		gs.mapcalc('{a} = {b}-{c}'.format(a='gamma_low',b='step_low',c='step_half'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*tan({e}),{f}*tan({g}))'.format(a='half_len',b=dem,c=moree,d='dist_half',e='gamma_low',f='dist_half',g='gamma_up1'));		
		gs.mapcalc('{a} = if({b} <= {c}, abs({d}+{e}-{b}), abs({d}+{f}-{b}))'.format(a='disl',b=dem,c=moree,d=more,e=m_l,f=m_u));		
		gs.mapcalc('{a} = sqrt((({b})^2)+(({c})^2))*({d}/{e})'.format(a='c_2',b='disl',c='dist_or',d='gamma_low',e='gamma_low'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*cos({e}), {d}*cos({f}))'.format(a='h_2',b=dem,c=moree,d='c_2',e='gamma_low',f='gamma_up1'));		
		gs.mapcalc('{a} = {b}*{c}/{d}'.format(a='pala',b=pala_scal,c='h_2',d='dist_half'));		
		gs.mapcalc('{a} = {b}*{c}/{d}'.format(a='base_1',b='half_len',c='h_2',d='dist_half'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*tan({e}), {d}*tan({f}))'.format(a='base_2',b=dem,c=moree,d='h_2',e='gamma_up1',f='gamma_low'));		
		gs.mapcalc('{a} = {b}+{c}'.format(a='len',b='base_1',c='base_2'));
		gs.mapcalc('{a} = 0.5*{b}*{c}*{d}'.format(a=str(h)+'area_elli',b=math.pi,c='len',d='pala'));

		m_l=0.0;
		m_h= m_u - pala_scal * 2;
		moree= more + m_h;
		
		gs.run_command('r.viewshed',input=dem,output='step_up',coordinates=coordinate,observer_elevation=m_u,max_dist=f);
		gs.run_command('r.viewshed',input=dem,output='step_low',coordinates=coordinate,observer_elevation=m_l,max_dist=f);		
		gs.run_command('r.viewshed',input=dem,output='step_half',coordinates=coordinate,observer_elevation=m_h,max_dist=f);		
		gs.mapcalc('{a} = sqrt(({b}+{c}-{d})^2+({e})^2)'.format(a='dist_up',b=more,c=m_u,d=dem,e='dist_or'));		
		gs.mapcalc('{a} = sqrt(({b}+{c}-{d})^2+({e})^2)'.format(a='dist_low',b=more,c=m_l,d=dem,e='dist_or'));		
		gs.mapcalc('{a} = sqrt(({b}-{c})^2+({d})^2)'.format(a='dist_half',b=moree,c=dem,d='dist_or'));		
		gs.mapcalc('{a} = {b}-{c}'.format(a='gamma_up2',b='step_half',c='step_up'));
		gs.mapcalc('{a} = {b}-{c}'.format(a='gamma_low2',b='step_low',c='step_half'));
		gs.mapcalc('{a} = if({b} <= {c}, {d}*tan({e}),{d}*tan({f}))'.format(a='half_len',b=dem,c=moree,d='dist_half',e='gamma_low2',f='gamma_up2'));
		gs.mapcalc('{a} = if({b} <= {c}, abs({d}+{e}-{b}), abs({d}+{f}-{b}))'.format(a='disl',b=dem,c=moree,d=more,e=m_l,f=m_u));	
		gs.mapcalc('{a} = sqrt(({b})^2+({c})^2)*({d}/{e})'.format(a='c_3',b='disl',c='dist_or',d='gamma_low',e='gamma_low'));	
		gs.mapcalc('{a} = if({b} <= {c}, {d}*cos({e}), {d}*cos({f}))'.format(a='h',b=dem,c=moree,d='c_3',e='gamma_low2',f='gamma_up2'));	
		gs.mapcalc('{a} = sqrt(({b}+{c}-{d})^2+({e})^2)'.format(a='dist_centro_ellisse',b=moree,c=pala_scal,d=dem,e='dist_or'));	
		gs.mapcalc('{a} = {b}*{c}/{d}'.format(a='base_1',b='half_len',c='h',d='dist_half'));	
		gs.mapcalc('{a} = if({b} <= {c}, {d}*tan({e}), {d}*tan({f}))'.format(a='base_2',b=dem,c=moree,d='h',e='gamma_up2',f='gamma_low2'));		
		gs.mapcalc('{a} = ({b}/{c})*if({d} <= {e}, 0.5*{f}, 0.5*{g})'.format(a='h_3',b='dist_centro_ellisse',c=pala_scal,d=dem,e=moree,f='base_2',g='base_1'));		
		gs.mapcalc('{a} = {b}*{c}/{d}'.format(a='pala',b=pala_scal,c='h_3',d='dist_centro_ellisse'));		
		gs.mapcalc('{a} = if({b} <= {c}, {d}*0.5, {e}*0.5)'.format(a='semiasse_ell',b=dem,c=moree,d='base_2',e='base_1'));		
		gs.mapcalc('{a} = ({b}*{c}*{d})+(({e}*(3+{f}/{g}))*{f}*0.5)'.format(a=str(h)+'area_composta',b=math.pi,c='semiasse_ell',d='pala',e=scal,f=m_h,g=high));
		
		patch_aree=str(h)+'area_composta'+','+str(h)+'area_elli'+','+str(h)+'area_semi';
		
		gs.run_command('r.patch',flags='z',input=patch_aree,output=str(h)+'tot_area');
		gs.run_command('r.null',map=str(h)+'tot_area',null='0');
		gs.run_command('r.patch',input='c_3,c_2,c_1',output=str(h)+'tot_distance');
		gs.run_command('r.null',map=str(h)+'tot_distance',null='3000000');
		if h == n :
			bibidi=bibidi+str(h)+'tot_distance';
			bobidi=bobidi+str(h)+'tot_area';
		else:
			bibidi=bibidi+str(h)+'tot_distance'+',';
			bobidi=bobidi+str(h)+'tot_area'+',';
		h= h + 1;
	
	gs.mapcalc('{a} = min({b})'.format(a='dist_min',b=bibidi));
	gs.run_command('r.null',map='dist_min',setnull='3000000');
	gs.mapcalc('{a} = 4*{b}*{c}^2'.format(a='fov',b=math.pi,c='dist_min'));
	gs.mapcalc('{a} = 0'.format(a='area'));
	gs.mapcalc('{a} = 0'.format(a='what_map'));
	gs.mapcalc('{a} = 0'.format(a='area_others'));

	bu=[];
	for i in b:
		z= 0;
		t= 1;
		cat=int(re.split('\|',i)[0]);
		gs.mapcalc('{a} = if(min({b}) == {c}, {d},{e})'.format(a='what_map',b=bibidi,c=str(cat)+'tot_distance',d=cat,e='what_map'));		
		for z in re.split(',',bibidi):
			gs.run_command('r.null',map=z,setnull='3000000');
			gs.run_command('r.null',map=z,null='0');
			bu.append(z);
		z= 0;
		c=bu[:];
		for z in c:
			del c[cat-1];
			del c[n-1:];
			gs.mapcalc('{a} = {a}+({b}*{c}/{d})'.format(a='area_others',b=z,c=str(cat)+'tot_area',d=str(cat)+'tot_distance'));
			c=bu[:];
		gs.mapcalc('{a} = if({b} = {c},{a}+{d},{a}+{e})'.format(a='area',b='what_map',c=cat,d=str(cat)+'tot_area',e='area_others'));
	
	gs.mapcalc('{a} = {b}/{c}'.format(a='pre',b='area',c='fov'));	

	gs.run_command('v.to.rast',input=input,output='out',use='cat',type='point',layer='1',value='1');
	
	gs.mapcalc('{a} = abs(if(isnull({b}),if({c} < 1,{c}*100,100),0))'.format(a=impact,b='out',c='pre'));
	
	gs.run_command('r.null',map=impact,setnull='0');
	
	gs.run_command('g.remove',flags='f',type='raster', name='out,pre,area,area_others,base_1,base_2,c_1,c_2,c_3,disl,dist_centro_ellisse,dist_half,dist_low,dist_or,dist_min,dist_up,fdem,fov,gamma_low,gamma_low2,gamma_up,gamma_up1,gamma_up2,h,h_1,h_2,h_3,half_len,len,pala,px,py,r,semiasse_ell,step_half,step_low,step_up,what_map');
	
	gs.run_command('g.remove',flags='f',type='vector', name='areas,buf3,buf5,buf7,face,face_model,line,line_model,pointD');
	
	for i in b:
		num=str(re.split('\|',i)[0]);
		r2remove=num+'area_composta'+','+num+'area_elli'+','+num+'area_semi'+','+num+'tot_area'+','+num+'tot_distance';
		v2remove='palo_linee_'+num+','+'palo_facce_'+num;
		gs.run_command('g.remove',flags='f',type='raster', name=r2remove);
		gs.run_command('g.remove',flags='f',type='vector',name=v2remove);
	
if __name__ == "__main__":
    options, flags = gs.parser();
    sys.exit(main())
