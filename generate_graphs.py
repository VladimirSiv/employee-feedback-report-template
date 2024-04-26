import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


def radar_factory(num_vars, frame='circle'):
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def draw(self, renderer):
            if frame == 'polygon':
                gridlines = self.yaxis.get_gridlines()
                for gl in gridlines:
                    gl.get_path()._interpolation_steps = num_vars
            super().draw(renderer)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)

                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def draw_radar_graph(data, img_name) -> None:
    N = len(data[0])
    theta = radar_factory(N, frame='polygon')

    spoke_labels = data.pop(0)
    title, case_data = data[0]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=1, bottom=0)

    ax.set_rgrids([0.2, 0.4, 0.6, 0.8])

    for d in case_data:
        line = ax.plot(theta, d)
        ax.fill(theta, d,  alpha=0.25)
        ax.plot(0.1, 0.1, 'ro', alpha=0)
    ax.set_varlabels(spoke_labels)

    fig.tight_layout()
    plt.savefig(f'{img_name}.png', dpi=300)


if __name__ == "__main__":
    hard_skills_radar_graph_data = [
        [
            'Coding',
            'System Design',
            'Debugging',
            'Testing',
            'Cloud',
            'Documentation',
            'Code Review',
            'Theory',
        ],
        (
            'Hard Skills', [[0.2, 0.3, 0.4, 0.8, 0.4, 0.9, 0.7, 1]]
        )
    ]
    soft_skills_radar_graph_data = [
        [
            'Teamwork',
            'Problem-Solving',
            'Adaptability',
            'Motivation',
            'Time Management',
            'Communication',
            'Proactivity',
            'Attention to Detail',
        ],
        (
            'Soft Skills', [[1, 0.3, 0.5, 0.7, 0.2, 0.1, 0.8, 1]]
        )
    ]
    draw_radar_graph(soft_skills_radar_graph_data, "soft_skills_radar_graph")
    draw_radar_graph(hard_skills_radar_graph_data, "hard_skills_radar_graph")

