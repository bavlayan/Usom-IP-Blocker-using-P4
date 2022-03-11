import json
import Constants
import sys
from BlockedUrl import BlockedUrl

switch_settings_dictionary = None
usom_blocked_url_list = None

def create_dropped_table_entries():
    try:
        if switch_settings_dictionary is not None and usom_blocked_url_list is not None:
            current_table_entires = switch_settings_dictionary['table_entries']
            for usom_blocked_url in usom_blocked_url_list:
                blocked_ip = usom_blocked_url['ip']                
                drop_object = {
                    'table': 'MyIngress.ipv4_lpm',
                    'match': {
                        'hdr.ipv4.dstAddr': [blocked_ip, 32]
                    },
                    'action_name' : 'MyIngress.drop',
                    'action_params' : {}
                }
                current_table_entires.append(drop_object)
            switch_settings_dictionary['table_entries'] = current_table_entires
            return switch_settings_dictionary
    except:
        print("An error occured in create_dropped_table_entries method")
        sys.exit()

def load_json_by_file_name(json_file_name):    
    with open(json_file_name) as json_file:
        result_dictionary = json.load(json_file)
        return result_dictionary

def write_json_to_file(json_dic, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(json_dic, outfile, default=vars, indent=2)
    
if __name__ == "__main__":
    switch_settings_dictionary = load_json_by_file_name(Constants.SWITCH_JSON_FILE_NAME)
    usom_blocked_url_list = load_json_by_file_name(Constants.BLOCKED_URL_JSON_FILE_NAME)
    result = create_dropped_table_entries()
    write_json_to_file(result, Constants.SWITCH_JSON_FILE_NAME)