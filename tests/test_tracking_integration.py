from pathlib import Path
import numpy as np
import apace as ap
from apace.tracking_integration import Tracking
from apace.plot import draw_lattice
import matplotlib.pyplot as plt


def test_quadrupole(tmp_path, plots):
    d1 = ap.Drift("D1", length=5)
    d2 = ap.Drift("D2", length=0.2)
    q = ap.Quadrupole("Q1", length=0.2, k1=1.5)
    s = ap.Sextupole("S1", length=0.4, k2=1000)
    lattice = ap.Lattice("Lattice", [d2, q, d2, s, d1])

    distribution = ap.distribution(
        5, x_dist="uniform", x_width=0.0002, delta_dist="uniform", delta_width=0.2
    )
    tracking = Tracking(lattice)
    s, trajectory = tracking.track(distribution, n_turns=2)

    if plots:
        _, ax = plt.subplots(figsize=(20, 5))
        ax.plot(s, trajectory[:, 0])
        draw_lattice(lattice, draw_sub_lattices=False)
        plt.savefig(tmp_path / "test_quadrupole.pdf")


def test_fodo_ring(tmp_path, fodo_ring, plots):
    b1 = fodo_ring["B1"]
    b1.e1 = 0
    b1.e2 = 0
    dist = ap.distribution(2, x_dist="uniform", x_width=0.001)
    tracking_mat = ap.MatrixTracking(fodo_ring, dist)
    tracking_int = Tracking(fodo_ring)
    s, trajectory = tracking_int.track(dist, max_step=0.1)

    if plots:
        plt.plot(tracking_mat.orbit_position, tracking_mat.x, "--")
        plt.gca().set_prop_cycle(None)
        plt.plot(s, trajectory[:, 0], "x")
        ap.plot.draw_lattice(fodo_ring)
        plt.savefig("/tmp/test_fodo_ring.pdf")
