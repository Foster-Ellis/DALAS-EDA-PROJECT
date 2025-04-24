import matplotlib.pyplot as plt
import numpy as np

# Parameters
mu = 64  # service rate in packets per second
packet_size_kbits = 8  # packet size in kbits
b_vals = np.linspace(1, 300, 1000)  # input rates in kbit/s
lambda_vals = b_vals / packet_size_kbits  # arrival rate in packets/s
K = 6  # M/M/1/K where K = queue size (5) + 1 for the service

# M/M/1/K delay calculation
def mm1k_delay(lambd, mu, K):
    rho = lambd / mu
    if rho == 1:
        pi_0 = 1 / (K + 1)
    else:
        pi_0 = (1 - rho) / (1 - rho**(K + 1))
    L = sum([n * (rho**n) for n in range(K)]) * pi_0
    return L / lambd

mm1k_delays = []
for l in lambda_vals:
    if l >= mu:
        mm1k_delays.append(np.nan)
    else:
        mm1k_delays.append(mm1k_delay(l, mu, K))
mm1k_delays = np.array(mm1k_delays)

# DropTail, RED, SFQ simulated delay approximation from Bmax-5queue.jpg
b_sim = np.array([0, 50, 100, 150, 200, 225, 240, 250, 260, 270, 280, 290, 300])
droptail_delay = np.array([0.05, 0.06, 0.07, 0.09, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.25, 0.28, 0.3])
red_delay =       np.array([0.05, 0.06, 0.07, 0.09, 0.11, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2])
sfq_delay =       np.array([0.05, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2, 0.24, 0.28, 0.32, 0.36, 0.4, 0.45])

# Plot
plt.figure(figsize=(10, 6))
plt.plot(b_vals, mm1k_delays, label='M/M/1/K (K=5)', color='blue', linestyle='-')
plt.plot(b_sim, droptail_delay, label='DropTail (sim)', color='magenta', linestyle='--', marker='o')
plt.plot(b_sim, red_delay, label='RED (sim)', color='green', linestyle='--', marker='x')
plt.plot(b_sim, sfq_delay, label='SFQ (sim)', color='orange', linestyle='--', marker='s')

plt.xlabel("Input Rate b (kbit/s)")
plt.ylabel("Delay (s)")
plt.title("Delay as a Function of b with Queue Limit 5")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
