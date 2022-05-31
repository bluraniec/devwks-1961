from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import requests

def requestNSO(method, url):
	if method == 'get':
		response = requests.get("http://172.16.238.2:8080/restconf/data/"+url, auth=('admin', 'admin'), 
			headers={'Content-type':'application/yang-data+json', 'Accept':'application/yang-data+json'}).json()
	elif method == 'post':
		response = requests.post("http://172.16.238.2:8080/restconf/data/"+url, auth=('admin', 'admin'), 
			headers={'Content-type':'application/yang-data+json', 'Accept':'application/yang-data+json'}).json()
	elif method == 'delete':
		response = requests.delete("http://172.16.238.2:8080/restconf/data/"+url, auth=('admin', 'admin'),
			headers={'Content-type':'application/yang-data+json', 'Accept':'application/yang-data+json'})
	return response

def show_devices(request):
	response = requestNSO('get','devices/device')

	device_name, address, port, device_type = ([] for i in range(4))

	for key, value in response.items():
		for i in range(0, len(value)):
			device_name.append(value[i]['name'])
			address.append(value[i]['address'])
			port.append(str(value[i]['port']))
			device_type.append(str(value[i]['device-type']))

	devices = zip(device_name, address, port, device_type)

	template = loader.get_template('show_devices.html')
	return HttpResponse(template.render({'devices':devices}, request))

def get_ACLs(request):
	result = []
	try:
		response = requestNSO('get','ACL_SERVICE')['ACL_SERVICE:ACL_SERVICE']

		device_name, interface, direction = ([] for i in range(3))
		device_types = ['ios', 'ios-xr', 'junos']

		for acl in range(0, len(response)):
			device_name.append(response[acl]['device'])
			for device_type in device_types:
				try:
					if response[acl][device_type]:
						interface.append(response[acl][device_type]['interface'])
						direction.append(response[acl][device_type]['direction'])
				except:
					pass
		result = zip(device_name, interface, direction)
	except:
		pass

	template = loader.get_template('get_ACLs.html')
	return HttpResponse(template.render({'result':result}, request))

def set_ACLs(request):
	if request.method == 'GET':
		response = requestNSO('get','devices/device')
		devices = []
		for key, value in response.items():
			for i in range(0, len(value)):
				devices.append(value[i]['name'])
		template = loader.get_template('set_ACLs.html')
		return HttpResponse(template.render({'devices':devices}, request))

	if request.method == 'POST':
		device = request.POST.get('device')
		name = request.POST.get('name')
		device_type = requestNSO('get','devices/device='+device+'/platform/name/')['tailf-ncs:name']
		device_interfaces = []
		if device_type == 'ios':
			response = requestNSO('get','devices/device='+device+'/config/tailf-ned-cisco-ios:interface/GigabitEthernet/')['tailf-ned-cisco-ios:GigabitEthernet']
			for interface in response:
				device_interfaces.append(interface['name'])
		elif device_type == 'ios-xr':
			response = requestNSO('get','devices/device='+device+'/config/tailf-ned-cisco-ios-xr:interface/GigabitEthernet/')['tailf-ned-cisco-ios-xr:GigabitEthernet']
			for interface in response:
				device_interfaces.append(interface['id'])
		elif device_type == 'junos':
			response = requestNSO('get','devices/device='+device+'/config/junos:configuration/interfaces/interface')['junos:interface']
			for interface in response:
				device_interfaces.append(interface['name'])

		template = loader.get_template('set_ACLs_submit.html')
		return HttpResponse(template.render({'device':device, 'name':name, 'device_interfaces':device_interfaces}, request))

def set_ACLs_submit(request):
	if request.method == 'POST':
		device = request.POST.get('device')
		name = request.POST.get('name')
		interface = request.POST.get('interface')
		direction = request.POST.get('direction')

		device_type = requestNSO('get','devices/device='+device+'/platform/name/')['tailf-ncs:name']

		response = requests.post('http://172.16.238.2:8080/restconf/data/',
   				data="{\"ACL_SERVICE:ACL_SERVICE\": [{\"name\": \""+name+"\",\"device\": \""+device+"\",\""+device_type+"\": {\"interface\": \""+interface+"\", \"direction\": \""+direction+"\"}}]}"
    				   , auth=('admin', 'admin'),
						 headers={'Content-type':'application/yang-data+json', 'Accept':'application/yang-data+json'})
		template = loader.get_template('message.html')
		return HttpResponse(template.render({'response':response}, request))

def delete_ACLs(request):
	response = requests.delete("http://172.16.238.2:8080/restconf/data/ACL_SERVICE",
                            auth=('admin', 'admin'), 
                            headers={'Content-type':'application/yang-data+json', 
                                     'Accept':'application/yang-data+json'})
	template = loader.get_template('message.html')
	return HttpResponse(template.render({'response':response}, request))





