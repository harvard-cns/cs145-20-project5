# Project 5: Failure Recovery and ARP Table

<!-- 
![#1589F0](https://placehold.it/15/1589F0/000000?text=+) TODO Begins:

### Implementing ARP by yourself

Discussing with students we enable automatic arp in previous setting. Now we need them to hand arp. 

![#f03c15](https://placehold.it/15/f03c15/000000?text=+) TODO Ends -->

# Objectives

- Learn how a switch can dynamically adapt its routes
	- Learn communication patterns that are used to share state between the data plane and the control plane of a switch.
	- Understand how the control plane can be used to programmatically set up and update the routing logic in a network.
	- Get acquainted with the Address Resolution Protocol (ARP) and understand how it works.

- Learn how to handle common failures in networks.
	- Learn about redundancy in networks.
	- Run a more intelligent controller on programmable switches that leverages path redundancy.

# Introduction
<!-- Network failures are not an unlikely occurrence, but a *matter of routine* in data centers. While handling failures can be done at the application level, cloud computing companies often do not have (and do not *want* to have) control over the applications that users run on their network. Hence it is necessary for the network itself (i.e switches, servers and/or controllers) to detect and circumvent failures. Handling a failure requires there to be redundancy in the network; an example of this you have already seen is how there are multiple paths between hosts in different pods in a fat tree topology). However, in addition to this redundancy, it is also necessary for switches to be smart enough to dynamically take advantage of this redundancy. To do this, we can no longer rely on statically configured routes. Instead, we must add routing logic adaptation to the switch's functionality.  -->

In this project, you are expected to add the ARP learning function. You will also add a failure recovery function that figure out an alternate path (if one exists) to a host during failures. 

The code you need to modify for this project is in the following files:

- `p4src/link_failure.p4`: the skeleton of the p4 program. This needs several additions to make the switch "learn" new paths. 

- `controller/link_failure_controller.py`: The skeleton of the controller. You should be able to correctly handle link failures by adding only a few lines to this.

## Part One: Programming the Ingress Pipeline (ARP Learning)

If the datapath sees a packet with an `src_mac` it has not seen before, it takes note of the ingress port the packet was received from and informs the controller that it can reach host `src_mac` by forwarding to that port. It forms the controller of this by *cloning* the packet and sending it to the controller. Here is how to do that:

- You need to add a new header (call it `cpu_t`) that will be added to the original packet. Give it two fields: mac addresss (48 bits) and input port (16 bits). Remember that in p4 you can get the ingress port of a packet by the metadata field `standard_metadata.ingress_port` so you will need to copy this value to your `cpu_t` header.

- Add this new header to the headers struct.

- Add a new metadata field called `ingress_port`. (this part has been done for you)

- You have already been provided with two tables: `broadcast` and `dmac`. `dmac` is just a regular forwarding table that matches a destination mac address and forwards it to a port. The `broadcast` table is applied when no match was seen by `dmac`.

- Define a new table called `smac`. This table adds rules for all `src_mac` addresses it sees. Give it two actions: `mac_learn` and `NoAction`. If `src_mac` has not been seen before, apply `mac_learn`. Otherwise, apply `NoAction` (i.e do nothing). 

- In the apply logic, first apply `smac`. Then apply `dmac`. If `dmac` does not have a match, apply `broadcast`.

- In `mac_learn`, set the `ingress_port` metadata field (defined in an earlier step) to `standard_metadata.ingress_port`. Then call the function `clone3(CloneType.I2E, 100, meta)` to clone the packet at the end of the ingress pipeline. You do not need to understand how this function works, just the fact that is clones the packet.

Note: in the previous experiments, we enabled automatic ARP table learning by ignoring `"auto_arp_tables"` option of `"topology"` in `p4app.json` file; in this project, we set `"auto_arp_tables"` to `false`, and let you to implement the ARP table learning. 

## Part Two: Programming the Egress Pipeline

Since you called `clone3`, the packet has now been cloned and is in the egress pipeline. Here you have to do the following:
- Check if `instance_type` equals `1` (i.e the packet is a clone)

- Then set the `cpu_t` header to be vald by using `setValid()`. Fill the `cpu_t` header with the mac source address and ingress port.

- Set `hdr.ethernet.etherType` to `0x1234`. This is so the controller can identify the packet as a control packet. 

- Emit the new header you created.

## Part Three: Programming the Controller

You have already been provided a fully functional controller (`link_failure_controller.py`). The controller has a function called `learn` which will be called each time the switch sends a control packet. You need to use the method `self.controller.table_add()` (which works the same way as the `table_add` primitive in the CLI scripts) to add rules to the `smac` and `dmac` tables. This requires only a couple of lines of code. 

## Automated Testing

We have provided an interface called `generate_test.py` that allows you to test multiple cases individually including aggregate switch failures, core switch failures and their combinations. The final option creates a randomly generated set of failures. Begin by testing individual failures and then do a complete test on a randomly generated set of failures once you are confident your solution works.

After each run, `generate_test.py` creates a file called `test.json`. You can run it using
```
sudo p4run --conf test.json
```
along with your learning controller and then do a `pingall` in mininet.


<!--
- `fat_tree_app.json` (4-port Fat-Tree without failures)
- `fat_tree_app_agg_failure.json` (4-port Fat-Tree with one aggregate switch failed)
- `fat_tree_app_core_failure.json` (4-port Fat-Tree with one core switch failed) 
-->

If `pingall` shows no drops for multiple cases, your solution is correct. We will test your solution on randomly generated failure patterns.

## Submission and Grading

### What to submit
You are expected to submit the following documents:

1. `p4src/link_failure.p4`: with your data plane implementation of link failure handling.
2. `controller/link_failure_controller.py`: completed controller implementation with link failure handling.
3. `report/report.txt` (or `report.md`): In this file you should describe how you program the ingress and egress pipeline, and controller. 

### Grading 

The total grades is 100:

- 20: For your description of how you program in README.txt.
- 20: For passing the automated tests.
- 60: We will manually check the correctness of your solutions for failure handling. 
- Deductions based on late policies
