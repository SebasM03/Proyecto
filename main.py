# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:16:35 2023

@author: SEB
"""
import db.db_utils as dbu
import plot.plot_utils as plotsie
import pandas as pd


sql="""SELECT 
	ov.obsValue,
	ov.obsValueID,
	ov.timePeriod,
	s.*,
	i.categoryID,
	i.FLARID,
	i.indicatorLeyendNameEN,
	i.indicatorLeyendNameES,
	i.indicatorNameEN,
	i.indicatorNameENShort,
	i.indicatorNameES,
	i.indicatorNameESShort,
	i.indicatorPropriety,
	um.unitMultValue,
	um.unitMultValueES,
	f.frequencyName,
	f.frequencyNameES,
	ra.refAreaName,
	ra.refAreaNameES,
	u.unitName,
	c.categoryName,
	dm.dataDomainName,
	dm.dataDomainPropriety,
	cat.categoryName,
	CASE 
		WHEN frequencyNameES = 'Anual' AND ISNUMERIC(timePeriod) = 1 THEN CONVERT(date, timePeriod + '-12-31') 
	    --Se verifica que sea numérico.
		WHEN frequencyNameES = 'Medio año, semestre' AND RIGHT(timePeriod, 1) = 1 AND timePeriod LIKE '%B%' THEN CONVERT(date, LEFT(timePeriod, 4) + '-06-30') 
	    --Se verifica que contenga el caracter B, y en función de último digito (para este caso #1), se genera el último día del mes Junio
		WHEN frequencyNameES = 'Medio año, semestre' AND RIGHT(timePeriod, 1) = 2 AND timePeriod LIKE '%B%' THEN CONVERT(date, LEFT(timePeriod, 4) + '-12-31') 
	    --Se verifica que contenga el caracter B, y en función de último digito (para este caso #2),  se genera el último día del mes de Diciembre
		WHEN frequencyNameES = 'Mensual' AND ISNUMERIC(RIGHT(timePeriod,2)) = 1 THEN DATEADD(DAY, 14, DATEADD(MONTH, RIGHT(timePeriod, 2) - 1, CONVERT(date, LEFT(timePeriod, 4))))
		--Se verifica que el campo sea numérico.
		WHEN frequencyNameES = 'Trimestral' AND RIGHT(timePeriod, 1) = 1 AND timePeriod LIKE '%Q%' THEN DATEADD(DAY, 30, DATEADD(MONTH, 2, CONVERT(date, LEFT(timePeriod, 4)))) 
	    --Se verifica que contenga el caracter Q, y en función de último digito (para este caso #1), se genera el último día del mes Marzo
		WHEN frequencyNameES = 'Trimestral' AND RIGHT(timePeriod, 1) = 2 AND timePeriod LIKE '%Q%' THEN DATEADD(DAY, 29, DATEADD(MONTH, 5, CONVERT(date, LEFT(timePeriod, 4)))) 
	    --Se verifica que contenga el caracter Q, y en función de último digito (para este caso #2), se genera el último día del mes Junio
		WHEN frequencyNameES = 'Trimestral' AND RIGHT(timePeriod, 1) = 3 AND timePeriod LIKE '%Q%' THEN DATEADD(DAY, 29, DATEADD(MONTH, 8, CONVERT(date, LEFT(timePeriod, 4)))) 
	    -- Se verifica que contenga el caracter Q, y en función de último digito (para este caso #3), se genera el último día del mes Septiembre 
		WHEN frequencyNameES = 'Trimestral' AND RIGHT(timePeriod, 1) = 4 AND timePeriod LIKE '%Q%' THEN DATEADD(DAY, 30, DATEADD(MONTH, 11, CONVERT(date, LEFT(timePeriod, 4)))) 
	    --Se verifica que contenga el caracter Q, y en función de último digito (para este caso #4), segenera el último día del mes Diciembre
		WHEN frequencyNameES = 'Semanal' AND ISNUMERIC(RIGHT(timePeriod, 2)) = 1 THEN DATEADD(DAY, 6, DATEADD(WEEK, RIGHT(timePeriod, 2) - 1, CONVERT(date, LEFT(timePeriod, 4)))) 
	    --Se verifica que sea numérico y en función los dos ultimos digitos se genera la fecha correspondiente a la semana, a la cual se le suman 6 días para obtener el último día de la semana.
		WHEN frequencyNameES = 'Diario' OR
	         frequencyNameES = 'Por hora' OR
	         frequencyNameES = 'Diario - Días hábiles' OR
	         frequencyNameES = 'Por minuto' AND ISNUMERIC(timePeriod) = 1 THEN CONVERT(date, timePeriod) 
		--Los casos que no son transformados dado que no pertenecen a ninguna de las condiciones previas, son almacenados como '1900-01-01' 
	    ELSE NULL END AS Fecha_Estructurada
FROM observation_value AS ov
LEFT OUTER JOIN serie AS s ON ov.serieID=s.serieID
LEFT OUTER JOIN indicator AS i ON s.indicatorID=i.indicatorID
LEFT OUTER JOIN unit_multiplier AS um ON um.unitMultID=s.unitMultID
LEFT OUTER JOIN frequency as f on f.freqID=s.freqID
LEFT OUTER JOIN reference_area as ra on ra.refAreaID=s.refAreaID
LEFT OUTER JOIN unit as u on u.unitID=s.unitID
LEFT OUTER JOIN category as c on c.categoryID=i.categoryID
LEFT OUTER JOIN data_domain as dm on dm.dataDomainID=i.dataDomainID
LEFT OUTER JOIN category as cat on cat.categoryID=i.categoryID
ORDER BY refAreaID
		,indicatorID
		,serieID
		,Fecha_Estructurada 
;"""
    
result=dbu.excecute_sql(sql)
tdf=result[['serieID','Fecha_Estructurada','obsValue','indicatorID','refAreaID']]
#tdf['Date']=pd.to_datetime(tdf['Fecha_Estructurada'],format='%Y-%m-%d')
tdf.rename(columns={"Fecha_Estructurada": "Date"}, inplace=True)
tdf = tdf.set_index(pd.to_datetime(tdf['Date'],format='%Y-%m-%d'))
tdf = tdf.sort_index()




paises=tdf['refAreaID'].unique().tolist()
indicators=tdf['indicatorID'].unique().tolist()
s_series=tdf['serieID'].unique().tolist()


for pais in paises:
     p_df=tdf[tdf['refAreaID']==pais]
     p_df=p_df[['serieID','Date','obsValue']]
     series=p_df['serieID'].unique().tolist()
     plotsie.subplots_byserie(p_df, series,'./pais_plot/'+pais)



for indicador in indicators:
     i_df=tdf[tdf['indicatorID']==indicador]
     i_df=i_df[['serieID','Date','obsValue']]
     series=i_df['serieID'].unique().tolist()
     plotsie.subplots_byserie(i_df, series,'./indicator_plot/'+indicador)
     
     
series_analytics_list=[]
for serie in s_series:    
    print(serie)
    df_stat=tdf[tdf['serieID']==serie]
    df_stat=df_stat[['serieID','Date','obsValue']]
    
    ser1 = df_stat.iloc[:,2]
    adf_r= plotsie.adfuller_test(ser1)
    print(adf_r['Es estacionaria'])
    
    dic={'serie':serie,
         'stacionary':adf_r['Es estacionaria']
         }
    series_analytics_list.append(dic) 
    
    
series_analytics_df = pd.DataFrame(series_analytics_list)   











