import numpy as np
import glob
import os

############################################
# bookkeeping items

basedir = './'

monthlabs = ['01Jan','02Feb','03Mar','04Apr','05May','06Jun','07Jul','08Aug','09Sep','10Oct','11Nov','12Dec']
monthnums = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0]

RH_year_num_map = {'1': '2001',
                   '2': '2002',
                   '3': '2003',
                   '4': '2004',
                   '5': '2005',
                   '6': '2006',
                   '7': '2007',
                   '8': '2008',
                   '9': '2009',
                   '10':'2010',
                   '11':'2011',
                   '12':'2012',
                   '13':'2013',
                   '14':'2014',
                   '15':'2015',
                   '16':'2016',
                   '17':'2017',
                   '18':'2018',
                   '19':'2019',
                   '20':'2020',
                   '21':'2021',
                   '22':'2022',
                   '23':'2023',
                   '24':'2024',
                   '25':'2025',}

exceptions = np.array(['PV','PDB'])
replacements = np.array(['IRAM','NOEMA'])

############################################
# combing through files

stationlist = np.sort(glob.glob(basedir+'*'))
stationlist = stationlist[(stationlist != basedir+'import_csv.py') & (stationlist != basedir+'weather_data')]

for stationhere in stationlist:

    ############################################
    # reading

    print('Reading inputs for ' + stationhere + '...')

    # get the list of files and sort it alphabetically
    filelist = np.sort(glob.glob(stationhere+'/*.err'))

    # initialize lists to track desired info
    years = list()
    months = list()
    days = list()
    segments = list()
    Pbases = list()
    Tbases = list()
    PWVs = list()

    # loop through each file in the list
    for filename in filelist:

        # extract the date and time information from the filename
        timestr = filename.split(".")[-2].split("/")[-1]
        yearstr = timestr[0:4]
        monthstr = timestr[4:6]
        daystr = timestr[6:8]
        segstr = timestr[-1]
        years.append(yearstr)
        months.append(monthstr)
        days.append(daystr)
        segments.append(segstr)

        # read the file
        lines = open(filename, 'r').readlines()
        for iline, line in enumerate(lines[::-1]):
            if 'z = 0.0' in line:
                linehere = line
                lineprev = lines[-iline]
                break
        for iline, line in enumerate(lines[::-1]):
            if '# total' in line:
                linetot = lines[-iline+2]
                break

        # extract the Pbase, Tbase, and PWV
        Pbase = float(linehere.split(' ')[1])
        Tbase = float(lineprev.split(' ')[1])
        PWV = float(linetot.split("(")[1].split(" ")[0]) / 1000.0
        Pbases.append(Pbase)
        Tbases.append(Tbase)
        PWVs.append(PWV)

    years = np.array(years)
    months = np.array(months)
    days = np.array(days)
    segments = np.array(segments)
    Pbases = np.array(Pbases)
    Tbases = np.array(Tbases)
    PWVs = np.array(PWVs)

    ############################################
    # writing

    print('Writing outputs for ' + stationhere + '...')

    for imonth, month in enumerate(monthlabs):

        # create directory
        if stationhere not in exceptions:
            pathname = './weather_data/'+stationhere+'/'+month+'/'
            statname = stationhere
        else:
            statname = replacements[exceptions == stationhere][0]
            pathname = './weather_data/'+statname+'/'+month+'/'
        os.makedirs(pathname,exist_ok=True)

        ############################################
        # write file with Pbase info (full)

        # write the file
        with open(pathname+'Pbase.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'segment'.ljust(16)
            strhere += 'Pbase (mbar)'.ljust(20)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'segment' + ','
            strhere += 'Pbase' + '\n'
            f.write(strhere)

            # table
            for i in range(len(Pbases)):
                strhere = ''
                strhere += str(int(years[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(days[i])) + ','
                strhere += str(int(segments[i])) + ','
                strhere += str(Pbases[i]) + '\n'
                f.write(strhere)

        ############################################
        # write file with Pbase info (mean)

        # averaging over segments
        ys = np.unique(years)
        ds = np.unique(days)
        yearlist = list()
        daylist = list()
        Pbaselist = list()
        for y in ys:
            for d in ds:
                indhere = ((years == y) & (days == d))
                if (indhere.sum() > 0):
                    yearlist.append(y)
                    daylist.append(d)
                    Pbaselist.append(np.nanmean(Pbases[indhere]))

        # write the file
        with open(pathname+'mean_Pbase.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'Pbase (mbar)'.ljust(20)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'Pbase' + '\n'
            f.write(strhere)

            # table
            for i in range(len(Pbaselist)):
                strhere = ''
                strhere += str(int(yearlist[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(daylist[i])) + ','
                strhere += str(np.round(Pbaselist[i],8)) + '\n'
                f.write(strhere)

        ############################################
        # write file with Tbase info (full)

        # write the file
        with open(pathname+'Tbase.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'segment'.ljust(16)
            strhere += 'Tbase (K)'.ljust(20)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'segment' + ','
            strhere += 'Tbase' + '\n'
            f.write(strhere)

            # table
            for i in range(len(Tbases)):
                strhere = ''
                strhere += str(int(years[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(days[i])) + ','
                strhere += str(int(segments[i])) + ','
                strhere += str(Tbases[i]) + '\n'
                f.write(strhere)

        ############################################
        # write file with Tbase info (mean)

        # averaging over segments
        ys = np.unique(years)
        ds = np.unique(days)
        yearlist = list()
        daylist = list()
        Tbaselist = list()
        for y in ys:
            for d in ds:
                indhere = ((years == y) & (days == d))
                if (indhere.sum() > 0):
                    yearlist.append(y)
                    daylist.append(d)
                    Tbaselist.append(np.nanmean(Tbases[indhere]))

        # write the file
        with open(pathname+'mean_Tbase.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'Tbase (K)'.ljust(20)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'Tbase' + '\n'
            f.write(strhere)

            # table
            for i in range(len(Tbaselist)):
                strhere = ''
                strhere += str(int(yearlist[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(daylist[i])) + ','
                strhere += str(np.round(Tbaselist[i],8)) + '\n'
                f.write(strhere)

        ############################################
        # write file with PWV info (full)

        # write the file
        with open(pathname+'PWV.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'segment'.ljust(16)
            strhere += 'PWV (mm)'.ljust(20)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'segment' + ','
            strhere += 'PWV' + '\n'
            f.write(strhere)

            # table
            for i in range(len(PWVs)):
                strhere = ''
                strhere += str(int(years[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(days[i])) + ','
                strhere += str(int(segments[i])) + ','
                strhere += str(PWVs[i]) + '\n'
                f.write(strhere)

        ############################################
        # write file with PWV info (mean)

        # averaging over segments
        ys = np.unique(years)
        ds = np.unique(days)
        yearlist = list()
        daylist = list()
        PWVlist = list()
        for y in ys:
            for d in ds:
                indhere = ((years == y) & (days == d))
                if (indhere.sum() > 0):
                    yearlist.append(y)
                    daylist.append(d)
                    PWVlist.append(np.nanmean(PWVs[indhere]))

        # write the file
        with open(pathname+'mean_PWV.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'PWV (mm)'.ljust(20)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'PWV' + '\n'
            f.write(strhere)

            # table
            for i in range(len(PWVlist)):
                strhere = ''
                strhere += str(int(yearlist[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(daylist[i])) + ','
                strhere += str(np.round(PWVlist[i],8)) + '\n'
                f.write(strhere)
