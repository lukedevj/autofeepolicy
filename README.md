# Auto Fee Policy 

Establishing automatic fees policies.

## Requirements

- `(Python >= 3.6, LND, BOS)`

## Install
```bash
$ git clone https://github.com/lukedevj/autofeepolicy.git
$ cd ./autofeepolicy
$ python3 setup.py install
$ cd ..
```

## How to use?

### Configuration

```bash
$ autofeepolicy --help
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

+----------------------------+-------------+--------------+-----------------+------------+
|             Id             | Inbound (%) | Outbound (%) |     Capacity    | Fee Policy |
+----------------------------+-------------+--------------+-----------------+------------+
| 0dac05b357e1c926325c234423 |     73%     |     28%      | $ 1,960,000 sat |   5 sat    |
+----------------------------+-------------+--------------+-----------------+------------+
```


