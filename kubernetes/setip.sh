#! /bin/bash
echo Setting /etc/hosts *.mss.mghpcc.org entries to $(minikube ip) and bouncing default dnsmasq...
sudo sed --in-place=.bck "s/\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}\s*\(\w*\.mss\.mghpcc\.org\)/$(minikube ip) \2/g" /etc/hosts
sudo pkill -HUP -f ^\.\*dnsmasq\.\*default.conf