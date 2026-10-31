"""Reproduces every number and figure in the paper. Writes results.json and fig_*.png."""
import json, os, platform, random, statistics, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from joins import nested_loop_join, hash_join, sort_merge_join
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = os.path.join(os.path.dirname(__file__), "..")
ALGS = {"nested_loop": nested_loop_join, "hash": hash_join, "sort_merge": sort_merge_join}

def timeit(f, R, S, reps=5):
    ts = []
    for _ in range(reps):
        t = time.perf_counter(); out = f(R, S); ts.append(time.perf_counter() - t)
    return statistics.median(ts), len(out)

def zipf_keys(rng, n, keys, s):
    w = [1 / (i + 1) ** s for i in range(keys)]
    return rng.choices(range(keys), weights=w, k=n)

def main():
    res = {"env": {"python": platform.python_version(), "machine": platform.machine(), "cpus": os.cpu_count()}, "scale": [], "skew": [], "sorted": []}
    for n in (500, 1000, 2000, 4000, 8000, 16000, 32000, 64000):
        rng = random.Random(n)
        R = [(rng.randrange(n), i) for i in range(n)]; S = [(rng.randrange(n), i) for i in range(n)]
        for a, f in ALGS.items():
            if a == "nested_loop" and n > 4000: continue
            t, rows = timeit(f, R, S, 3 if a == "nested_loop" else 5)
            res["scale"].append(dict(n=n, alg=a, ms=t * 1e3, rows=rows))
    n = 20000
    for s in (0.0, 0.5, 1.0, 1.2):
        rng = random.Random(7)
        R = [(k, i) for i, k in enumerate(zipf_keys(rng, n, 5000, s))]; S = [(k, i) for i, k in enumerate(zipf_keys(rng, n, 5000, s))]
        for a in ("hash", "sort_merge"):
            t, rows = timeit(ALGS[a], R, S, 3)
            res["skew"].append(dict(s=s, alg=a, ms=t * 1e3, rows=rows))
    rng = random.Random(3); n = 64000
    R = [(rng.randrange(n), i) for i in range(n)]; S = [(rng.randrange(n), i) for i in range(n)]
    for label, (r, s_) in {"random": (R, S), "presorted": (sorted(R), sorted(S))}.items():
        for a in ("hash", "sort_merge"):
            t, rows = timeit(ALGS[a], r, s_)
            res["sorted"].append(dict(input=label, alg=a, ms=t * 1e3, rows=rows))
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    plt.figure(figsize=(5.5, 3.6))
    for a in ALGS:
        pts = [(r["n"], r["ms"]) for r in res["scale"] if r["alg"] == a]
        plt.loglog(*zip(*pts), marker="o", label=a)
    plt.xlabel("rows per input (n)"); plt.ylabel("median time (ms)"); plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
    plt.savefig(os.path.join(OUT, "fig_scale.png"), dpi=150)
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main()
