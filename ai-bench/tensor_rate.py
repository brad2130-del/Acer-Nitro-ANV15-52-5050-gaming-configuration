#!/usr/bin/env python3
"""
Tensor-core rate check — Acer Nitro V15 (RTX 5050 Blackwell)
Is the GeForce half-rate FP16/FP32-accumulate limit present on this GPU?

GeForce cards issue FP16 matmuls with FP32 accumulation at half the rate of
FP16 accumulation; that throttle is what the GPU-Unlock projects remove on
RTX 20/30/40. Measure both here: ~2x gap = the limit exists (unlock target),
~1x = nothing to unlock. Read-only: plain cuBLAS GEMMs, no register pokes.

Needs PyTorch >= 2.7 with CUDA (for allow_fp16_accumulation).
Run plugged in, Performance profile, nothing else on the dGPU:
  python3 ai-bench/tensor_rate.py [--n 8192] [--iters 50]
"""

import argparse
import time

import torch


def tflops(dtype: torch.dtype, n: int, iters: int, fp16_acc: bool = False, tf32: bool = False) -> float:
    torch.backends.cuda.matmul.allow_fp16_accumulation = fp16_acc
    torch.backends.cuda.matmul.allow_tf32 = tf32
    a = torch.randn(n, n, device="cuda", dtype=dtype)
    b = torch.randn(n, n, device="cuda", dtype=dtype)
    for _ in range(5):                      # warm up clocks + cuBLAS heuristics
        a @ b
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(iters):
        a @ b
    torch.cuda.synchronize()
    dt = time.perf_counter() - t0
    return 2 * n**3 * iters / dt / 1e12


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n", type=int, default=8192, help="square matrix size")
    ap.add_argument("--iters", type=int, default=50)
    args = ap.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit("CUDA not available — check the NVIDIA driver / PyTorch build")
    if not hasattr(torch.backends.cuda.matmul, "allow_fp16_accumulation"):
        raise SystemExit(f"PyTorch {torch.__version__} lacks allow_fp16_accumulation — need >= 2.7")

    print(f"GPU: {torch.cuda.get_device_name()}  (n={args.n}, iters={args.iters})\n")
    r = {
        "FP16, FP32 accumulate": tflops(torch.float16, args.n, args.iters),
        "FP16, FP16 accumulate": tflops(torch.float16, args.n, args.iters, fp16_acc=True),
        "BF16, FP32 accumulate": tflops(torch.bfloat16, args.n, args.iters),
        "TF32":                  tflops(torch.float32, args.n, args.iters, tf32=True),
    }
    for name, v in r.items():
        print(f"  {name:<24} {v:7.1f} TFLOPS")

    ratio = r["FP16, FP16 accumulate"] / r["FP16, FP32 accumulate"]
    print(f"\n  FP16-acc / FP32-acc ratio: {ratio:.2f}x")
    if ratio >= 1.7:
        print("  → Half-rate FP32-accumulate limit looks PRESENT. This is what an unlock would target.")
    elif ratio <= 1.2:
        print("  → No half-rate limit visible. Nothing for a GPU-Unlock-style mod to free up.")
    else:
        print("  → Inconclusive. Re-run plugged in, Performance profile, GPU otherwise idle.")


if __name__ == "__main__":
    main()
