"""Fees and price ticks. Prices may carry at most 4 significant figures."""
import math


def tick_size(p):
    if p <= 0:
        return 0.01
    return max(10.0 ** (math.floor(math.log10(p)) - 3), 0.01)


def valid_down(p):
    """Largest valid price <= p."""
    t = tick_size(p)
    return round(math.floor(p / t + 1e-9) * t, 2)


def valid_up(p):
    """Smallest valid price >= p."""
    t = tick_size(p)
    return round(math.ceil(p / t - 1e-9) * t, 2)


def tick_down(p):
    """Largest valid price strictly below p (one tick under)."""
    q = p * (1 - 1e-9)
    t = tick_size(q)
    return round(math.floor(q / t) * t, 2)


def tick_up(p):
    """Smallest valid price strictly above p (one tick over)."""
    q = p * (1 + 1e-9)
    t = tick_size(q)
    return round(math.ceil(q / t) * t, 2)


class Fees:
    def __init__(self, cfg):
        s, f = cfg["skills"], cfg["fees"]
        self.broker = max(
            f["broker_min"],
            f["broker_base"] - 0.003 * s["broker_relations"]
            - 0.0003 * s["faction_standing"] - 0.0002 * s["corp_standing"],
        )
        self.tax = f["sales_tax_base"] * (1 - 0.11 * s["accounting"])
        self.relist_discount = 0.5 + 0.06 * s["advanced_broker_relations"]
        self.min_fee = f["min_fee_isk"]

    def broker_fee(self, price, qty):
        return max(self.min_fee, self.broker * price * qty)

    def relist_fee(self, old, new, qty):
        return max(self.min_fee, (1 - self.relist_discount) * self.broker * new * qty
                   + self.broker * max(0.0, (new - old) * qty))

    def sell_breakeven(self, unit_cost):
        """Sell price that returns unit_cost after sales tax (listing fee already paid)."""
        return unit_cost / (1 - self.tax)
