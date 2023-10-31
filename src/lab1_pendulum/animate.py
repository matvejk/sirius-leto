import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .constants import *
from src.general.constants import *
from src.general.calculations import *


def __animation_step(frame: int, alpha_array) -> tuple:
	global t0, pendulum_line, pendulum_point, time_text, n  # noqa - variables are defined in `animate()`

	# calculating current in-model time
	data_item_index = render_dt * frame
	time = data_item_index * dt

	# fps counting
	if frame == 0:
		t0 = real_time()
	elif frame % frames_count_fps == 0:
		t1 = real_time()
		clear_screen()
		print(f'fps = {frames_count_fps / (t1 - t0):2}')  # printing fps value
		t0 = real_time()

	# if animation was ended, but was not closed
	if data_item_index >= n:
		return pendulum_line, pendulum_point, time_text

	# by default, angle is in [0; 2×pi], but for beautiful rendering we need angle in [-pi/2; 3/4×pi],
	# so we subtract pi/2 from each alpha value
	alpha: float = alpha_array[data_item_index] - pi / 2

	# converting polar coordinates (l, alpha) to cartesian (x, y)
	x, y = pol2cart(l, alpha)

	# pendulum axis's coordinates is not always (0, 0),
	# so we need to add (pendulum_axis_x, pendulum_axis_y) to obtained (x, y)
	x += pendulum_axis_x
	y += pendulum_axis_y

	# updating coordinates on plot
	pendulum_point.set_data([x], [y])
	pendulum_line.set_data([pendulum_axis_x, x], [pendulum_axis_y, y])

	time_text.set_text(rf"${time:.2f}\,s$")  # updating stopwatch (format “0.00 s”)

	return pendulum_line, pendulum_point, time_text


def animate(config: dict[str, ...]) -> None:
	global n, pendulum_line, pendulum_point, time_text  # noqa - variables will be defined below

	for i in config.keys():
		globals()[i] = config[i]

	with open(datapath_model) as f:  # reading data generated by `model.py`
		dt, l, t_max, n = [float(f.readline().strip()) for _ in range(4)]  # noqa

		time_array  = [float(i) for i in f.readline().strip().split()]  # noqa double space
		alpha_array = [float(i) for i in f.readline().strip().split()]

		if calculate_extremums:
			extremums_x = [float(i) for i in f.readline().strip().split()]
			extremums_y = [float(i) for i in f.readline().strip().split()]

		if calculate_theoretical:
			theoretical_alpha_array = [float(i) for i in f.readline().strip().split()]
			if calculate_extremums:
				extremums_theory_x = [float(i) for i in f.readline().strip().split()]
				extremums_theory_y = [float(i) for i in f.readline().strip().split()]

	n = int(n)

	mpl.rcParams['mathtext.fontset'] = 'cm'
	mpl.rcParams['figure.figsize'] = (figsize, figsize)

	t0 = real_time()  # noqa, do not remove, required for fps counting!

	if plot_animation:
		fig, _ = plt.subplots()
		plt.title("Numerical model of a pendulum")
		plt.grid(True, linestyle='--')
		plt.xlabel(r'$x, m$', fontsize=13)
		plt.ylabel(r'$y, m$', fontsize=13)
		plt.xlim(-plot_lims * l, plot_lims * l)
		plt.ylim(-plot_lims * l, plot_lims * l)

		pendulum_line, = plt.plot([], [], linewidth=2, color='blue')
		pendulum_axis, = plt.plot([pendulum_axis_x], [pendulum_axis_y], marker='o', markersize=5, color='red')  # noqa, required for animation
		pendulum_point, = plt.plot([], [], marker='o', markersize=5, color='red')
		time_text = plt.text(0, text_y * l, "", fontsize=20)
		animation = FuncAnimation(fig,  # noqa:F841
		                          func=__animation_step,
		                          fargs=(alpha_array,),
		                          interval=0,
		                          frames=n,
		                          blit=True,
		                          repeat=False,
		                          cache_frame_data=True)

	if plot_alpha:
		fig, _ = plt.subplots()
		plt.grid(True, linestyle='--')
		plt.xlabel(r"$t, s$", fontsize=13)
		plt.ylabel(r"$\alpha, rad$", fontsize=13)

		color = plt.plot(time_array, alpha_array, label="simulation")[0].get_color()
		if calculate_extremums:
			plt.plot(extremums_x, extremums_y, 'o', color=color)
			for i in range(len(extremums_x)):
				plt.axvline(extremums_x[i], ymin=-plot_lims, ymax=plot_lims, color=color, linewidth=1, ls='--')

		if calculate_theoretical:
			color = plt.plot(time_array, theoretical_alpha_array, label="theory")[0].get_color()
			if calculate_extremums:
				plt.plot(extremums_theory_x, extremums_theory_y, 'o', color=color)
				for i in range(len(extremums_x)):
					plt.axvline(extremums_theory_x[i], ymin=-plot_lims, ymax=plot_lims, color=color, linewidth=1, ls='--')

	elif calculate_theoretical:
		fig, _ = plt.subplots()
		plt.grid(True, linestyle='--')
		plt.xlabel(r"$t, s$", fontsize=13)
		plt.ylabel(r"$\alpha, rad$", fontsize=13)

		color = plt.plot(time_array, theoretical_alpha_array, label="theory")
		if calculate_extremums:
			plt.plot(extremums_theory_x, extremums_theory_y, 'o', color=color)

	plt.legend(loc="upper right")
	plt.show()
