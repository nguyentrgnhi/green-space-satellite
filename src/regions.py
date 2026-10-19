"""Boundaries of the study regions as (longitude, latitude) polygons.

Only the boundaries that survived in the original scripts are included. The other regions (Hanoi
outskirts, Saigon city, Khanh Hoa, Seville) were drawn with the Earth Engine geometry tool and their
polygons were not saved; their results are in data/ instead.
"""

# Wider Hanoi area, from the original NDVI test script
HANOI = [[
    [105.93219657852012, 20.7211045053012],
    [105.84567924453575, 20.957259808922938],
    [105.96240898086387, 21.039313708800066],
    [105.859412154692, 21.1776771512693],
    [105.3815068812545, 21.120041394900255],
    [105.75366874648887, 20.641447195637344],
    [105.93219657852012, 20.7211045053012],
]]

SAIGON_OUTSKIRTS = [[
    [106.53572962055758, 10.900071573472225],
    [106.66069910297945, 10.914904865828035],
    [106.60579464107069, 11.000347787146893],
    [106.56048545219565, 11.019723974925313],
    [106.4601986146982, 11.146073005055541],
    [106.40183374653414, 10.984341778911014],
    [106.53572962055758, 10.900071573472225],
]]

REGIONS = {"hanoi": HANOI, "saigon_outskirts": SAIGON_OUTSKIRTS}
