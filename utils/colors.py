from PyQt6.QtGui import QColor

def darken_color(color: QColor, percentage: float) -> QColor:
    red = color.red()
    green = color.green()
    blue = color.blue()
    
    darkened_red = int(max(0, red/percentage))
    darkened_green = int(max(0, green/percentage))
    darkened_blue = int(max(0, blue/percentage))

    return QColor(darkened_red, darkened_green, darkened_blue)
    
def lighten_color(color: QColor, percentage: float) -> QColor:
    red = color.red()
    green = color.green()
    blue = color.blue()
    
    darkened_red = int(min(red*(1+(percentage/100)), 255))
    darkened_green = int(min(green*(1+(percentage/100)), 255))
    darkened_blue = int(min(blue*(1+(percentage/100)), 255))

    return QColor(darkened_red, darkened_green, darkened_blue)
