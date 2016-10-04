from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

try: 
    from boto.vpc import VPCConnection 
except ImportError:
    pass

class LookupModule(LookupBase):
    """
    lookup('vpc', 'id tag1=value1 tag2=value2')

    to lookup vpc id by name tag:
    lookup('vpc', 'id name=svceap')
    """

    def run(self, terms, variables=None, **kwargs):
    	ret = []

        # Below i will implement 
        valid_lookups = {
             'id' : None
             'dhcp_options_id' : None 
             'state' : None 
             'cidr_block' : None    
             'is_default' : None    
             'instance_tenancy' : None
             'classic_link_enabled' : None
        }
        conn = VPCConnection()
        for term in terms:
        	params = term.split(' ')
        	key_to_lookup = params[0]
            try:
                assert( key_to_lookup in valid_lookups ) 
            except (AssertionError) as e:
                raise AnsibleError(e)

            vpc_filter = {}
            for param in params[1:]:
                tag, value = param.split('=')
                vpc_filter.update({'tag:'+ tag : value})
        
            vpcs = conn.get_all_vpcs(None, vpc_filter)
            if len(vpcs) > 1:
                ret = [ x.get( key_to_lookup ) for x in vpcs ]
            return ret

        	


