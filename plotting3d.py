#!/usr/bin/env python

import numpy as np
import scipy.stats as stats
import itertools
import matplotlib
from matplotlib import cm

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sklearn as sk
import sklearn.linear_model
from helpers import bround
from tof import calc_tof, calc_es, calc_s_es


def plot_ci_manual(t, s_err, n, x, x2, y2, ax=None):
    if ax is None:
        ax = plt.gca()

    ci = (
        t
        * s_err
        * np.sqrt(1 / n + (x2 - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2))
    )
    ax.fill_between(x2, y2 + ci, y2 - ci, color="#b9cfe7", alpha=0.6)

    return ax


def plot_3d_lsfer(idx1, idx2, d, tags, coeff, cb="white", ms="o", verb=0):
    d_refill = np.zeros_like(d)
    d_refill[~np.isnan(d)] = d[~np.isnan(d)]
    tags = [str(tag) for tag in tags]
    lnsteps = range(d.shape[1])
    mape = 100
    for j in lnsteps[1:-1]:
        if verb > 0:
            print(f"Plotting regression of {tags[j]}.")
        XY = np.vstack([[d[:, idx1], d[:, idx2]], d[:, j]]).T
        if isinstance(cb, np.ndarray):
            cbi = np.array(cb)[~np.isnan(XY).any(axis=1)]
        else:
            cbi = cb
        if isinstance(ms, np.ndarray):
            msi = np.array(ms)[~np.isnan(XY).any(axis=1)]
        else:
            msi = ms
        XYm = XY[np.isnan(XY).any(axis=1)]
        XY = XY[~np.isnan(XY).any(axis=1)]
        Xm = XYm[:, :2]
        Ym = XYm[:, 2]
        X = XY[:, :2]
        Y = XY[:, 2]
        xmax = bround(Y.max() + 10)
        xmin = bround(Y.min() - 10)
        xint = np.sort(Y)
        reg = sk.linear_model.LinearRegression().fit(X, Y)
        if verb > 2:
            print(
                f"Linear model has coefficients : {reg.coef_} \n and intercept {reg.intercept_}"
            )
        Y_pred = reg.predict(X)
        p = reg.coef_
        currmape = sk.metrics.mean_absolute_percentage_error(Y, Y_pred)
        for k, y in enumerate(Ym):
            if not np.isnan(Xm[k, 0]) and not np.isnan(Xm[k, 1]) and np.isnan(Ym[k]):
                Ym[k] = reg.predict(Xm[k])
                d_refill[np.isnan(d).any(axis=1)][:, j][k] = Ym[k]
            elif not np.isnan(Ym[k]) and not np.isnan(Xm[k, 0]):
                if currmape < mape:
                    Xm[k, 1] = (
                        Ym[k] - reg.intercept_ - reg.coeff_[0] * X[k][0]
                    ) / reg.coeff_[1]
                    d_refill[np.isnan(d).any(axis=1)][:, idx2][k] = Xm[k, 1]
                    mape = currmape
            elif not np.isnan(Ym[k]) and not np.isnan(Xm[k, 1]):
                if currmape < mape:
                    Xm[k, 0] = (
                        Ym[k] - reg.intercept_ - reg.coeff_[1] * X[k][1]
                    ) / reg.coeff_[0]
                    d_refill[np.isnan(d).any(axis=1)][:, idx1][k] = Xm[k, 0]
                    mape = currmape
            else:
                print(
                    "Both descriptor and regression target are undefined. This should have been fixed before this point. Exiting."
                )
                exit()
        n = Y.size
        m = p.size
        dof = n - m
        t = stats.t.ppf(0.95, dof)
        resid = Y - Y_pred
        chi2 = np.sum((resid / Y_pred) ** 2)
        s_err = np.sqrt(np.sum(resid ** 2) / dof)
        fig, ax = plt.subplots(
            frameon=False, figsize=[3, 3], dpi=300, constrained_layout=True
        )
        yint = np.sort(Y_pred)
        plot_ci_manual(t, s_err, n, X, xint, yint, ax=ax)
        pi = (
            t
            * s_err
            * np.sqrt(
                1 + 1 / n + (xint - np.mean(X)) ** 2 / np.sum((X - np.mean(X)) ** 2)
            )
        )
        ax.plot(xint, yint, "-", linewidth=1, color="#000a75", alpha=0.85)
        for i in range(len(X)):
            ax.scatter(
                Y_pred[i],
                Y[i],
                s=5,
                c=cbi[i],
                marker=msi[i],
                linewidths=0.15,
                edgecolors="black",
            )
        # Border
        ax.spines["top"].set_color("black")
        ax.spines["bottom"].set_color("black")
        ax.spines["left"].set_color("black")
        ax.spines["right"].set_color("black")
        ax.get_xaxis().set_tick_params(direction="out")
        ax.get_yaxis().set_tick_params(direction="out")
        ax.xaxis.tick_bottom()
        ax.yaxis.tick_left()
        # Labels and key
        plt.xlabel(f"Function of {tags[idx1]} and {tags[idx2]}")
        plt.ylabel(f"{tags[j]} [kcal/mol]")
        plt.xlim(xmin, xmax)
        plt.savefig(f"{tags[j]}.png")
    return d_refill


def plot_3d_t_volcano(idx1, idx2, d, tags, coeff, dgr, cb="white", ms="o", verb=0):
    tags = np.array([str(tag) for tag in tags])
    tag1 = tags[idx1]
    tag2 = tags[idx2]
    tags = tags[~coeff]
    lnsteps = range(np.count_nonzero(coeff == 0))
    X1 = d[:, idx1].reshape(-1)
    X2 = d[:, idx2].reshape(-1)
    x1max = bround(X1.max() + 15)
    x1min = bround(X1.min() - 15)
    x2max = bround(X2.max() + 15)
    x2min = bround(X2.min() - 15)
    npoints = 200
    if verb > 1:
        print(
            f"Range of descriptors set to [ {x1min} , {x1max} ] and [ {x2min} , {x2max} ]"
        )
    xint = np.linspace(x1min, x1max, npoints)
    yint = np.linspace(x2min, x2max, npoints)
    d = d[:, ~coeff]
    grids = []
    for i, j in enumerate(lnsteps):
        XY = np.vstack([X1, X2, d[:, j]]).T
        X = XY[:, :2]
        Y = XY[:, 2]
        reg = sk.linear_model.LinearRegression().fit(X, Y)
        Y_pred = reg.predict(X)
        gridj = np.zeros((npoints, npoints))
        for k, x1 in enumerate(xint):
            for l, x2 in enumerate(yint):
                x1x2 = np.vstack([x1, x2]).reshape(1, -1)
                gridj[k, l] = reg.predict(x1x2)
        grids.append(gridj)
    grid = np.zeros_like(gridj)
    ridmax = np.zeros_like(gridj, dtype=int)
    ridmin = np.zeros_like(gridj, dtype=int)
    rb = np.zeros_like(gridj, dtype=int)
    for k, x1 in enumerate(xint):
        for l, x2 in enumerate(yint):
            profile = [gridj[k, l] for gridj in grids]
            grid[k, l], ridmax[k, l], ridmin[k, l], diff = calc_s_es(
                profile, dgr, esp=True
            )
    rid = np.hstack([ridmin, ridmax])
    if verb > 0:
        pass
    ymin = grid.min()
    ymax = grid.max()
    px = np.zeros_like(d[:, 0])
    py = np.zeros_like(d[:, 0])
    for i in range(d.shape[0]):
        profile = d[i, :]
        px[i] = X1[i]
        py[i] = X2[i]
    x1label = f"{tag1} [kcal/mol]"
    x2label = f"{tag2} [kcal/mol]"
    ylabel = "-ΔG(kds) [kcal/mol]"
    filename = f"t_volcano_{tag1}_{tag2}.png"
    if verb > 0:
        csvname = f"t_volcano_{tag1}_{tag2}.csv"
        print(f"Saving volcano data to file {csvname}")
        x = np.zeros_like(grid.reshape(-1))
        y = np.zeros_like(grid.reshape(-1))
        for i, xy in enumerate(itertools.product(xint, yint)):
            x[i] = xy[0]
            y[i] = xy[1]
        zdata = list(zip(x, y, grid.reshape(-1)))
        np.savetxt(
            csvname,
            zdata,
            fmt="%.4e",
            delimiter=",",
            header="Descriptor 1, Descriptor 2, -\D_kds",
        )
    plot_3d(
        xint,
        yint,
        grid,
        px,
        py,
        ymin,
        ymax,
        x1min,
        x1max,
        x2min,
        x2max,
        x1label=x1label,
        x2label=x2label,
        ylabel=ylabel,
        filename=filename,
        cb=cb,
        ms=ms,
    )
    return xint, yint, grid, px, py


def plot_3d_k_volcano(idx1, idx2, d, tags, coeff, dgr, cb="white", ms="o", verb=0):
    tags = [str(tag) for tag in tags]
    lnsteps = range(d.shape[1])
    X1 = d[:, idx1].reshape(-1)
    X2 = d[:, idx2].reshape(-1)
    x1max = bround(X1.max() + 15)
    x1min = bround(X1.min() - 15)
    x2max = bround(X2.max() + 15)
    x2min = bround(X2.min() - 15)
    npoints = 200
    if verb > 1:
        print(
            f"Range of descriptors set to [ {x1min} , {x1max} ] and [ {x2min} , {x2max} ]"
        )
    xint = np.linspace(x1min, x1max, npoints)
    yint = np.linspace(x2min, x2max, npoints)
    grids = []
    for i, j in enumerate(lnsteps):
        XY = np.vstack([[d[:, idx1], d[:, idx2]], d[:, j]]).T
        X = XY[:, :2]
        Y = XY[:, 2]
        reg = sk.linear_model.LinearRegression().fit(X, Y)
        Y_pred = reg.predict(X)
        gridj = np.zeros((npoints, npoints))
        for k, x1 in enumerate(xint):
            for l, x2 in enumerate(yint):
                x1x2 = np.vstack([x1, x2]).reshape(1, -1)
                gridj[k, l] = reg.predict(x1x2)
        grids.append(gridj)
    grid = np.zeros_like(gridj)
    ridmax = np.zeros_like(gridj, dtype=int)
    ridmin = np.zeros_like(gridj, dtype=int)
    rb = np.zeros_like(gridj, dtype=int)
    for k, x1 in enumerate(xint):
        for l, x2 in enumerate(yint):
            profile = [gridj[k, l] for gridj in grids]
            grid[k, l], ridmax[k, l], ridmin[k, l], diff = calc_es(
                profile, dgr, esp=True
            )
    rid = np.hstack([ridmin, ridmax])
    if verb > 0:
        pass
    ymin = grid.min()
    ymax = grid.max()
    px = np.zeros_like(d[:, 0])
    py = np.zeros_like(d[:, 0])
    for i in range(d.shape[0]):
        profile = d[i, :]
        px[i] = d[i, idx1].reshape(-1)
        py[i] = d[i, idx2].reshape(-1)
    x1label = f"{tags[idx1]} [kcal/mol]"
    x2label = f"{tags[idx2]} [kcal/mol]"
    ylabel = "-ΔG(kds) [kcal/mol]"
    filename = f"k_volcano_{tags[idx1]}_{tags[idx2]}.png"
    if verb > 0:
        csvname = f"k_volcano_{tags[idx1]}_{tags[idx2]}.csv"
        print(f"Saving volcano data to file {csvname}")
        x = np.zeros_like(grid.reshape(-1))
        y = np.zeros_like(grid.reshape(-1))
        for i, xy in enumerate(itertools.product(xint, yint)):
            x[i] = xy[0]
            y[i] = xy[1]
        zdata = list(zip(x, y, grid.reshape(-1)))
        np.savetxt(
            csvname,
            zdata,
            fmt="%.4e",
            delimiter=",",
            header="Descriptor 1, Descriptor 2, -\D_kds",
        )
    plot_3d(
        xint,
        yint,
        grid,
        px,
        py,
        ymin,
        ymax,
        x1min,
        x1max,
        x2min,
        x2max,
        x1label=x1label,
        x2label=x2label,
        ylabel=ylabel,
        filename=filename,
        cb=cb,
        ms=ms,
    )
    return xint, yint, grid, px, py


def plot_3d_tof_volcano(
    idx1, idx2, d, tags, coeff, dgr, T=298.15, cb="white", ms="o", verb=0
):
    tags = [str(tag) for tag in tags]
    lnsteps = range(d.shape[1])
    X1 = d[:, idx1].reshape(-1)
    X2 = d[:, idx2].reshape(-1)
    x1max = bround(X1.max() + 15)
    x1min = bround(X1.min() - 15)
    x2max = bround(X2.max() + 15)
    x2min = bround(X2.min() - 15)
    npoints = 200
    if verb > 1:
        print(
            f"Range of descriptors set to [ {x1min} , {x1max} ] and [ {x2min} , {x2max} ]"
        )
    xint = np.linspace(x1min, x1max, npoints)
    yint = np.linspace(x2min, x2max, npoints)
    grids = []
    for i, j in enumerate(lnsteps):
        XY = np.vstack([[d[:, idx1], d[:, idx2]], d[:, j]]).T
        X = XY[:, :2]
        Y = XY[:, 2]
        reg = sk.linear_model.LinearRegression().fit(X, Y)
        Y_pred = reg.predict(X)
        gridj = np.zeros((npoints, npoints))
        for k, x1 in enumerate(xint):
            for l, x2 in enumerate(yint):
                x1x2 = np.vstack([x1, x2]).reshape(1, -1)
                gridj[k, l] = reg.predict(x1x2)
        grids.append(gridj)
    grid = np.zeros_like(gridj)
    rb = np.zeros_like(gridj, dtype=int)
    for k, x1 in enumerate(xint):
        for l, x2 in enumerate(yint):
            profile = [gridj[k, l] for gridj in grids]
            grid[k, l] = np.log10(calc_tof(profile, dgr, T, coeff, exact=True)[0])
    ymin = grid.min()
    ymax = grid.max()
    px = np.zeros_like(d[:, 0])
    py = np.zeros_like(d[:, 0])
    for i in range(d.shape[0]):
        profile = d[i, :]
        px[i] = d[i, idx1].reshape(-1)
        py[i] = d[i, idx2].reshape(-1)
    x1label = f"{tags[idx1]} [kcal/mol]"
    x2label = f"{tags[idx2]} [kcal/mol]"
    ylabel = "log(TOF) [1/s]"
    filename = f"tof_volcano_{tags[idx1]}_{tags[idx2]}.png"
    if verb > 0:
        csvname = f"tof_volcano_{tags[idx1]}_{tags[idx2]}.csv"
        print(f"Saving TOF volcano data to file {csvname}")
        x = np.zeros_like(grid.reshape(-1))
        y = np.zeros_like(grid.reshape(-1))
        for i, xy in enumerate(itertools.product(xint, yint)):
            x[i] = xy[0]
            y[i] = xy[1]
        zdata = list(zip(x, y, grid.reshape(-1)))
        np.savetxt(
            csvname,
            zdata,
            fmt="%.4e",
            delimiter=",",
            header="Descriptor 1, Descriptor 2, log10(TOF)",
        )
    plot_3d(
        xint,
        yint,
        grid,
        px,
        py,
        ymin,
        ymax,
        x1min,
        x1max,
        x2min,
        x2max,
        x1label=x1label,
        x2label=x2label,
        ylabel=ylabel,
        filename=filename,
        cb=cb,
        ms=ms,
    )
    return xint, yint, grid, px, py


def plot_3d(
    xint,
    yint,
    grid,
    px,
    py,
    ymin,
    ymax,
    x1min,
    x1max,
    x2min,
    x2max,
    x1label="X1-axis",
    x2label="X2-axis",
    ylabel="Y-axis",
    filename="plot.png",
    cb="white",
    ms="o",
):
    fig, ax = plt.subplots(
        frameon=False, figsize=[4, 3], dpi=300, constrained_layout=True
    )
    grid = np.clip(grid, ymin, ymax)
    norm = cm.colors.Normalize(vmax=ymax, vmin=ymin)
    levels = np.arange(ymin - 5, ymax + 5, 5.0)
    cset = ax.contourf(
        xint,
        yint,
        grid,
        levels=levels,
        norm=norm,
        cmap=cm.get_cmap("RdYlBu", len(levels)),
    )
    # Border
    ax.spines["top"].set_color("black")
    ax.spines["bottom"].set_color("black")
    ax.spines["left"].set_color("black")
    ax.spines["right"].set_color("black")
    ax.get_xaxis().set_tick_params(direction="out")
    ax.get_yaxis().set_tick_params(direction="out")
    ax.xaxis.tick_bottom()
    ax.yaxis.tick_left()
    # Labels and key
    plt.xlabel(x1label)
    plt.ylabel(x2label)
    plt.xlim(x1min, x1max)
    plt.ylim(x2min, x2max)
    ax.contour(xint, yint, grid, cset.levels, colors="black", linewidths=0.25)
    cbar = fig.colorbar(cset)
    cbar.set_label(ylabel, labelpad=5, rotation=270)
    for i in range(len(px)):
        ax.scatter(
            px[i],
            py[i],
            s=5,
            c=cb[i],
            marker=ms[i],
            linewidths=0.15,
            edgecolors="black",
        )
    plt.savefig(filename)