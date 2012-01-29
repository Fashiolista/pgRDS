# Copyright (C) 2011, 2012 9apps B.V.
# 
# This file is part of Redis for AWS.
# 
# Redis for AWS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Redis for AWS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Redis for AWS. If not, see <http://www.gnu.org/licenses/>.

import os, sys, re, subprocess
import json, urllib2

from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo

from route53 import Route53Zone

try:
	url = "http://169.254.169.254/latest/"

	userdata = json.load(urllib2.urlopen(url + "user-data"))
	instance_id = urllib2.urlopen(url + "meta-data/instance-id").read()
	hostname = urllib2.urlopen(url + "meta-data/public-hostname/").read()

	zone = urllib2.urlopen(url + "meta-data/placement/availability-zone").read()
	region = zone[:-1]

	zone_name = os.environ['HOSTED_ZONE_NAME']
	zone_id = os.environ['HOSTED_ZONE_ID']
except Exception as e:
	exit( "We couldn't get user-data or other meta-data...")

pg_dir = '/var/lib/postgresql/9.1/'

if __name__ == '__main__':
	region_info = RegionInfo(name=region,
							endpoint="ec2.{0}.amazonaws.com".format(region))
	ec2 = EC2Connection(sys.argv[1], sys.argv[2], region=region_info)
	r53_zone = Route53Zone(sys.argv[1], sys.argv[2], zone_id)

	# the name (and identity) of SOLR
	name = "{0}.{1}".format(userdata['name'],
						os.environ['HOSTED_ZONE_NAME'].rstrip('.'))

	if sys.argv[3] == "start":
		r53_zone.create_record(name, hostname)
		ec2.create_tags( [instance_id], { "Name": name })
		print "start"
	elif sys.argv[3] == "stop":
		r53_zone.delete_record(name)
		ec2.delete_tags( [instance_id], ["Name"])
		print "stop"
	elif sys.argv[3] == "restart":
		print "restart"
	elif sys.argv[3] == "reload":
		print "reload"
	else:
		print "else"
