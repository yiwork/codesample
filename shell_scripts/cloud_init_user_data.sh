#!/bin/bash

instid=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
az=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)

aws configure set region ${az::(-1)}
my_s3_bucket='yi_devops_bucket'

# awstag:env - attempt to get required 'env' tag 5 times before trying to find bootstrap tag
for i in `seq 1 5`; do
    env=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$instid" "Name=key,Values=env" | jq -r .Tags[0].Value)
    if [ $? -ne 0 -o "$env" == 'null' ]; then 
        sleep 2
    else    
        break
    fi
done 

# awstag:bootstrap
# We should've gotten the env tag, now try the bootstrap tag. only need to try once. 
#    Since bootstrap tag isn't required, we get this after we try to get 'env' tag so we get more definitive
#    test on whether meta data is more delayed, or the tags aren't set. 
bootstrap_tag=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$instid" "Name=key,Values=bootstrap" | jq -r .Tags[0].Value)
if [ "$bootstrap_tag" != 'null' ]; then 
    echo "Bootstrap tag: $bootstrap_tag"
    echo "Download and run alternate bootstrap file..."
    aws s3 cp s3://$my_s3_bucket/bootstrap/$bootstrap_tag /root && chmod u+x "/root/$bootstrap_tag" && exec "/root/$bootstrap_tag"
fi 

if [ "$env" == 'null' ]; then
    echo "Aborting rest of bootstrap effort. env tag isn't set."
    exit 1 
fi  

if [ -d /root/ansible_repo ]; then 
    rm -fr /root/ansible_repo
fi 

# Checking to see if there's a different branch of devops repo this is suppose to use
# awstag: devops_repo_branch
devops_repo_branch=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$instid" "Name=key,Values=devops_repo_branch" | jq -r .Tags[0].Value)
if [ "$devops_repo_branch" == 'null' ]; then
    devops_repo_branch='master'
fi  

# Download playbooks from git or s3
git clone -b $devops_repo_branch git@github.com:yiwork/ansible_repo.git /root/ansible_repo

# if git fails, grab old copy from s3...
if [ $? -ne 0 ]; then
    aws s3 cp s3://$my_s3_bucket/ansible_repo.tar.gz /tmp
    tar zxvf /tmp/ansible_repo.tar.gz -C /root
fi 

cd /root/ansible_repo/

# awstag: service
utils/ec2_tags_json $instid service > /tmp/awstags.txt
service=$(jq '.service' -r /tmp/awstags.txt)

if [ "$service" == 'null' ]; then
    echo "Aborting rest of bootstrap effort. service tag isn't set."
    exit 1 
fi 

# awstag: <service_name>
utils/ec2_tags_json $instid $service > /tmp/awstags_$service.txt

# awstag: extract pb: section of  <service_name> tag
playbook=$(jq ".$service | .[] | objects | select(has(\"pb\")) | .pb" -r /tmp/awstags_$service.txt)

export ANSIBLE_HOME=/root/ansible_repo/ansible
export ANSIBLE_CONFIG="$ANSIBLE_HOME/ansible_cfg/$env.ansible.cfg"
export EC2_INI_PATH="$ANSIBLE_HOME/inventory/$env/ec2.ini"
export HOME=/root

public_hostname=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname)
public_ip=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

printenv

if [ -n "$playbook" -a "$playbook" != "null" ]; then
    echo "Running playbook dextro_services/$service/$playbook.yml..."
    ansible-playbook --limit=$public_hostname --limit=$public_ip --connection=local $ANSIBLE_HOME/$service/$playbook.yml 
else
    echo "Running playbook dextro_services/$service/main.yml..."
    ansible-playbook --limit=$public_hostname --limit=$public_ip --connection=local $ANSIBLE_HOME/$service/main.yml 
fi 

exec /etc/rc.local
