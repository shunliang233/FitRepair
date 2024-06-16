import gpxpy

with open('_11_Bus(igp).gpx', 'r', encoding='utf-8') as f:
    gpx = gpxpy.parse(f)
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print(type(point.latitude))
            print(type(point.longitude))
            print(type(point.elevation))
            print(type(point.time))
            print(point.time)
            print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevation}')