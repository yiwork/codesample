from fabric.api import local, run, env, settings, abort, sudo, put, prompt, get
from fabric.contrib.console import confirm
import boto

def get_unused_ebs_vol(vol_size=None, aws_zone=None, delete=False):
    """Returns a list of existing and unattached volumes that also contains the criteria specified in dict.
       currently allowed criterias - size (for minimum size), and zone"""
    
    conn = boto.connect_ec2()
    criteria = {
        'status':'available',
        'zone':aws_zone, 
    }

    vols = conn.get_all_volumes(None, {'status':'available'})
    vols_sorted = sorted(vols, key=attrgetter('zone', 'size'))
    for v in vols_sorted:
        print "%(v_id)s, %(v_zone)s, %(v_size)4d" % { "v_id": v.id, "v_zone":v.zone, "v_size":v.size}
        if delete:
           v.delete()
    return vols

def update_tags_per_instance_name():
    """ updates the tags associated with the instance name, ex. env, stack, subenv"""
    """ for instances in autoscale group a separate server_role tag is added in update """
    instances = get_all_running_instances()
    for instance in instances:
        #print "chking %s" % instance.tags['Name']
        name = instance.tags['Name'].replace(' ', '-').replace('_', '-').replace(')','-').replace('(','-')

        name_parts = name.split('-')
        env = name_parts[0]
        if name != 'jumpprod':
            stack = name_parts[1]
        subenv = ''
        zone_or_number = ''

        if len(name_parts) < 3:
            subenv = ''
        elif len(name_parts) > 3:
            # prod-spdj-tasks-d will have 'tasks' as subenv, d for zone_or_number
            # prod-corp-asg-web-d will have 'asg-web' as subenv, and d for zone_or_number
            subenv = '-'.join(name_parts[2:-1])
            zone_or_number = name_parts[-1]
        else:
            # 3 parts to the name
            if name_parts[2].isdigit() or len(name_parts[2]) <= 2:
                # ex. prod-rabbit-01 or dev-couchcluster-a1
                subenv = ''
                zone_or_number = name_parts[2]
            else:
                subenv = name_parts[2]

        # Section for overrides
        if 'v2' in stack or stack == 'pub':
            stack = 'spv2'
        elif subenv == 'ftp':
            stack = 'ftp'
        elif instance.tags['Name'] == PG_PROD_MASTER:
            subenv = 'master'
        elif name == "jumpprod":
            env='prod'
            stack='jumpprod'
            subenv=''
            zone_or_number=''
        else:
            pass
        
        instance.add_tag("env", env)
        instance.add_tag("stack", stack)
        instance.add_tag("subenv", subenv)
        instance.add_tag("zone_or_number", zone_or_number)
        instance.add_tag("status", 'active')
        #print "Tagged instance: %s | env: %s | stack: %s | subenv: %s | zone_or_number: %s" % (instance.tags['Name'], env, stack, subenv, zone_or_number)

def generate_ansible_inventory():
    """generates human readable ansible inventory with better logical grouping by name and put in /etc/ansible"""
    """Since this file can be used in conjunction witih dynamic inventory, groups names generated here will have sp_ beginning"""
    """need refactoring...srsly - offends my own standards, but let's get first draft up - yi"""

    env_inst = {}
    stack_inst = {}
    subenv_inst = {}
    status_inst = {}
    #myhash = _hash()
    myhash='test'
    tmpfile = '/tmp/hosts.ansible.%s' % myhash
    f = open(tmpfile,'w')
    
    ### group for status
    for status in ['active','inactive']:
        instances = get_all_instances('status', status, state='running')
        f.write("[sp_%s]\n" % status)
        status_inst[status] = {}

        for inst in instances:
            inst_name = inst.tags['Name']
            f.write("%s\n" % inst_name)
            status_inst[status][inst_name] = inst
        f.write('\n')

    ### group for environment    
    for env in ['dev', 'prod', 'qa']:
        instances = get_all_instances('env', env, state='running')
        f.write("[sp_%s]\n" % env)
        env_inst[env] = {}

        for inst in instances:
            inst_name = inst.tags['Name']
            f.write("%s\n" % inst_name)
            env_inst[env][inst_name] = inst     # preserve inst obj in event need other aws properties
        f.write('\n')

    ### group for stack
    for stack in ['spv2','spdj','couch','djsinglepage','singlepage','pubapi','corp','sapi','pg','ftp']:
        instances = get_all_instances('stack', stack, state='running')
        f.write("[sp_%s]\n" % stack)
        stack_inst[stack] = {}

        for inst in instances:
            inst_name = inst.tags['Name']
            f.write("%s\n" % inst_name)
            stack_inst[stack][inst_name] = inst
        f.write('\n')

    ### group for subenv
    for subenv in ['merchant','publisher','billing','toolkit','phi']:
        instances = get_all_instances('subenv', subenv, state='running')
        f.write("[sp_%s]\n" % env)
        subenv_inst[subenv] = {}

        for inst in instances:
            inst_name = inst.tags['Name']
            f.write("%s\n" % inst_name)
            subenv_inst[subenv][inst_name] = inst
        f.write('\n')

    # ### group for env-stack
    for env in env_inst.keys():
        for stack in stack_inst.keys():
            f.write("[sp_%s-%s]\n" % (env, stack))
            instance_set = set( env_inst[env].keys() ) & set( stack_inst[stack].keys() )
            if len(instance_set) > 0:
                for name in instance_set:
                    f.write("%s\n" % name)
                f.write('\n')
            else:
                f.write("\n")

    # ### group for env-subenv
    # # only dev and qa environments so far have a need for these.
    for env in ['dev','qa']:
        for subenv in ['merchant','publisher','billing','toolkit','phi']:
            f.write("[sp_%s-%s]\n" % (env, subenv))
            instance_set = set(env_inst[env].keys()) & set(subenv_inst[subenv].keys())
            if len(instance_set) > 0:
                for name in instance_set:
                    f.write("%s\n" % name)
                f.write('\n')
            else:
                f.write("\n")
