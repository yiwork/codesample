#!/usr/bin/python

import re
from operator import itemgetter
try:
    import boto.ec2
    import boto.ec2.autoscale
    import boto.ec2.elb
    from boto.exception import BotoServerError
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False


def list_asgs(connections, module):
    asg_names = []
    if module.params.get("name"): 
        asg_names.append(module.params.get("name"))
    else:
        asg_names = module.params.get("names")

    sort_order = module.params.get("sort_order")
    if not asg_names:
        names_prefix = module.params.get("startswith") 
        names_suffix = module.params.get("endswith")

    try:
        all_asgs = connections['asg'].get_all_groups(names=asg_names)
    except BotoServerError as e:
        module.fail_json(msg = "%s: %s" % (e.error_code, e.error_message))

    if len(all_asgs) <= 0:
        module.exit_json(changed=False, asgs=None)

    asgs_array = []
    for asg in all_asgs:
        asg_info = {
            'name': asg.name,
            'load_balancers': asg.load_balancers,
            'min_size': asg.min_size,
            'max_size': asg.max_size,
            'desired_capacity': asg.desired_capacity,
            'health_check_period': asg.health_check_period,
            'health_check_type': asg.health_check_type,
            'instances': [i.instance_id for i in asg.instances],
            'instance_count': len(asg.instances) or 0,
            'availability_zones': asg.availability_zones,
            'termination_policies': asg.termination_policies,
            'vpc_zone_identifier': asg.vpc_zone_identifier,
            'launch_config': asg.launch_config_name, 
        }

        # if searching using startswith and endswith (i.e. no explicit names)
        if not asg_names:
            # if both prefix and suffix are specified return items that matches both conditions
            #name_pattern = '^{}{}$'.format(names_prefix or '', names_suffix or '')
            name_pattern = ''
            if names_prefix: 
                name_pattern += '^' + names_prefix 
            if names_suffix:
                name_pattern += names_suffix + '$'
            if ( re.match(name_pattern, asg.name) ):
                asgs_array.append(asg_info)
        else:   
            # if searching via explicit asg names, just append the string as the boto library has
            #   filtered it for us already
            asgs_array.append(asg_info)          

    module.exit_json( asgs=sorted(asgs_array, 
                                  key=itemgetter('name'), 
                                  reverse=(sort_order!='ascending')) )


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            name={'default': None, 'type': 'str'},
            names={'default': None, 'type': 'list'},
            startswith={'default': None, 'type': 'str'},
            endswith={'default': None, 'type':'str'},
            region={'default': 'us-east-1', 'type':'str'},
            sort_order={'required': False, 'default': 'ascending', 'choices':['ascending', 'descending'] },
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module)
    connections = {}
    if not region: 
        region = module.params.get("region")
    if region:
        try:
            connections['asg'] = connect_to_aws(boto.ec2.autoscale, region, **aws_connect_params)
            connections['elb'] = connect_to_aws(boto.ec2.elb, region, **aws_connect_params)
        except (boto.exception.NoAuthHandlerFound, AnsibleAWSError), e:
            module.fail_json(msg=str(e))
    else:
        module.fail_json(msg="region must be specified")

    list_asgs(connections, module)

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()