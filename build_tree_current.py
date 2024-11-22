#New
def build_tree(data, part_name, recipe_type, target_quantity, visited=None):
    if visited is None:
        visited = set()

    # Check for circular dependency
    if (part_name, recipe_type) in visited:
        return {"Error": f"Circular dependency detected for part '{part_name}' with recipe '{recipe_type}'."}

    # Mark this part and recipe as visited
    visited.add((part_name, recipe_type))
    
    tree = {}

    # Determine the correct recipe type for the part itself (default to _Standard if no alternate specified)
    alternate_recipe_row = alternate_data[(alternate_data['Name'] == part_name) & (alternate_data['Selection'] == True)]
    current_recipe = alternate_recipe_row['Alternate_Recipe'].iloc[0] if not alternate_recipe_row.empty else recipe_type
    
     # Filter the dataset for the specified part and recipe type
    part_data = data[(data['Name'] == part_name) & (data['Recipe'] == current_recipe)]
    if part_data.empty:
        return {
        "Error": f"Part '{part_name}' with recipe '{current_recipe}' not found.",
        "Required Quantity": 0,
        "Produced In": "Unknown",
        "No. of Machines": 0,
        "Recipe": current_recipe,
        "Subtree": {}
        }
    
   
        
    # Iterate over base inputs for the given part
    for _, row in part_data.iterrows():
        base_input_name = row['Base Input']
        source_level = row['Source Level']
        base_demand = row['Base Demand p/m']
        
        # Determine the correct recipe type for the part itself (default to _Standard if no alternate specified)
        alternate_recipe_row = alternate_data[(alternate_data['Name'] == part_name) & (alternate_data['Selection'] == True)]
        current_recipe = alternate_recipe_row['Alternate_Recipe'].iloc[0] if not alternate_recipe_row.empty else recipe_type
         
        
    
        # Lookup base input data to get its supply rate and produced in machine
        base_input_data = data[(data['Name'] == base_input_name) & (data['Recipe'] == current_recipe)]
        if base_input_data.empty:
            base_supply = 0
            produced_in = "Unknown"
        else:
            base_supply = base_input_data['Base Supply p/m'].iloc[0]
            produced_in = base_input_data['Produced In (Automated)'].iloc[0]
        
        # Skip parts with source_level == -2
        if source_level == -2 and base_input_name == 0:
            continue
        
        # Calculate required input quantity for the target output
        if pd.notna(base_demand) and pd.notna(base_supply) and base_supply > 0:
            #required_quantity = base_demand * target_quantity
            required_quantity = (base_demand / base_supply) * target_quantity
        else:
            required_quantity = 0

        # Debugging print to verify values
        print(f"Base Input: {base_input_name}, Required Quantity: {required_quantity}, Base Demand: {base_demand}, Base Supply: {base_supply}")
        
        # Calculate the number of machines needed to produce the required amount
        no_of_machines = required_quantity / base_supply if base_supply else 0

        # Recursively build the tree for the base input
        subtree = build_tree(data, base_input_name, current_recipe, required_quantity, visited)
        tree[base_input_name] = {
            "Required Quantity": required_quantity,
            "Produced In": produced_in,
            "No. of Machines": no_of_machines,
            "Recipe": current_recipe,  # Add the recipe name for the base input
            "Subtree": subtree
        }
    
    # Unmark this part and recipe after processing
    visited.remove((part_name, recipe_type))
    
    return tree