points = {'Ed': 0, 'Hhjjn': 1, 'Jean': 4}

print([k for k, v in points.items() if v == max(points.values())][0])
