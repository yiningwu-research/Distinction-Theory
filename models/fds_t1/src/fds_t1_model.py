import numpy as np


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def decreasing_sigmoid(t, high, low, center, width):
    """Smooth transition from high to low."""
    return high - (high - low) * sigmoid((t - center) / width)


def binary_entropy(d):
    d = np.asarray(d)
    eps = 1e-12
    x = np.clip(d, eps, 1 - eps)
    return -(x * np.log2(x) + (1 - x) * np.log2(1 - x))


def binary_entropy_inverse(y, max_iter=100):
    """Invert H_b(D)=y for D in [0, 0.5]."""
    y_arr = np.asarray(y, dtype=float)
    y_clip = np.clip(y_arr, 0.0, 1.0)
    lo = np.zeros_like(y_clip)
    hi = np.full_like(y_clip, 0.5)
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        h = binary_entropy(mid)
        lo = np.where(h < y_clip, mid, lo)
        hi = np.where(h >= y_clip, mid, hi)
    return 0.5 * (lo + hi)


def gaussian_rate_distortion_dmin(capacity_bits, sigma2=1.0):
    """D_min(R)=sigma^2 2^{-2R} for Gaussian source under MSE."""
    return sigma2 * np.power(2.0, -2.0 * np.asarray(capacity_bits))


def gaussian_rate_required(epsilon, sigma2=1.0):
    """R(D)=1/2 log2(sigma^2/D)."""
    return 0.5 * np.log2(sigma2 / epsilon)


def binary_rate_distortion_dmin(capacity_bits, p=0.5):
    """Bernoulli(p) Hamming source: R(D)=H_b(p)-H_b(D)."""
    hp = float(binary_entropy(np.array([p]))[0])
    target_h = hp - np.asarray(capacity_bits)
    target_h = np.clip(target_h, 0.0, hp)
    d = binary_entropy_inverse(target_h)
    return np.minimum(d, min(p, 1 - p))


def active_bottleneck(capacity_dict):
    names = list(capacity_dict.keys())
    values = np.vstack([capacity_dict[name] for name in names])
    idx = np.argmin(values, axis=0)
    cacc = values[idx, np.arange(values.shape[1])]
    labels = np.array([names[i] for i in idx])
    return cacc, labels


def transition_indices(labels):
    """Return indices where active bottleneck label changes."""
    return np.where(labels[1:] != labels[:-1])[0] + 1


def default_gaussian_scenario(n=1001):
    t = np.linspace(0.0, 100.0, n)
    capacities = {
        "record-access": np.full_like(t, 5.0),
        "channel": decreasing_sigmoid(t, high=4.6, low=3.7, center=30.0, width=5.0),
        "causal-boundary": decreasing_sigmoid(t, high=5.2, low=2.8, center=55.0, width=4.0),
        "thermodynamic": decreasing_sigmoid(t, high=4.9, low=1.9, center=75.0, width=5.0),
    }
    cacc, labels = active_bottleneck(capacities)
    return t, capacities, cacc, labels


def delayed_observer_scenario(n=1001):
    t = np.linspace(0.0, 100.0, n)
    capacities = {
        "record-access": np.full_like(t, 5.0),
        "channel": decreasing_sigmoid(t, high=4.6, low=3.7, center=30.0, width=5.0),
        "causal-boundary": decreasing_sigmoid(t, high=5.2, low=2.8, center=67.0, width=5.0),
        "thermodynamic": decreasing_sigmoid(t, high=4.9, low=1.9, center=75.0, width=5.0),
    }
    cacc, labels = active_bottleneck(capacities)
    return t, capacities, cacc, labels


def default_binary_scenario(n=1001):
    t = np.linspace(0.0, 100.0, n)
    capacities = {
        "record-access": np.full_like(t, 1.00),
        "channel": decreasing_sigmoid(t, high=0.92, low=0.62, center=30.0, width=5.0),
        "causal-boundary": decreasing_sigmoid(t, high=1.10, low=0.35, center=58.0, width=5.0),
        "thermodynamic": decreasing_sigmoid(t, high=0.98, low=0.42, center=78.0, width=5.0),
    }
    cacc, labels = active_bottleneck(capacities)
    return t, capacities, cacc, labels
