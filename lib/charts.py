import logging


def add_array_chart(workbook, sheet, range, title):

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': title})
    chart.set_y_axis({
        'name': 'GBytes',
        'num_format': '#,##0',
    })

    chart.add_series({
        'name': 'Total Used After Optimization',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['total'][0], range['total'][1], range['total'][2], range['total'][3]],
        'line': {'width': 2},
    })
    chart.add_series({
        'name': 'Snapshots',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['snapshots'][0], range['snapshots'][1], range['snapshots'][2], range['snapshots'][3]],
        'line': {'width': 2},
    })
    chart.add_series({
        'name': 'Provisioned',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['provisioned'][0], range['provisioned'][1], range['provisioned'][2], range['provisioned'][3]],
        'line': {'width': 2},
    })
    chart.add_series({
        'name': 'Capacity',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['capacity'][0], range['capacity'][1], range['capacity'][2], range['capacity'][3]],
        'line': {'width': 2},
    })

    return chart



def add_hgroup_chart(workbook, sheet, range, title):

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': title})
    chart.set_y_axis({
        'name': 'GBytes',
        'num_format': '#,##0',
    })

    chart.add_series({
        'name': 'Total',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['total'][0], range['total'][1], range['total'][2], range['total'][3]],
        'line': {'width': 2},
    })
    chart.add_series({
        'name': 'Snapshots',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['snapshots'][0], range['snapshots'][1], range['snapshots'][2], range['snapshots'][3]],
        'line': {'width': 2},
    })
    chart.add_series({
        'name': 'Provisioned',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['size'][0], range['size'][1], range['size'][2], range['size'][3]],
        'line': {'width': 2},
    })

    return chart


def add_hgroup_vol_size_chart(workbook, sheet, range, title):

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': title})
    chart.set_y_axis({
        'name': 'GBytes',
        'num_format': '#,##0',
    })

    for vol in range:
        series_title = vol + ' Used'
        chart.add_series({
            'name': series_title,
            'categories': [sheet, range[vol]['dates'][0], range[vol]['dates'][1], range[vol]['dates'][2],
                           range[vol]['dates'][3]],
            'values': [sheet, range[vol]['total'][0], range[vol]['total'][1], range[vol]['total'][2],
                       range[vol]['total'][3]],
            'line': {'width': 2},
        })
    return chart


def add_hgroup_vol_snapshot_chart(workbook, sheet, range, title):

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': title})
    chart.set_y_axis({
        'name': 'GBytes',
        'num_format': '#,##0',})

    for vol in range:
        series_title = vol + ' Snapshots'
        chart.add_series({
            'name': series_title,
            'categories': [sheet, range[vol]['dates'][0], range[vol]['dates'][1], range[vol]['dates'][2],
                           range[vol]['dates'][3]],
            'values': [sheet, range[vol]['snapshots'][0], range[vol]['snapshots'][1], range[vol]['snapshots'][2],
                       range[vol]['snapshots'][3]],
            'line': {'width': 2},
        })
    return chart


def add_exec_chart(workbook, sheet, range, title):

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': title})
    chart.set_y_axis({
        'name': 'GBytes',
        'num_format': '#,##0',
    })

    #'num_format': '#,##0',

    chart.add_series({
        'name': 'Total Used After Optimization',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['total'][0], range['total'][1], range['total'][2], range['total'][3]],
        'line': {'width': 2}
    })

    chart.add_series({
        'name': 'Snapshots',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['snapshots'][0], range['snapshots'][1], range['snapshots'][2], range['snapshots'][3]],
        'line': {'width': 2}
    })

    chart.add_series({
        'name': 'Total Provisioned',
        'categories': [sheet, range['dates'][0], range['dates'][1], range['dates'][2], range['dates'][3]],
        'values': [sheet, range['size'][0], range['size'][1], range['size'][2], range['size'][3]],
        'line': {'width': 2}
    })

    return chart






