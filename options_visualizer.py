"""
Options Pricing Visualizer
"""

from math import exp, log, sqrt
from typing import Literal

from reactpy import component, hooks, html, run
from scipy.stats import norm

OptionType = Literal["call", "put"]


def black_scholes(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType,
) -> float:
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0

    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == "call":
        return S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)

    return K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def payoff(
    final_price: float,
    strike: float,
    premium: float,
    option_type: OptionType,
) -> float:
    intrinsic = (
        max(final_price - strike, 0)
        if option_type == "call"
        else max(strike - final_price, 0)
    )

    return intrinsic - premium


# ---------- TESTS ----------
def test_black_scholes():
    call_price = black_scholes(100, 100, 1, 0.05, 0.2, "call")
    put_price = black_scholes(100, 100, 1, 0.05, 0.2, "put")

    assert abs(call_price - 10.45) < 0.05
    assert abs(put_price - 5.57) < 0.05
    assert payoff(120, 100, 8, "call") == 12
    assert payoff(80, 100, 7, "put") == 13
    assert black_scholes(0, 100, 1, 0.05, 0.2, "call") == 0


STYLE = """
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f8fafc;
    color: #0f172a;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px;
}

.card {
    background: white;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    padding: 24px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.metric {
    font-size: 30px;
    font-weight: bold;
}

button {
    padding: 10px 16px;
    border-radius: 12px;
    border: 1px solid #cbd5e1;
    background: white;
    cursor: pointer;
    margin-right: 10px;
    font-weight: bold;
}

.active {
    background: #0f172a;
    color: white;
}

input[type='range'] {
    width: 100%;
    margin-top: 6px;
    margin-bottom: 18px;
    accent-color: #0f172a;
}
"""


def slider(label, value, setter, minimum, maximum, step, suffix=""):
    return html.div(
        {},
        html.div(
            {
                "style": {
                    "display": "flex",
                    "justifyContent": "space-between",
                    "fontWeight": "bold",
                }
            },
            html.span(label),
            html.span(f"{value}{suffix}"),
        ),
        html.input(
            {
                "type": "range",
                "min": minimum,
                "max": maximum,
                "step": step,
                "value": value,
                "on_change": lambda event: setter(
                    float(event["target"]["value"])
                ),
            }
        ),
    )


@component
def App():
    option_type, set_option_type = hooks.use_state("call")

    S, set_S = hooks.use_state(100.0)
    K, set_K = hooks.use_state(100.0)
    days, set_days = hooks.use_state(45.0)
    rate, set_rate = hooks.use_state(4.5)
    vol, set_vol = hooks.use_state(25.0)

    T = days / 365
    r = rate / 100
    sigma = vol / 100

    premium = black_scholes(S, K, T, r, sigma, option_type)

    breakeven = K + premium if option_type == "call" else K - premium

    return html.div(
        {},
        html.style(STYLE),
        html.main(
            {"class_name": "container"},
            html.h1("Options Pricing Visualizer"),
            html.p(
                "Interactive Black-Scholes pricing model built with Python and ReactPy."
            ),
            html.div(
                {"class_name": "card"},
                html.div(
                    {"style": {"marginBottom": "18px"}},
                    html.button(
                        {
                            "class_name": "active"
                            if option_type == "call"
                            else "",
                            "on_click": lambda _: set_option_type("call"),
                        },
                        "Call",
                    ),
                    html.button(
                        {
                            "class_name": "active"
                            if option_type == "put"
                            else "",
                            "on_click": lambda _: set_option_type("put"),
                        },
                        "Put",
                    ),
                ),
                slider("Underlying Price", S, set_S, 20, 250, 1),
                slider("Strike Price", K, set_K, 20, 250, 1),
                slider("Days to Expiry", days, set_days, 1, 365, 1, "d"),
                slider("Risk-Free Rate", rate, set_rate, 0, 12, 0.1, "%"),
                slider("Implied Volatility", vol, set_vol, 1, 100, 1, "%"),
                html.hr(),
                html.div(
                    {"class_name": "grid"},
                    html.div(
                        {},
                        html.div("Premium"),
                        html.div(
                            {"class_name": "metric"},
                            f"${premium:.2f}",
                        ),
                    ),
                    html.div(
                        {},
                        html.div("Breakeven"),
                        html.div(
                            {"class_name": "metric"},
                            f"${breakeven:.2f}",
                        ),
                    ),
                ),
            ),
        ),
    )


if __name__ == "__main__":
    test_black_scholes()
    print("All Black-Scholes tests passed.")
    print("Starting ReactPy server at http://127.0.0.1:8000")
    run(App, host="127.0.0.1", port=8000)
