import random

fail_agg_pod_one = random.choice([False, True])
fail_agg_pod_two = random.choice([False, True])
fail_core = random.choice([False, True])
pod_to_test = random.choice([1, 2, 3, 4])
second_pod_to_test = random.choice([1, 2, 3, 4])

exec_scripts = []
links = []

while second_pod_to_test == pod_to_test:
	second_pod_to_test = random.choice([1, 2, 3, 4])

#print("Testing pods: ", pod_to_test, ", ", second_pod_to_test)
#print("Fail agg pod one: ", fail_agg_pod_one)
#print("Fail agg pod two: ", fail_agg_pod_two)
#print("Fail core: ", fail_core)

failed_agg = -1
working_agg = -1

if fail_agg_pod_one:
	failed_agg = random.choice([pod_to_test * 2 - 1, pod_to_test * 2])
	if failed_agg == pod_to_test * 2 - 1:
		working_agg = pod_to_test * 2
	else:
		working_agg = pod_to_test * 2 - 1

	exec_scripts += ['''
			{{
      	"cmd": "sudo python link_failure_controller.py a{} cpu &",
      	"reboot_run": true
    	}}'''.format(working_agg)]
else:
	exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py a{0} cpu &",
      	"reboot_run": true
    	}}'''.format(pod_to_test * 2 - 1)]
	exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py a{} cpu &",
      	"reboot_run": true
    	}}'''.format(pod_to_test * 2)]

if fail_agg_pod_two:
	if not fail_agg_pod_one:
		failed_agg = random.choice([second_pod_to_test * 2 - 1, second_pod_to_test * 2])
		if failed_agg == second_pod_to_test * 2 - 1:
			working_agg = second_pod_to_test * 2
		else:
			working_agg = second_pod_to_test * 2 - 1

	else:
		failed_agg -= pod_to_test * 2
		failed_agg += second_pod_to_test * 2
		working_agg -= pod_to_test * 2
		working_agg += second_pod_to_test * 2

	exec_scripts += ['''
			{{
      	"cmd": "sudo python link_failure_controller.py a{} cpu &",
      	"reboot_run": true
    	}}'''.format(working_agg)]
else:
	exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py a{} cpu &",
      	"reboot_run": true
    	}}'''.format(second_pod_to_test * 2 - 1)]
	exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py a{} cpu &",
      	"reboot_run": true
    	}}'''.format(second_pod_to_test * 2)]

fail_core = True
if fail_core:
	if fail_agg_pod_one or fail_agg_pod_two:
		failed_core = 2 - (failed_agg % 2)

		if failed_core == 2:
			working_core = 1
		else:
			working_core = 2
	else:
		working_core = random.choice([1, 2])

	exec_scripts += ['''
			{{
      	"cmd": "sudo python link_failure_controller.py c{} cpu &",
      	"reboot_run": true
    	}}'''.format(working_core)]
else:
	exec_scripts += ['''
			{{
      	"cmd": "sudo python link_failure_controller.py c{} cpu &",
      	"reboot_run": true
    	}}'''.format(1)]
	
	exec_scripts += ['''
			{{
      	"cmd": "sudo python link_failure_controller.py c{} cpu &",
      	"reboot_run": true
    	}}'''.format(2)]


exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py t{} cpu &",
      	"reboot_run": true
    	}}'''.format(pod_to_test * 2 - 1)]

exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py t{} cpu &",
      	"reboot_run": true
    	}}'''.format(pod_to_test * 2)]

exec_scripts +=  ['''
			{{
      	"cmd": "sudo python link_failure_controller.py t{} cpu &",
      	"reboot_run": true
    	}}'''.format(second_pod_to_test * 2 - 1)]

hosts = []
links = []

for i in range(((pod_to_test - 1) * 4) + 1, ((pod_to_test - 1) * 4) + 5, 1): 
	hosts += ['''"h{}": {{}}'''.format(i)]
	links += ['''["h{}", "t{}", {{"bw": 10}}]'''.format(i, 1 + int((i - 1) / 2))]

for i in range(((second_pod_to_test - 1) * 4) + 1, ((second_pod_to_test - 1) * 4) + 3, 1): 
	hosts += ['''"h{}": {{}}'''.format(i)]
	links += ['''["h{}", "t{}", {{"bw": 10}}]'''.format(i, 1 + int((i - 1)/2))]

to_save = '''
{{
  "program": "p4src/link_failure.p4",
  "switch": "simple_switch",
  "compiler": "p4c",
  "options": "--target bmv2 --arch v1model --std p4-16",
  "switch_cli": "simple_switch_CLI",
  "cli": true,
  "pcap_dump": true,
  "enable_log": true,
  "exec_scripts": [
	{}
	],

  "topo_module": {{
    "file_path": "",
    "module_name": "p4utils.mininetlib.apptopo",
    "object_name": "AppTopoStrategies"
  }},
  "controller_module": null,
  "topodb_module": {{
    "file_path": "",
    "module_name": "p4utils.utils.topology",
    "object_name": "Topology"
  }},
  "mininet_module": {{
    "file_path": "",
    "module_name": "p4utils.mininetlib.p4net",
    "object_name": "P4Mininet"
  }},
  "topology": {{
    "assignment_strategy": "l2",
    "auto_arp_tables": false,
    "links": [{}, ["t1", "a1", {{"bw": 10}}], ["t1", "a2", {{"bw": 10}}], ["t2", "a1", {{"bw": 10}}], ["t2", "a2", {{"bw": 10}}], ["t3", "a3", {{"bw": 10}}], ["t3", "a4", {{"bw": 10}}], ["t4", "a3", {{"bw": 10}}], ["t4", "a4", {{"bw": 10}}], ["t5", "a5", {{"bw": 10}}], ["t5", "a6", {{"bw": 10}}], ["t6", "a5", {{"bw": 10}}], ["t6", "a6", {{"bw": 10}}], ["t7", "a7", {{"bw": 10}}], ["t7", "a8", {{"bw": 10}}], ["t8", "a7", {{"bw": 10}}], ["t8", "a8", {{"bw": 10}}], ["a1", "c1", {{"bw": 10}}], ["a1", "c2", {{"bw": 10}}], ["a2", "c3", {{"bw": 10}}], ["a2", "c4", {{"bw": 10}}], ["a3", "c1", {{"bw": 10}}], ["a3", "c2", {{"bw": 10}}], ["a4", "c3", {{"bw": 10}}], ["a4", "c4", {{"bw": 10}}], ["a5", "c1", {{"bw": 10}}], ["a5", "c2", {{"bw": 10}}], ["a6", "c3", {{"bw": 10}}], ["a6", "c4", {{"bw": 10}}], ["a7", "c1", {{"bw": 10}}], ["a7", "c2", {{"bw": 10}}], ["a8", "c3", {{"bw": 10}}], ["a8", "c4", {{"bw": 10}}]],

	"hosts" : {{ 

			{} 
						
	}},
    "switches": {{
	"t1": {{"cpu_port": true}},
	"t2": {{"cpu_port": true}},
	"t3": {{"cpu_port": true}},
	"t4": {{"cpu_port": true}},
	"t5": {{"cpu_port": true}},
	"t6": {{"cpu_port": true}},
	"t7": {{"cpu_port": true}},
	"t8": {{"cpu_port": true}},
	"a1": {{"cpu_port": true}},
	"a2": {{"cpu_port": true}},
	"a3": {{"cpu_port": true}},
	"a4": {{"cpu_port": true}},
	"a5": {{"cpu_port": true}},
	"a6": {{"cpu_port": true}},
	"a7": {{"cpu_port": true}},
	"a8": {{"cpu_port": true}},
	"c1": {{"cpu_port": true}},
	"c2": {{"cpu_port": true}},
	"c3": {{"cpu_port": true}},
	"c4": {{"cpu_port": true}}
    }}
  }}
}}
'''.format( 
						', \n'.join(exec_scripts),
						', '.join(links),
 						', \n'.join(hosts))

with open("test.json", "w") as f:
	f.write(to_save)
 	


