#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

if ([ ! -e /usr/bin/jq ] || [ ! -e /usr/local/bin/aws ]); then
    exit 0
fi

update_hostname_file () {
    echo "$1" > /etc/hostname
    hostname "$1"
}

update_aws_name_tag () {
    aws ec2 create-tags --resources $(curl -s http://169.254.169.254/latest/meta-data/instance-id) --tags Key=Name,Value=$1
}

fully_change_hostname() {
    update_hostname_file $1
    update_aws_name_tag $1
    echo "127.0.0.1 localhost $1" > /tmp/new_hosts_file.txt
    tail -n +2 /etc/hosts >> /tmp/new_hosts_file.txt
    mv /tmp/new_hosts_file.txt /etc/hosts
}

# curl for instance availablility zone and configure aws tool
az=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
aws_region=$(echo $az | awk '{ string=substr($0, 0, length($0)-1); print string; }')
aws configure set region $aws_region

# Get the last 2 sets of number in local ip
ip_with_dashes=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 | tr -s '.' '-')
ip_last_2_numbers=${ip_with_dashes#*-*-}

if (expr "$(hostname)" : "^ip-*" 1>/dev/null) || (! echo $(hostname) | grep $ip_last_2_numbers 1>/dev/null); then 
    echo "Changing hostname..."
    current_name_tag=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)" "Name=key,Values=Name" | jq -r .Tags[0].Value)

    # if there's currently no name tag, let it be and not change hostname
    if [ -z "$current_name_tag" ]; then 
        echo "Instance does not have name tag. Not changing hostname."
    else
        new_hostname="${current_name_tag%-[0-9]*-[0-9]*}-$ip_last_2_numbers"
        fully_change_hostname $new_hostname
    fi 
else 
    echo "Hostname seems ok...Not changing."
fi 

exit 0

