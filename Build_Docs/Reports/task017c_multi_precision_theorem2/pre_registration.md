# Task 017c Pre-registration - Theorem 2 Multi-precision Validation

This document records the Task 017c predictions before campaign execution. These
predictions are not to be edited after the pre-registration commit.

## Theorem 2 Source

Source file:

```text
/home/william_lloydlt/projects/V4/Docs/transfer_function_exponent_family_v3.tex
```

Verbatim theorem block:

```tex
\begin{theorem}[Precision-scaling separation test]\label{thm:precision-separation}
Assume measurements at precision $p$ and arithmetic path $k$ have asymptotic form
\begin{equation}\label{eq:precision-model}
    R_{p,k}(f)=
    \left(a+u_p b_k\right)f^{\alpha-1}L(f)(1+o(1))
    +o(u_p f^{\alpha-1}L(f)),
\end{equation}
where $u_p$ is the unit roundoff, $a$ is the path-invariant geometric amplitude, and $b_k$ is the path-dependent conditioning amplitude. Define the measured branch amplitude
\begin{equation}\label{eq:measured-amplitude}
    C_{p,k}:=\lim_{f\to0^+}\frac{R_{p,k}(f)}{f^{\alpha-1}L(f)}.
\end{equation}
Then
\[
    C_{p,k}=a+u_p b_k.
\]
With at least two distinct precisions, $a$ and $b_k$ are identifiable for each fixed path $k$ by a linear fit in $u_p$. With multiple algebraically equivalent paths, variation in $b_k$ provides an additional path-dependence test for arithmetic conditioning.
\end{theorem}
```

Canonical `C_{p,k}` definition line:

```tex
    C_{p,k}:=\lim_{f\to0^+}\frac{R_{p,k}(f)}{f^{\alpha-1}L(f)}.
```

## Pre-registered Sub-claims

| Sub-claim | Pre-registered criterion |
| --- | --- |
| Regular-region linear fit | R2 >= 0.98 for `C_{p,k} = a_k + b_k * u_p` outside the Sterbenz-applicable region. |
| Intercept consistency | The deterministic bootstrap 95% CI for each `a_k` includes zero. |
| Slope structure | In the regular region, F1/F2/F4 slopes are distinguishable from zero and do not all collapse to the same value; F3 slope is indistinguishable from zero. |
| Sterbenz-region F2 vanishing | In the Sterbenz-applicable region, F2 slope CI includes zero. |

## Precision Battery

Schwarzschild, SR, and pure algebraic execute:

- `float32`
- `float64`
- `float128` when meaningfully distinct from `float64`
- `decimal_50`
- `decimal_100`
- `decimal_200`

Cbrt executes:

- `float32`
- `float64`
- `float128` when meaningfully distinct from `float64`

Cbrt Decimal rows are recorded as `out_of_scope_by_design`.

## Platform Float128 Report

```text
numpy.float64:
  eps: 2.220446049250313e-16
  bits: 64
  precision: 15
  max: 1.7976931348623157e+308
  tiny: 2.2250738585072014e-308

numpy.float128 / numpy.longdouble:
  eps: 1.084202172485504434e-19
  bits: 128
  precision: 18
  max: 1.189731495357231765e+4932
  tiny: 3.3621031431120935063e-4932
```

`numpy.float128` is meaningfully distinct from `numpy.float64` on this host
because `eps(float128) != eps(float64)`.

## Sterbenz-applicable Regions

| Fixture | Region |
| --- | --- |
| `schwarzschild` | `r >= 4` |
| `sr` | `beta <= 1 / sqrt(2)` |
| `pure_algebraic` | `x <= 1/2` |
| `cbrt_chain` | `x <= 1/2` |

## Closing

The predictions in this document are registered before campaign execution and
are not to be edited after this commit. The pre-registration commit hash is
recorded in `Build_Docs/Reports/task017c_summary.md`.
