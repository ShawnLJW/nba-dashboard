import numpy as np
import plotly.express as px

def ellipse_arc(x_center=0.0, y_center=0.0, a=10.5, b=10.5, start_angle=0.0, end_angle=2 * np.pi, N=200, closed=False):
    t = np.linspace(start_angle, end_angle, N)
    x = x_center + a * np.cos(t)
    y = y_center + b * np.sin(t)
    path = f'M {x[0]}, {y[0]}'
    for k in range(1, len(t)):
        path += f'L{x[k]}, {y[k]}'
    if closed:
        path += ' Z'
    return path

court = [   
    # paint
    dict(
        type="rect", x0=-80, y0=-47.5, x1=80, y1=137.5, layer='below'
    ),
    dict(
        type="rect", x0=-60, y0=-47.5, x1=60, y1=137.5, layer='below'
    ),
    
    # Free throw circle
    dict(
        type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y", layer='below'
    ),
    dict(
        type="line", x0=-60, y0=137.5, x1=60, y1=137.5, layer='below'
    ),

    # rim
    dict(
        type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
        line=dict(color="#ec7607", width=2),
    ),
    
    #backboard
    dict(
        type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5
    ),
    
    # three point line
    dict(
        type="path", path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101), layer='below'
    ),
    dict(
        type="line", x0=-220, y0=-47.5, x1=-220, y1=92.5, layer='below'
    ),
    dict(
        type="line", x0=220, y0=-47.5, x1=220, y1=92.5, layer='below'
    ),
    dict(
        type="line", x0=-250, y0=227.5, x1=-220, y1=227.5, layer='below'
    ),
    dict(
        type="line", x0=250, y0=227.5, x1=220, y1=227.5, layer='below'
    ),
    
    # hash marks
    dict(
        type="line", x0=-90, y0=17.5, x1=-80, y1=17.5, layer='below'
    ),
    dict(
        type="line", x0=-90, y0=27.5, x1=-80, y1=27.5, layer='below'
    ),
    dict(
        type="line", x0=-90, y0=57.5, x1=-80, y1=57.5, layer='below'
    ),
    dict(
        type="line", x0=-90, y0=87.5, x1=-80, y1=87.5, layer='below'
    ),
    dict(
        type="line", x0=90, y0=17.5, x1=80, y1=17.5, layer='below'
    ),
    dict(
        type="line", x0=90, y0=27.5, x1=80, y1=27.5, layer='below'
    ),
    dict(
        type="line", x0=90, y0=57.5, x1=80, y1=57.5, layer='below'
    ),
    dict(
        type="line", x0=90, y0=87.5, x1=80, y1=87.5, layer='below'
    ),
    
    # No foul line
    dict(
        type="path", path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi), layer='below'
    ),

    # Center circle
    dict(
        type="path", path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi), layer='below'
    ),
]

def plot_shotchart(shots):
    fig = px.scatter(
        x=shots['LOC_X'], y=shots['LOC_Y']
    )
    fig.update_layout(margin={'l':0, 'r':0, 't':0, 'b':0}, plot_bgcolor="white", shapes=court)
    fig.update_xaxes(range=[-250, 250], visible=False)
    fig.update_yaxes(range=[-47.5, 422.5], visible=False)
    return fig