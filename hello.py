#!/usr/bin/python

import json
import urllib2
import time
import sys

#for some reason blockchain.info api-chain is 59711 blocks short..
#blockstart = 170399
#blockstart += 59711
#blockcount = urllib2.urlopen("https://blockchain.info/en/q/getblockcount").read()
#1PPVzjfPZece9mwJKdPB5Kbhv4JiSemFCu (not found is true)
#1GXFXm3esL7Hh8rmvAme1YHKhYAnT1d7Sr (found 1 is true)

def rscan(addr):
	"""Check address for duplicated r values."""
	# TODO: add BCI API check address

	print "WELCOME TO R-scan v0.1.16!"
	print "ADDRESS-R-SCAN: "
	
	urladdr = 'https://blockchain.info/address/%s?format=json&offset=%s'

	###control api-url
	#print str(urladdr[:-22] % addr)

	addrdata = json.load(urllib2.urlopen(urladdr % (addr, '0')))
	ntx = addrdata['n_tx']
	print "Data for pubkey: " + str(addr) + " has " + str(addrdata['n_tx']).center(6) + "Tx%s" % 's'[ntx==1:]
	#print "number of txs: " + str(addrdata['n_tx'])

	#tx-details:

	txs = []
	for i in range(0, ntx//1000 + 1):
		sys.stderr.write("Fetching Txs from offset\t%s\n" % str(i*1000))
		jdata = json.load(urllib2.urlopen(urladdr % (addr, str(i*1000))))
		txs.extend(jdata['txs'])	

	assert len(txs) == ntx
	addrdata['txs'] = txs


	y = 0
	inputs = []
	blokInd = []
	txids = []
	while y < ntx:	
		#print "#################################################################################"
		#print "TX nr :" + str(y+1)
		#print "hash: " + str(addrdata['txs'][y]['hash'])
		#print "number of inputs: " + str(addrdata['txs'][y]['vin_sz'])
		#only if
		#if addrdata['txs'][y]['vin_sz'] > 1:
		zy = 0
		while zy < addrdata['txs'][y]['vin_sz']:
			#print "Input-ScriptNR " + str(zy+1) + " :" + str(addrdata['txs'][y]['inputs'][zy]['script'])
			if 'addr' in addrdata['txs'][y]['inputs'][zy]['prev_out'] and addrdata['txs'][y]['inputs'][zy]['prev_out']['addr'] == addr:
				inputs.append(addrdata['txs'][y]['inputs'][zy]['script'])
				blokInd.append(addrdata['txs'][y]['block_index'])
				txids.append(addrdata['txs'][y]['hash'])
			zy += 1
		y += 1

	xi = 0
	zi = 1
	lenx = len(inputs)
	alert = 0
	
	bad = []
	bad2 = dict()
	#compare the sig values in each input script
	while xi < lenx-1:
		x = 0
		while x < lenx-xi-1:
			if inputs[xi][10:74] == inputs[x+xi+1][10:74] and inputs[xi]<>inputs[x+xi+1] and xi<>x+xi+1:
				#print "In Input NR: " + str(xi) + "[global increment] xi='" + str(inputs[xi]) + "' x+xi+1='" +str(inputs[x + xi + 1]) + "' "
				bad.append((int(xi), str(inputs[xi][10:74]), int(x+xi+1)))
				if str(inputs[xi][10:74]) not in bad2:
					bad2[str(inputs[xi][10:74])] = dict()
				bad2[str(inputs[xi][10:74])][str(xi)] = str(xi)
				bad2[str(inputs[xi][10:74])][str(x+xi+1)] = str(x+xi+1)
				alert += 1
				xi += 1
			x += 1
		xi += 1
		
	for RUsed in bad2:
		print "Resued R-Value: "
		print "R:" + str(RUsed)
		for PosIn in bad2[RUsed]:
			print "In BlockIndex:" + str(blokInd[int(PosIn)]) + " \tTxId:" + str(txids[int(PosIn)])
		print "\n"
	
	
	if alert < 1:
		print "Good pubKey. No problems."
	else:
		print "Address %s has %d reused R value%s!" % (addr, len(bad2), "s"[len(bad2)==1:])
		return bad
		
if __name__ == '__main__':
	from sys import argv
	print """Welcome to rscan"""
	if len(argv) == 1:
		addr = raw_input("type address:  ")
	elif len(argv) == 2 and isinstance(argv[1], basestring):
		addr = str(argv[1])
	rscan(addr)
	
# 9ec4bc49e828d924af1d1029cacf709431abbde46d59554b62bc270e3b29c4b1
