import random, sys, os
import matplotlib.pyplot as plt
import numpy as np

def flip():
    return random.randint(0,1)      #1 is for heads, 0 is for tails

# settings
max_flips = 1000
num_trials = 20
threshold = 20
folder = 'plots'
os.makedirs(folder, exist_ok=True)
# settings

all_trials = []

for t in range(1, num_trials + 1):
    probabilities = []
    flips = []
    ds = []
    critical_found = False

    for i in range (max_flips):
        ds.append(flip())
        n = len(ds)
    
        hprob = ds.count(1) / n
        probabilities.append(hprob)
        flips.append(n)
    
        if n > threshold and (0.49999 < hprob < 0.50001):     # stop the trial when probability of heads is sufficiently close to 0.5
            print(f'[Trial {t}] Critical point reached at {n}. Head probability is {hprob}')
            critical_found = True
            critical_n = n
            break
        else:
            print(f'[Trial {t}] Coin flip {n} is {hprob}')
    else:
        print(f"[Trial {t}] No critical point found within the range of {max_flips}")
    
    all_trials.append({
        "trial": t,
        "flips": flips[:],
        "probs": probabilities[:],
        "critical_found": critical_found,
        "critical_n": critical_n if critical_found else None
    })

  
    # INDIVIDUAL GRAPH
    plt.figure()
    plt.plot(flips, probabilities, label="Head Probability")
    plt.axhline(0.5, color="red", linestyle="--", label="Expected Probability 0.5")

    if critical_found:
        final_x = flips[-1]
        final_y = probabilities[-1]
        plt.scatter(final_x, final_y, color="blue", s=100, zorder=5, label="Final Value")
        plt.annotate(f"Flips: {final_x}",
                     (final_x, final_y),
                     textcoords="offset points",
                     xytext=(-40,10),
                     ha='center',
                     fontsize=9,
                     color="blue")
    else:
        plt.text(0.5, 0.95, "⚠ No final value found",
                 transform=plt.gca().transAxes,
                 ha='center', va='top',
                 fontsize=10, color="red",
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='red'))

    plt.xlabel("Number of Flips")
    plt.ylabel("Probability of Heads")
    plt.title(f"Coin Flip Simulation — Trial {t}")
    plt.legend()

    out_path = os.path.join(folder, f"trial_{t:02d}.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


# FINAL SUMMARY GRAPH
max_n = max(len(tr["probs"]) for tr in all_trials)
ns = np.arange(1, max_n + 1)

means = []
for n in ns:
    vals_at_n = [tr["probs"][n-1] for tr in all_trials if len(tr["probs"]) >= n]
    means.append(np.mean(vals_at_n))

#adds the amount of trials that found/did not find a critical point
num_found = sum(1 for tr in all_trials if tr["critical_found"])
num_nofound = len(all_trials) - num_found

with plt.style.context('bmh'):
    fig = plt.figure(figsize=(11, 7), dpi=150)
    ax = plt.gca()

    # plot each trial (solid if critical found, dashed if not)
    found_labeled = False
    nofound_labeled = False
    for tr in all_trials:
        if tr["critical_found"]:
            label = f"Individual trials (critical found: {num_found})" if not found_labeled else None
            found_labeled = True
            ax.plot(tr["flips"], tr["probs"],
                    linewidth=1.0, alpha=0.5, linestyle='-',
                    label=label)
            # mark final point if critical found
            ax.scatter(tr["flips"][-1], tr["probs"][-1], s=35, zorder=5)
        else:
            label = f"Individual trials (no critical: {num_nofound})" if not nofound_labeled else None
            nofound_labeled = True
            ax.plot(tr["flips"], tr["probs"],
                    linewidth=1.0, alpha=0.5, linestyle='--',
                    label=label)

    # plot the average curve across trials
    ax.plot(ns, means, linewidth=2.5, color="blue", label="Average across trials")

    #expected random variation
    wiggle = 1 / np.sqrt(ns)
    ax.fill_between(ns, 0.5 - wiggle, 0.5 + wiggle,
                    color="#ffab58dc", alpha=0.4,
                    label="Expected random variation")

    # expected 0.5 line (bolder)
    ax.axhline(0.5, linestyle="--", linewidth=2.0, color="red",
               label="Expected Probability 0.5")

    # labels and aesthetics
    ax.set_xlabel("Number of Flips")
    ax.set_ylabel("Probability of Heads")
    ax.set_title("Coin Flip Simulation — Summary Across Trials")
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(frameon=True, fontsize=9)

    summary_path = os.path.join(folder, "summary.png")
    plt.tight_layout()
    plt.savefig(summary_path, bbox_inches="tight")
    plt.close()


print(f"Saved summary overlay: {summary_path}")
print(f"\nSaved {num_trials} graphs in ./{folder}/ (trial_01.png ... trial_{num_trials:02d}.png)")

critical_points = [tr["critical_n"] for tr in all_trials if tr["critical_found"]]
critical_points = np.array(critical_points, dtype=int)

# Compute basic statistics on critical points across all trials
mu = critical_points.mean()                 # mean
median = np.median(critical_points)         # median
sigma = critical_points.std(ddof=1)         # sample standard deviation
se = sigma / np.sqrt(len(critical_points))  # standard error of the mean
cmin, cmax = critical_points.min(), critical_points.max()

print(f"\nCritical-point stats over {len(critical_points)} trials:")
print(f"  mean = {mu:.2f}")
print(f"  median = {median:.2f}")
print(f"  standard deviation = {sigma:.2f}")
print(f"  standard error = {se:.2f}")
print(f"  min = {cmin}, max = {cmax}")

# BAR GRAPH
plt.figure(figsize=(10,6), dpi=150)
counts, bin_edges, _ = plt.hist(
    critical_points,
    bins='auto',        # lets numpy pick sensible bin count
    edgecolor='black',
    alpha=0.7,
    label=f"Critical points (n={len(critical_points)})"
)

plt.title("Distribution of Critical Points Across Trials")
plt.xlabel("Critical point (flip count)")
plt.ylabel("Number of trials")
plt.legend()

hist_path = os.path.join(folder, "critical_points_graph.png")
plt.tight_layout()
plt.savefig(hist_path, bbox_inches="tight")
plt.close()

print(f"Saved critical-points bar-graph: {hist_path}")
