from collections import defaultdict

def nested_loop_join(R, S, kr=0, ks=0):
    return [r + s for r in R for s in S if r[kr] == s[ks]]

def hash_join(R, S, kr=0, ks=0):
    small, big, swap = (R, S, False) if len(R) <= len(S) else (S, R, True)
    h = defaultdict(list)
    for t in small: h[t[kr if not swap else ks]].append(t)
    out = []
    for t in big:
        for m in h.get(t[ks if not swap else kr], ()):
            out.append(m + t if not swap else t + m)
    return out

def sort_merge_join(R, S, kr=0, ks=0):
    R = sorted(R, key=lambda t: t[kr]); S = sorted(S, key=lambda t: t[ks])
    i = j = 0; out = []
    while i < len(R) and j < len(S):
        a, b = R[i][kr], S[j][ks]
        if a < b: i += 1
        elif a > b: j += 1
        else:
            j2 = j
            while j2 < len(S) and S[j2][ks] == a: j2 += 1
            while i < len(R) and R[i][kr] == a:
                out.extend(R[i] + S[k] for k in range(j, j2)); i += 1
            j = j2
    return out
