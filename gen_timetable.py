# Copyright (C) 2018 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.

import re
import pandas as pd
import numpy as np

# example structured data input to generate timetable
tt_info = {'Intelligent Systems [CC306]': [
                'AI',
                ['Wednesday : 09:30 to 11:00 - KL Block B - C Lab M - [Network/Mobile Lab]'],
                 ['Wednesday : 11:00 to 12:30 - KL Block B - C Lab M - [Network/Mobile Lab] ]']],
            'Network Security Design [CC312]': [
                'NSD',
                ['Monday : 11:00 to 12:30 - KL Block B - C Lab B - [COMPUTER LAB B]]'],
                ['Monday : 14:00 to 15:30 - KL Block B - C Lab A - [COMPUTER LAB A]]']],
            'Programming Model [CC303]': [
                'PM',
                ['Tuesday : 09:30 to 11:00 - KL Block B - C Lab B - [COMPUTER LAB B]',
                 'Wednesday : 14:00 to 15:30 - KL Block B - C Lab M - [Network/Mobile Lab]'],
                ['Tuesday : 12:30 to 14:00 - KL Block B - C Lab M - [Network/Mobile Lab]']],
            'Operating Systems & Networks [CD214]': [
                'OSN',
                ['Tuesday : 14:00 to 15:30 - KL Block B - C Lab B - [COMPUTER LAB B]',
                 'Thursday : 08:00 to 09:30 - KL Block B - C Lab C - [COMPUTER LAB C]'],
                ['Thursday : 11:00 to 12:30 - KL Block B - C Lab B - [COMPUTER LAB B]']]
            }

fname_out_excel = 'timetable.xlsx'
fname_out_html = 'timetable.html' # this is much more beautiful/useful

dayOfWeek = r"(Monday|Tuesday|Wednesday|Thursday|Friday)"
timeOfDay = r"([0-9][0-9]):([0-9][0-9])"
whichLab = r"(Lab [ABCM])" # Lab A, Lab B, Lab C or Lab M
pattern_search = dayOfWeek + " : " + timeOfDay + " to " + timeOfDay +  " - KL Block B - C " + whichLab
reObj = re.compile(pattern_search)

# from 8am to 8pm with 30 mins increments
time_class_start = np.arange(8, 20, 0.5)

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

arr_tt = pd.DataFrame(index=time_class_start, columns=days)

def parse_info_str(reObj, ss):
    match_obj = reObj.search(ss)
    day_found = match_obj.group(1)
    # make sure to make it a proper float value that is calculatable. E.g. '10:30' to 10.50, '2:00' to 2.00
    start_time_found = float(match_obj.group(2) + '.' + ('50' if match_obj.group(3) == '30' else '00'))
    # make sure to make it a proper float value that is calculatable. E.g. '10:30' to 10.50, '2:00' to 2.00
    end_time_found = float(match_obj.group(4) + '.' + ('50' if match_obj.group(5) == '30' else '00'))
    venue_found = match_obj.group(6)
    return day_found, start_time_found, end_time_found, venue_found

for v in tt_info:
    print('Processing subject: ' + v)

    shortname_cur_subj = tt_info[v][0]
    lecs_cur_subj = tt_info[v][1]
    tuts_cur_subj = tt_info[v][2]

    # process each lecture
    for lec in lecs_cur_subj:
        (day_found, start_time_found, end_time_found, venue_found) = parse_info_str(reObj, lec)
        str_cell = "{} Lec ({})".format(shortname_cur_subj, venue_found)
        arr_tt.loc[start_time_found:(end_time_found-0.5), day_found] = str_cell

    # process each tutorial
    for tut in tuts_cur_subj:
        (day_found, start_time_found, end_time_found, venue_found) = parse_info_str(reObj, tut)
        str_cell = "{} Tut ({})".format(shortname_cur_subj, venue_found)
        arr_tt.loc[start_time_found:(end_time_found-0.5), day_found] = str_cell

# convert all the cell entries to string (since a lot them are 'nan' float types)
arr_tt = arr_tt.astype(str)

# write to excel format
arr_tt.to_excel(fname_out_excel)

render_html = ['''
<html>
    <head>
        <title>Timetable for current semester</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
        <div class="container">
    </head>
    <body>
        <h1>Timetable for the current semester</h1>
        <table class="table table-striped table-bordered table-hover">
            <tr>
                <th>Time</th>
''']

for day in days:
    render_html.append('<th>{}</th>'.format(day))
render_html.append('</tr>')

# write each row
for rr in time_class_start:
    render_html.append('<tr>')
    if rr % 1 == 0: # if whole number
        render_html.append('<td>{:g}-{:g}:30</td>'.format(rr, rr))
    else: # if not whole number: i.e. x.50 which is supposed to mean some hour & 30 minutes
        render_html.append('<td>{:g}:30-{:g}</td>'.format(np.floor(rr), rr+0.5)) #
    for day in days:
        val_cell = arr_tt.loc[rr, day]
        if val_cell == 'nan':
            render_html.append('<td></td>')
        else:
            render_html.append('<td>{}</td>'.format(val_cell))
    render_html.append('</tr>')

render_html.append('</table>')
render_html.append('</div>')
render_html.append('</body>')
render_html.append('</html>')

with open(fname_out_html, 'w') as fout:
    fout.write(''.join(render_html))



