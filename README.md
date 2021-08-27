# Auto Fee Policy 

Establishing automatic fees policies.

[![Donate](https://img.shields.io/badge/Donate-Bitcoin-green.svg)](https://coinos.io/lukedevj)

## Requirements

- [Python >= 3.6](https://www.python.org/)
- [LND](https://github.com/LightningNetwork/lnd)
- [BOS](https://github.com/alexbosworth/balanceofsatoshis)

## Install
```bash
$ git clone https://github.com/lukedevj/autofeepolicy.git
$ cd ./autofeepolicy
$ python3 setup.py install --user
$ cd ..
```

## How to use?

### Configuration

```bash
$ autofeepolicy --help
Usage: autofeepolicy [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --datadir PATH  The path to lnd base directory.  [default: ~/.lnd]
  -n, --network TEXT  The network lnd is running  [default: mainnet]
  --help              Show this message and exit.

Commands:
  fees  Establishing automatic fees policies.

$ nano ~/.autofeepolicy/autofeepolicy.yaml
```

#### Expressions (How to use)

```yaml
# Will apply rules to all channels except channels outside this scope and channels that are in void.
all:
    - IF(OLP > 20, 20)

# Apply rules for this specific channel.
0318d4e22cf1f76766bb6c73ce0e83805e9a93b20dac05b357e1c926325c234423:
    # If "inbound" is greater than or equal to 82%, increase the forward rate to 600.
    - IF(ILP > 82, 600)
    # If the "outbound" is less than 25%, decrease the rate to 1 otherwise increase to 5.
    - IF(OLP < 25, 1, 5)
    # Expresions: (not < > >= <= != | LIQUIDITY INBOUND OUTBOUND OLP ILP)

# Avoid (x and y).
avoid:
    - 02eda3fc37f5c7d8d3cbc999b5b9c4fdb58ca6736ff267c575bbc8f779994fa882
```

Testing the software without applying the rules.

```bash
# Testing the software and avoiding specific channels.
$ autofeepolicy fees
# Outbound is not less than 25%, so it should be applied at a rate of 5.
+----------------------------+-------------+--------------+-----------------+------------+
|             Id             | Inbound (%) | Outbound (%) |     Capacity    | Fee Policy |
+----------------------------+-------------+--------------+-----------------+------------+
| 0dac05b357e1c926325c234423 |     73%     |     28%      | $ 1,960,000 sat |     5      |
+----------------------------+-------------+--------------+-----------------+------------+
```

We can also pass the avoid as an argument.
```
$ autofeepolicy fees --avoid 0318d4e22cf1f76766bb6c73ce0e83805e9a93b20dac05b357e1c926325c234423
+----------------------------+-------------+--------------+-----------------+------------+
|             Id             | Inbound (%) | Outbound (%) |     Capacity    | Fee Policy |
+----------------------------+-------------+--------------+-----------------+------------+
| 6ff267c575bbc8f779994fa882 |     72%     |     29%      | $ 1,960,000 sat |     20     |
+----------------------------+-------------+--------------+-----------------+------------+
# As I only have two payment channels I had to remove 6ff267c575bbc8f779994fa882 from the configuration for it to work.
```
To apply the tax policy rules you must pass --activate-policy-auto as an argument
```
$ autofeepolicy fees --activate-policy-auto
+----------------------------+-------------+--------------+-----------------+------------+
|             Id             | Inbound (%) | Outbound (%) |     Capacity    | Fee Policy |
+----------------------------+-------------+--------------+-----------------+------------+
| 0dac05b357e1c926325c234423 |     73%     |     28%      | $ 1,960,000 sat |     5      |
| 6ff267c575bbc8f779994fa882 |     72%     |     29%      | $ 1,960,000 sat |     20     |
+----------------------------+-------------+--------------+-----------------+------------+
```

## Cronjob
```
$ which autofeepolicy
/home/linux/.local/bin/autofeepolicy

$ which python3
/usr/bin/python3

$ crontab -e
# m h  dom mon dow   command
*/10 * * * * /usr/bin/python3 /home/linux/.local/bin/autofeepolicy fees --activate-policy-auto
```

