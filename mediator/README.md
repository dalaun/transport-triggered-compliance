# Mediator-Canonizer API

Canonical dispute resolution for autonomous agents.

## Base URL

http://76.13.107.248:8745

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | / | None | Service info |
| GET | /health | None | Health check |
| POST | /mediate | x402 $0.05 USDC | Mediate + on-chain |
| POST | /mediate/free | None | Dev/test only |

## Payment (x402)

POST /mediate requires $0.05 USDC on Base mainnet (Chain ID: 8453).

1. Send request without payment -- receive 402 with requirements
2. Pay $0.05 USDC to 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A
3. Resend with X-PAYMENT header (base64-encoded proof)
4. Receive frozen canon artifact + on-chain TX

## On-Chain Registry

- Contract: 0xf2325531264CA4Fc2cEC5D661E2200eA8013b091
- Network: Base mainnet (8453)
- Explorer: https://basescan.org/address/0xf2325531264CA4Fc2cEC5D661E2200eA8013b091

## Canon Protocol

Implements CMP v1.0 -- DOI: https://doi.org/10.5281/zenodo.18746444

## Operator

- Wallet: 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A
- ENS: canonizer.base.eth
- GitHub: https://github.com/dalaun/transport-triggered-compliance