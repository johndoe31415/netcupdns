#!/usr/bin/env python3
#	dnssync_nc - DNS API interface for the ISP netcup
#	Copyright (C) 2020-2020 Johannes Bauer
#
#	This file is part of dnssync_nc.
#
#	dnssync_nc is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	dnssync_nc is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with dnssync_nc; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import dnssync_nc

nca = dnssync_nc.NetcupConnection.from_credentials_file("credentials.json")
with nca:
	# Print the DNS zone info
	print(nca.info_dns_zone("my-domain.de"))

	# Set the DNS zone info to debugging timings
	print(nca.update_dns_zone(dnssync_nc.DNSZone.debug_values("my-domain.de")))

	# Retrieve DNS records, print them, delete a hostname and update
	dns_records = nca.info_dns_records("my-domain.de")
	dns_records.dump()
	dns_records.delete_hostname("bar.my-domain.de")
	dns_records = nca.update_dns_records(dns_records)
	dns_records.dump()

	# Add a new record
	new_records = dnssync_nc.DNSRecordSet("my-domain.de")
	new_records.add(dnssync_nc.DNSRecord.new("A", "bar.my-domain.de", "123.123.123.123"))
	updated_records = nca.update_dns_records(new_records)
	updated_records.dump()
