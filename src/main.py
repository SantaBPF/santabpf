import glob
import time
import yaml

if __name__ == '__main__':
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
    
    passive_scenarios = glob.glob('scenarios/passive/[!_]' + config['passive_scenarios'] + '.py')
    
    while True:
        for scenario in passive_scenarios:
            scenario.monitor()
        time.sleep(config['core']['monitor_interval_sec'])
    
