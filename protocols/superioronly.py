''' module of Superior-Only data transfer '''
import geocalc
import simtimer

import epidemic

class SuperiorOnlyHandoff(epidemic.EpidemicHandoff):
    ''' Superior-Only Handoff '''

    def __init__(self, group_id, global_params):
        epidemic.EpidemicHandoff.__init__(self)
        self.find_level(group_id, global_params)


    def find_level(self, group_id, global_params):
        if 'Paths' not in global_params.envt_params.groups[group_id]:
            possible_types = ['0']
        else:
            possible_types = global_params.envt_params.groups[group_id]['Paths'][:]
        for i in range(len(possible_types)):
            possible_types[i] = int(possible_types[i])
        min_type = min(possible_types)

        available_types = global_params.envt_params.envt['Path_Types'].values()
        for i in range(len(available_types)):
            available_types[i] = int(available_types[i])
        max_type = max(available_types)

        self.level = max_type - min_type


    ## Function for exchanging data with all the neighbors
    def exchange_data(self, mvmt_ob, global_params):

        msgs = mvmt_ob.buffer[:]

        # Extract all messages from the buffer of movement object
        src_msg_data = []
        for msg_tuple in msgs:
            src_msg_data.append(msg_tuple[0])            

        # Copy the messages to neighbor nodes
        for node in self.neighbor_dict:
            # Discard the nodes at lower levels
            if self.level <= node.protocol_obj.level:
                continue
            mobile_status = global_params.envt_params.groups[node.group_id]['Mobile']
            if not mobile_status:
                continue
            dst_msg_data = []
            for msg_tuple in node.buffer[:]:
                dst_msg_data.append(msg_tuple[0])

            msgs_not_in_node = set(src_msg_data) - set(dst_msg_data)
            if global_params.gui_ob:
                msg_ids = []
                for msg in msgs_not_in_node:
                    msg_ids.append(msg.e_id)
                    if msg_ids:
                        global_params.gui_ob.print_msg('STAT3', '%s -> %s: %s' \
                                                       % (mvmt_ob.obj_id, node.obj_id, \
                                                          str(msg_ids)))
            for msg in msgs_not_in_node:
                node.buffer.append([msg, mvmt_ob.obj_id])

            # Clear the buffer on data transfer
            mvmt_ob.buffer = []


    def execute_protocol(self, mvmt_ob, global_params):
        # Find the neighbors
        self.find_neighbors(mvmt_ob, global_params)
        self.print_neighbors(mvmt_ob, global_params.gui_ob)
        self.exchange_data(mvmt_ob, global_params)
        

    def print_neighbors(self, mvmt_ob, gui_ob):
        if not gui_ob:
            return 

        for node in self.neighbor_dict:
            distance = self.neighbor_dict[node][0]
            already_neighbor = self.neighbor_dict[node][1]
            if not already_neighbor:                
                # gui_ob.print_msg('STAT1', '%s -> %s (%.4f)' % (mvmt_ob.obj_id, node.obj_id, distance))
                gui_ob.print_msg('STAT2', '%s -> %s (%d)' % (mvmt_ob.obj_id, node.obj_id, distance * 1000))

        return 
                
        
