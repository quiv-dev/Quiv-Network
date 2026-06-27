"""
Quiv Network — x402 Agent Demo
================================
Demonstrates the x402 payment flow:
  1. Send HTTP request to paid endpoint
  2. Parse 402 Payment Required response
  3. Sign USDC micropayment (EIP-3009)
  4. Retry with X-PAYMENT header
  5. Return resource

NOTE: This is a demonstration stub.
      Full implementation requires a funded wallet and live x402 endpoint.
"""

import requests
import json
from typing import Optional

AGENT_VERSION = "0.1.0"
NETWORK = "eip155:8453"  # Base mainnet
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


class QuivAgent:
    """
    Autonomous AI agent with native x402 payment capability.
    Pays for digital resources per-request using USDC on Base.
    """

    def __init__(self, private_key: str, budget_per_request_usdc: float = 0.01):
        self.private_key = private_key
        self.budget = int(budget_per_request_usdc * 1_000_000)  # to USDC decimals
        self.session = requests.Session()
        self.payment_count = 0
        self.total_spent_usdc = 0.0

    def fetch(self, url: str, **kwargs) -> Optional[dict]:
        """
        Fetch a resource, auto-paying via x402 if required.
        """
        response = self.session.get(url, **kwargs)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 402:
            payment_spec = self._parse_402(response)
            if payment_spec is None:
                raise ValueError("Invalid 402 response: missing payment spec")

            amount = int(payment_spec.get("maxAmountRequired", 0))
            if amount > self.budget:
                raise ValueError(
                    f"Payment required ({amount} USDC units) exceeds budget ({self.budget})"
                )

            signed_payment = self._sign_payment(payment_spec)
            return self._retry_with_payment(url, signed_payment, **kwargs)

        response.raise_for_status()

    def _parse_402(self, response: requests.Response) -> Optional[dict]:
        """Extract payment specification from 402 response header."""
        header = response.headers.get("X-PAYMENT-REQUIRED")
        if not header:
            return None
        try:
            return json.loads(header)
        except json.JSONDecodeError:
            return None

    def _sign_payment(self, payment_spec: dict) -> str:
        """
        Sign a USDC EIP-3009 transferWithAuthorization.
        Returns base64-encoded signed payload.

        NOTE: Stub — full implementation requires eth_account + web3.
        """
        # In production:
        # from eth_account import Account
        # from eth_account.messages import encode_structured_data
        # ...sign EIP-3009 transferWithAuthorization...
        print(f"[Quiv] Signing payment: {payment_spec.get('maxAmountRequired')} USDC units")
        print(f"[Quiv] Recipient: {payment_spec.get('payTo')}")
        return "SIGNED_PAYMENT_STUB"

    def _retry_with_payment(self, url: str, signed_payment: str, **kwargs) -> Optional[dict]:
        """Retry the original request with X-PAYMENT header attached."""
        headers = kwargs.pop("headers", {})
        headers["X-PAYMENT"] = signed_payment

        response = self.session.get(url, headers=headers, **kwargs)
        response.raise_for_status()

        self.payment_count += 1
        print(f"[Quiv] Payment #{self.payment_count} settled. Resource delivered.")

        return response.json()

    def stats(self) -> dict:
        return {
            "version": AGENT_VERSION,
            "payments_made": self.payment_count,
            "network": NETWORK,
        }


if __name__ == "__main__":
    print(f"Quiv Network Agent v{AGENT_VERSION}")
    print("Demo mode — no live payments will be made.")

    agent = QuivAgent(private_key="0x_YOUR_PRIVATE_KEY_HERE")
    print(f"Agent initialized. Budget: {agent.budget} USDC units per request.")
    print("Ready.")
