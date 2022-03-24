import os
from time import sleep
import random
import json
from typing import List
from dataclasses import dataclass

@dataclass
class TargetBank():
    file_name: str
    targets: List[str]

SWAP_TIMEOUT = 60*20

def load_all_targets():
    target_banks: List[TargetBank] = []

    for filename in os.listdir('./targets'):
        f = os.path.join('./targets', filename)
        if os.path.isfile(f):
            lines = []
            with open(f, "r") as fp:
                lines = fp.readlines()
            lines = list(filter(lambda l: l != "" and l != " ", lines))
            lines = [ l.strip().replace(" ", "").replace("\n", "") for l in lines]

            target_banks.append(TargetBank(filename, lines))

    return target_banks
    

def apply_target(json_data):
    #prepare environment
    if not os.path.isdir('./repo'):
        r = os.system('ssh-agent bash -c "ssh-add ./push_key; git clone git@github.com:opengs/uashieldtargets.git -b v2 repo"')
        if r != 0:
            print(f"Fail to clone git repo. Exit code {r}")
            raise Exception()

    #pull repo
    r = os.system('cd repo && ssh-agent bash -c "ssh-add ../push_key; git pull"')
    if r != 0:
        print(f"Fail to pull git repo. Exit code {r}")
        raise Exception()


    #modify targets file
    with open("./repo/sites.json", "w") as fp:
        json.dump(json_data, fp)

    #commit repo
    r = os.system('cd repo && ssh-agent bash -c "ssh-add ../push_key; git add ."')
    if r != 0:
        print(f"Fail to add files to git repo. Exit code {r}")
        raise Exception()

    r = os.system('cd repo && ssh-agent bash -c "ssh-add ../push_key; git commit -m targets"')
    if r != 0:
        print(f"Fail to commit files to git repo. Exit code {r}")
        raise Exception()

    #push repo
    r = os.system('cd repo && ssh-agent bash -c "ssh-add ../push_key; git push"')
    if r != 0:
        print(f"Fail to push git repo. Exit code {r}")
        raise Exception()
    
    
    print("Target updated")

def main():
    #load targets to the system

    banks = load_all_targets()

    while True:
        random.shuffle(banks)

        for bank in banks:
            print("Loading data bank: " + bank.file_name)
            
            #convert data to json format
            json_out = []
            for target in bank.targets:
                json_out.append({ 
                    "method": "get",
                    "page": target
                })
            
            apply_target(json_out)

            to_sleep = SWAP_TIMEOUT
            while to_sleep > 0:
                sleep(1)
                to_sleep -= 1

main()