# Author: Dr. Shayan Taheri.
# File Content: The Python program for parsing a netlist and ...
# ... counting the number of clock cycles for propagation of ...
# ... data from corrupted cells to sensitive cells.

import argparse

# Function for Parsing the Netlist File.
def parse_netlist(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        
        # Parsing the first section: Total Nets.
        total_nets = int(lines.pop(0).strip())
        
        # Parsing the second section: All Cells.
        all_cells = {}
        for _ in range(total_nets):
            line = lines.pop(0).strip().split()
            cell_type = line[0]
            cell_name = line[1]
            associated_cells = line[2:]
            all_cells[cell_name] = {
                "Cell Type": cell_type,
                "Associated Cells": associated_cells
            }
            
        # Parsing the third section: Total Queries.
        total_queries = int(lines.pop(0).strip())
        
        # Parsing the fourth section: Corrupted Cells.
        corrupted_cells = {}
        for _ in range(total_queries):
            line = lines.pop(0).strip().split()
            corrupted_cell = line[0]
            sensitive_cell = line[1]
            if corrupted_cell in corrupted_cells:
                corrupted_cells[corrupted_cell].append(sensitive_cell)
            else:
                corrupted_cells[corrupted_cell] = [sensitive_cell]
        
        # Storing parsed data in the main data structure.
        data_structure = {
            "Total Nets": total_nets,
            "All Cells": all_cells,
            "Total Queries": total_queries,
            "Corrupted Cells": corrupted_cells
        }
        
        return data_structure

# Function to determine the connection path from corrupted to sensitive cell.
def track_path(current, target, all_cells, visited, path=[]):
    if current == target:
        return path + [current]
    
    visited.add(current)
    paths = []
    
    for assoc_cell in all_cells[current]["Associated Cells"]:
        if assoc_cell not in visited:
            potential_path = track_path(assoc_cell, target, all_cells, visited, path + [current])
            if potential_path:
                paths.append(potential_path)
    
    # Return the shortest path with minimum DFFs.
    paths.sort(key=lambda p: len([cell for cell in p if all_cells[cell]["Cell Type"] == "DFF"]))
    
    return paths[0] if paths else []

# Function to analyze cell interactions.
def cell_interaction_analysis(parsed_data):
    all_cells = parsed_data["All Cells"]
    corrupted_cells_data = parsed_data["Corrupted Cells"]
    
    for corrupted, sensitive_list in corrupted_cells_data.items():
        for sensitive in sensitive_list:
            visited = set()
            path = track_path(corrupted, sensitive, all_cells, visited)
            
            if path:
                connection_status = "Available"

                # Counting the number of DFFs in the path.
                # If the first cell in the path is a DFF, then we need to subtract 1 from the total count.
                # This is because the first DFF is the corrupted cell itself and its timing for ...
                # ... production of a new corrupted data (i.e., one clock cycle) should not be considered.
                # It is assumed that the corrupted cell already has a corrupted data at its output port ...
                # ... and the data is ready to be propagated to the sensitive cell.
                if all_cells[path[0]]["Cell Type"] == "DFF":
                    dff_count = len([cell for cell in path if all_cells[cell]["Cell Type"] == "DFF"]) - 1
                else:
                    dff_count = len([cell for cell in path if all_cells[cell]["Cell Type"] == "DFF"])
                
            else:
                connection_status = "Unavailable"
                dff_count = -1
            
            # For same cell cases.
            if corrupted == sensitive:
                dff_count = 0
                
            print(f"Corrupted Cell: {corrupted}, Sensitive Cell: {sensitive}, Connection: {connection_status}, Clock Cycles: {dff_count}")

if __name__ == '__main__':
    # Argument parser setup.
    parser = argparse.ArgumentParser(description='Parse Netlist.txt')
    parser.add_argument('file_name', type=str, help='Path to the netlist file')
    args = parser.parse_args()

    # Parsing and printing the output.
    parsed_data = parse_netlist(args.file_name)
    for key, value in parsed_data.items():
        print(f"{key}: {value}\n")

    # Performing cell interaction analysis.
    cell_interaction_analysis(parsed_data)