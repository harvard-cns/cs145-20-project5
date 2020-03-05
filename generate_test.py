import os

print("Which topology do you want to test on? (P = single pod. F = full fat tree.)")
c = input("P/F:")
assert(c == "P" or c == "F")
print("Options:")
print("1: no failure.")
print("2: aggregate switch failure")
if c == "F":
	print("3: core switch failure")
	print("4: randomly generated failures")
o = int(input("Option:"))
if o == 1:
	if c == "P":
		os.system("cp tests/fat_tree_app_one_pod.json test.json")
	else:
		os.system("cp tests/fat_tree_app.json test.json")

elif o == 2:
	if c == "P":
		os.system("cp tests/fat_tree_app_one_pod_agg_failure.json test.json")
	else:
		os.system("cp tests/fat_tree_app_agg_failure.json test.json")

elif o == 3:
	os.system("cp tests/fat_tree_app_core_failure.json test.json")

elif o == 4:
	os.system("python3 tests/generate_random_failures.py")


