# About this branch:

This are the Windows omologue versions of r.wind.py and r.photovoltaic.py 

Some minor changes are done with respect to the Linux/MacOS version: r.univar in r.photovoltaic.py is commented since it was a blocking command, "r" character is added both in r.wind and r.photovoltaic before the escape character ("\") in r.split execution.

----------------------------------------------------------------------------

A bit of history:

# r.wind.sun
r.wind.sun implements a method to calculate visibility of aerogenerators and photovoltaic panels using an impact index. 

More information regarding method conceived here: https://researchportal.port.ac.uk/portal/files/8108007/An_Open_Source_GIS_Tool.pdf . 

This code is optimized for GRASS GIS 64, and it is also included in official addons: https://svn.osgeo.org/grass/grass-addons/grass6/raster/r.wind.sun/r.wind.sun.py . 

If you use this work for academic and/or professional purposes please cite: 
Minelli, A., Marchesini, I., Taylor, F. E., De Rosa, P., Casagrande, L., &amp; Cenci, M. (2014). An open source GIS tool to quantify the visual impact of wind turbines and photovoltaic panels. Environmental Impact Assessment Review, 49, 70-78. https://doi.org/10.1016/j.eiar.2014.07.002

# r.photovoltaic
r.photovoltaic updates r.wind.sun code to be used in GRASS GIS 8 for the part limited to photovoltaic panels. The code is in alpha version, but all the functionalities of r.wind.sun have been updated and this specific part (photovoltaic panels visibility impact) has been recently used to evauate visibility in two study cases: (i) for new soil lost in Italy in 2023, in the frame of the last Soil consumption report (https://www.snpambiente.it/temi/suolo/consumo-di-suolo-dinamiche-territoriali-e-servizi-ecosistemici-edizione-2024/) and (ii) for existing and potential aquaculture facilites within Gaeta Gulf (Italy). 

# r.wind
r.wind updates r.wind.sun code to be used in GRASS GIS 8 for the part limited to aerogenerators. The code is in alpha version, but all the functionalities of r.wind.sun have been updated. The code has been successfully tested using the same .txt file (https://github.com/annalisapg/r.wind.sun/blob/master/inputfile.txt) previously used as wind turbine model in the old version of the code.
