#!/usr/bin/python3
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

import sys
import json
import dnssync_nc
from .FriendlyArgumentParser import FriendlyArgumentParser

class NetcupCLI():
	def __init__(self, args):
		self._args = args
		self._nc = dnssync_nc.NetcupConnection.from_credentials_file(self._args.credentials)

	def _parse_dns_record(self, record_data):
		return dnssync_nc.DNSRecord.new(record_type = record_data["type"], hostname = record_data["hostname"], destination = record_data["destination"], priority = record_data.get("priority"))

	def _process_domain_layout(self, domain_layout):
		if self._args.verbose >= 2:
			print("Layout of domain %s consists of %d DNS records." % (domain_layout["domain"], len(domain_layout["records"])))

		current_dns_records = self._nc.info_dns_records(domain_layout["domain"])
		if (self._args.verbose >= 2) or (not self._args.commit):
			print("Current DNS records of %s (%d records):" % (current_dns_records.domainname, len(current_dns_records)))
			current_dns_records.dump()
			print()

		current_dns_records.delete_all()
		for new_dns_record in domain_layout["records"]:
			current_dns_records.add(self._parse_dns_record(new_dns_record))

		if (self._args.verbose >= 3) or (not self._args.commit):
			print("Proposed DNS update records of %s (%d records):" % (current_dns_records.domainname, len(current_dns_records)))
			current_dns_records.dump()
			print()

		if self._args.commit:
			if self._args.verbose >= 1:
				print("Commiting record of %s to live system." % (domain_layout["domain"]))

			updated_records = self._nc.update_dns_records(current_dns_records)
			if self._args.verbose >= 1:
				print("Successfully update DNS records of %s (%d records):" % (updated_records.domainname, len(updated_records)))
				updated_records.dump()
				print()
		else:
			if self._args.verbose >= 1:
				print("Not updating record of %s to live system (no commit requested)." % (domain_layout["domain"]))


	def _process_layout(self, layout_file, layout):
		if self._args.verbose >= 1:
			print("Processing layout file %s: %d domain entries found." % (layout_file, len(layout)))
		for domain_layout in layout:
			self._process_domain_layout(domain_layout)

	def run(self):
		with self._nc:
			for layout_file in self._args.layout_file:
				with open(layout_file) as f:
					layout = json.load(f)
				self._process_layout(layout_file, layout)

parser = FriendlyArgumentParser(description = "Update DNS records using the netcup DNS API.")
parser.add_argument("-c", "--credentials", metavar = "filename", type = str, default = "credentials.json", help = "Specifies credential file to use. Defaults to %(default)s.")
parser.add_argument("--commit", action = "store_true", help = "By default, only records are read and printed on the command line. This actually puts into effect the requested changes.")
parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increases verbosity. Can be specified multiple times to increase.")
parser.add_argument("layout_file", type = str, nargs = "+", help = "DNS layout file(s) that should be processed")
args = parser.parse_args(sys.argv[1:])

cli = NetcupCLI(args)
cli.run()
