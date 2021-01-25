import logging
logger = logging.getLogger('array_annual')


def add_array_chart(workbook, sheet, range):
    logger.info("Adding Charts for Array")

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': sheet})

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



def add_hgroup_chart(workbook, sheet, range):
    logger.info("Adding Charts for Host Group")

    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': sheet})

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
