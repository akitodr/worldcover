import pandas as pd

def xiaoline(x0, y0, x1, y1):

        x=[]
        y=[]
        dx = x1-x0
        dy = y1-y0
        steep = abs(dx) < abs(dy)

        if steep:
            x0,y0 = y0,x0
            x1,y1 = y1,x1
            dy,dx = dx,dy

        if x0 > x1:
            x0,x1 = x1,x0
            y0,y1 = y1,y0

        gradient = float(dy) / float(dx)  # slope

        """ handle first endpoint """
        xend = round(x0)
        yend = y0 + gradient * (xend - x0)
        xpxl0 = int(xend)
        ypxl0 = int(yend)
        x.append(xpxl0)
        y.append(ypxl0) 
        x.append(xpxl0)
        y.append(ypxl0+1)
        intery = yend + gradient

        """ handles the second point """
        xend = round (x1)
        yend = y1 + gradient * (xend - x1)
        xpxl1 = int(xend)
        ypxl1 = int (yend)
        x.append(xpxl1)
        y.append(ypxl1) 
        x.append(xpxl1)
        y.append(ypxl1 + 1)

        """ main loop """
        for px in range(xpxl0 + 1 , xpxl1):
            x.append(px)
            y.append(int(intery))
            x.append(px)
            y.append(int(intery) + 1)
            intery = intery + gradient

        if steep:
            y,x = x,y

        coords=zip(x,y)

        return coords


def read_from_file(path):
    file = pd.read_csv(path, sep=';')
    df = pd.DataFrame(file)
    df = df.reset_index()

    return df