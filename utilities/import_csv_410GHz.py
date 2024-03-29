import numpy as np
import glob
import os

############################################
############################################
# reading

print('Reading inputs...')

quantities = ['tau','Tb']

# initialize dictionary
master_dict = {}

# loop through each of the weather quantities
for quantity in quantities:

    # get the list of files and sort it alphabetically
    filelist = np.sort(glob.glob(quantity+'*.txt'))

    # initialize lists to track desired info
    stationnames = list()
    years = list()
    months = list()
    days = list()
    segments = list()
    freqs = list()
    quants = list()

    # loop through each file in the list
    for filename in filelist:

        # extract the station name from the filename
        station = filename.split('.')[0].split('_')[1]

        # read in the file
        if quantity in ['RH','wind']:
            year, month, day, segment, quant = np.loadtxt(filename,unpack=True)
        elif quantity in ['tau','Tb']:
            year, month, day, segment, freq, quant = np.loadtxt(filename,unpack=True)

        # append to lists
        stationnames.append(station)
        years.append(year)
        months.append(month)
        days.append(day)
        segments.append(segment)
        if quantity in ['tau','Tb']:
            freqs.append(freq)
        quants.append(quant)

    # add info to master dictionary
    if quantity in ['RH','wind']:
        master_dict[quantity] = {'stations':stationnames,
                                 'years':years,
                                 'months':months,
                                 'days':days,
                                 'segments':segments,
                                 'quantity':quants}
    elif quantity in ['tau','Tb']:
        master_dict[quantity] = {'stations':stationnames,
                                 'years':years,
                                 'months':months,
                                 'days':days,
                                 'segments':segments,
                                 'freqs':freqs,
                                 'quantity':quants}

print('Done reading.')

############################################
############################################
# writing

print('Writing outputs...')

months = ['01Jan','02Feb','03Mar','04Apr','05May','06Jun','07Jul','08Aug','09Sep','10Oct','11Nov','12Dec']
monthnums = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0]
stations = np.unique(np.array(stationnames))

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

for imonth, month in enumerate(months):
    for station in stations:

        # create directory
        if station not in exceptions:
            pathname = './weather_data/'+station+'/'+month+'/'
            statname = station
        else:
            statname = replacements[exceptions == station][0]
            pathname = './weather_data/'+statname+'/'+month+'/'
        os.makedirs(pathname,exist_ok=True)

        # isolate the current info for tau, Tb
        ind1 = np.where(np.array(master_dict['tau']['stations']) == station)[0][0]
        ind2 = (master_dict['tau']['months'][ind1] == monthnums[imonth])
        years = master_dict['tau']['years'][ind1][ind2]
        days = master_dict['tau']['days'][ind1][ind2]
        segments = master_dict['tau']['segments'][ind1][ind2]
        freqs = master_dict['tau']['freqs'][ind1][ind2]

        ############################################
        # write file with 410 GHz SEFD info (full)

        # bookkeeping
        ind3 = (freqs == 410.0)
        yearshere = years[ind3]
        dayshere = days[ind3]
        segmentshere = segments[ind3]
        tau = master_dict['tau']['quantity'][ind1][ind2][ind3]
        Tb = master_dict['Tb']['quantity'][ind1][ind2][ind3]

        # write the file
        with open(pathname+'SEFD_info_410.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            f.write(('# Frequency: 410 GHz').ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'segment'.ljust(16)
            strhere += 'tau'.ljust(8)
            strhere += 'Tb (K)'.ljust(8)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'segment' + ','
            strhere += 'tau' + ','
            strhere += 'Tb' + '\n'
            f.write(strhere)

            # table
            for i in range(len(tau)):
                strhere = ''
                strhere += str(int(yearshere[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(dayshere[i])) + ','
                strhere += str(int(segmentshere[i])) + ','
                strhere += str(tau[i]) + ','
                strhere += str(Tb[i]) + '\n'
                f.write(strhere)

        ############################################
        # write file with 410 GHz SEFD info (mean)

        # bookkeeping
        ind3 = (freqs == 410.0)
        yearshere = years[ind3]
        dayshere = days[ind3]
        segmentshere = segments[ind3]
        tau = master_dict['tau']['quantity'][ind1][ind2][ind3]
        Tb = master_dict['Tb']['quantity'][ind1][ind2][ind3]

        # averaging over segments
        ys = np.unique(yearshere)
        ds = np.unique(dayshere)
        yearlist = list()
        daylist = list()
        taulist = list()
        Tblist = list()
        for y in ys:
            for d in ds:
                indhere = ((yearshere == y) & (dayshere == d))
                if (indhere.sum() > 0):
                    yearlist.append(y)
                    daylist.append(d)
                    taulist.append(np.nanmean(tau[indhere]))
                    Tblist.append(np.nanmean(Tb[indhere]))

        # write the file
        with open(pathname+'mean_SEFD_info_410.csv','w') as f:
            
            # header
            f.write('#'*100 + '\n')
            f.write(('# Month: '+month).ljust(99)+'#' + '\n')
            f.write(('# Station: '+statname).ljust(99)+'#' + '\n')
            f.write(('# Frequency: 410 GHz').ljust(99)+'#' + '\n')
            strhere = ''
            strhere += 'year'.ljust(8)
            strhere += 'month'.ljust(8)
            strhere += 'day'.ljust(8)
            strhere += 'tau'.ljust(8)
            strhere += 'Tb (K)'.ljust(8)
            f.write(('# Columns are: '+strhere).ljust(99)+'#' + '\n')
            f.write('#'*100+ '\n')
            strhere = ''
            strhere += 'year' + ','
            strhere += 'month' + ','
            strhere += 'day' + ','
            strhere += 'tau' + ','
            strhere += 'Tb' + '\n'
            f.write(strhere)

            # table
            for i in range(len(taulist)):
                strhere = ''
                strhere += str(int(yearlist[i])) + ','
                strhere += month[0:2] + ','
                strhere += str(int(daylist[i])) + ','
                strhere += str(np.round(taulist[i],8)) + ','
                strhere += str(np.round(Tblist[i],8)) + '\n'
                f.write(strhere)

print('Done writing.')

