from prettytable import PrettyTable
from .utils.helpers import (
    touchdir, touchfile, expanduser, 
    updatepolicyfee, percentage,
    which, system
)
from yaml import safe_load
import click

PATH = touchdir('~/.autofeepolicy')
CONF = touchfile(f'{PATH}/autofeepolicy.yaml')

with open(CONF, 'r') as file:
    config = safe_load(file)
    if not (config):
        config = {}

@click.group()
@click.option(
    '--datadir', '-d', help='The path to lnd base directory.', show_default=True, default='~/.lnd', type=click.Path()
)
@click.option(
    '--network', '-n', help='The network lnd is running', show_default=True, default='mainnet', type=click.STRING
)
@click.option(
    '--restlisten', '-r', help='Specify your nodes REST API hos and port.', type=click.STRING
)
@click.pass_context
def cli(ctx, datadir: str,  network: str, restlisten: str):
    ctx.ensure_object(dict)
    ctx.obj['datadir'] = expanduser(datadir)
    ctx.obj['network'] = network
    ctx.obj['restlisten'] = restlisten

@cli.command()
@click.option(
    '--node', '-n', help='Use a specific node configured in Balance of Satoshi.'
)
@click.option(
    '--avoid', '-a', help='Specify all channels that should be avoided.', multiple=True
)
@click.option(
    '--activate-policy-auto', '-p', is_flag=True, help='Activate automated fee policy.'
)
@click.pass_context
def fees(ctx, node: str, avoid: tuple, activate_policy_auto: bool):
    '''
    Establishing automatic fees policies.\n
    To edit the rules:\n
        $ nano ~/.autofeepolicy/autofeepolicy.yaml
    '''
    from .grpc import Grpc

    grpc = Grpc(
        datadir=ctx.obj['datadir'], 
        network=ctx.obj['network'],
        restlisten=ctx.obj['restlisten']
    )
    table = PrettyTable([
        'Channels', 'Alias', 'Total Inbound (%)', 'Total Outbound (%)', 
        'Total Reserve (%)', 'Total Capacity', 'Fee Policy', 
    ])

    avoid_identifiers = set(config.get('avoid') if config.get('avoid') else {})
    avoid_identifiers.update(avoid)

    channel_identifiers = set(
        channel['remote_pubkey'] for channel in next(grpc.listchannels()) \
            if not (channel['remote_pubkey'] in avoid_identifiers)
    )
    if not channel_identifiers:
        click.echo('[!] No channels were found.')
        raise click.Abort()
    
    channel_policies = {}
    for x in channel_identifiers:
        v = config.get('all')
        if (v != None):
            channel_policies[x] = v
        
        k = config.keys()
        if (x in k):
            v = config.get(x)
            channel_policies[x] = (
                v if (v != None) else []
            )

    if not (channel_policies):
        click.echo(f'[!] No rules were found in {CONF}.')
        raise click.Abort()

    for identify in channel_identifiers:
        total_remote_reserve, total_local_reserve = (0, 0)
        total_inbound, total_outbound, total_capacity = (0, 0, 0)
        channel_alias = next(grpc.getnodeinfo(identify))['alias']
        total_channels = 0
        for channel in next(grpc.filterchannel(identify)):
            remote_balance = int(channel['remote_balance']) 
            remote_reserve = int(channel['remote_chan_reserve_sat'])
            if (remote_balance >= remote_reserve):
                total_remote_reserve += remote_reserve
            total_inbound += remote_balance

            local_balance = int(channel['local_balance'])
            local_reserve = int(channel['local_chan_reserve_sat'])
            if (local_balance >= local_reserve):
                total_local_reserve += local_reserve
            
            total_outbound += local_balance
            total_capacity += int(channel['capacity'])
            total_channels += 1

        outbound_capacity_percentage = percentage(total_outbound, total_capacity)
        inbound_capacity_percentage = percentage(total_inbound, total_capacity)
        reserve_capacity_percentage = percentage(
            total_local_reserve + total_remote_reserve, total_capacity
        )

        channels_fee_policy = {}
        for x in channel_policies.get(identify, []):
            if not ('IF' in x): continue

            formula = str(x[3:].split(',')[0])
            if ('INBOUND' in formula):
                formula = formula.replace('INBOUND', str(total_inbound))
            
            if ('OUTBOUND' in formula):
                formula = formula.replace('OUTBOUND', str(total_outbound))
            
            if ('LIQUIDITY' in formula):
                formula = formula.replace('LIQUIDITY', str(total_capacity))
            
            if 'OLP' in formula: 
                formula = formula.replace('OLP', str(outbound_capacity_percentage))
            
            if ('ILP' in formula):
                formula = formula.replace('ILP', str(inbound_capacity_percentage))

            resolve = eval(formula)
            fees = list(map(
                lambda x: x.strip().replace(')', ''), x.split(',')[1:]
            ))
            if (len(fees) <= 1) and (resolve == False): continue

            result = (fees[0] if (resolve == True) else fees[1])
            if isinstance(resolve, bool) and (len(fees) <= 2):
                resolve = ('true' if (resolve == True) else 'false')
                formula = '"IF(%s,%s)"' % (resolve, ','.join(fees))
                
                set_fee_policies = updatepolicyfee(
                    node=node, formula=formula, to=identify
                ) if (activate_policy_auto == True) else True

                if set_fee_policies:
                    channels_fee_policy[identify] = result

        if channels_fee_policy.get(identify):
            table.add_row([
                total_channels,
                channel_alias, 
                "{:.2f}%".format(inbound_capacity_percentage), 
                "{:.2f}%".format(outbound_capacity_percentage),
                "{:.2f}%".format(reserve_capacity_percentage),
                "{:0,.0f} sat".format(total_capacity), 
                f"{channels_fee_policy[identify]}"
            ])

    click.echo(table)