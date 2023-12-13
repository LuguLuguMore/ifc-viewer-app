import tkinter as tk
from tkinter import ttk
import ifcopenshell

class IfcViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("IFC Viewer")

        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, columns=('Properties'))
        self.tree.heading('#0', text='IFC Elements')
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree.bind("<ButtonRelease-1>", self.show_properties)

        self.property_frame = ttk.Frame(self.master)
        self.property_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.property_label = ttk.Label(self.property_frame, text="Properties:")
        self.property_label.pack()

        self.property_text = tk.Text(self.property_frame, wrap='none')
        self.property_text.pack(fill=tk.BOTH, expand=True)

    def load_ifc_file(self, file_path):
        self.ifc_file = ifcopenshell.open(file_path)
        self.populate_tree()

    """def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for element in self.ifc_file.by_type('IfcProduct'):
            self.tree.insert('', 'end', element.GlobalId, text="%s: %s" %(element.get_info()["type"], element.Name))"""

    """
    def populate_tree(self):
        elements = [(element.GlobalId, element.Name, element.is_a()) for element in self.ifc_file.by_type('IfcProduct')]
        elements.sort(key=lambda x: x[2])  # Sort by IFC type

        self.tree.delete(*self.tree.get_children())
        for element_id, element_name, element_type in elements:
            self.tree.insert('', 'end', element_id, text=element_name, values=(element_type,))"""
    
    """def populate_tree(self):
        self.tree.delete(*self.tree.get_children())

        # Define the order of IFC types
        ifc_types_order = ['IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey', 'IfcElement']

        for ifc_type in ifc_types_order:
            for element in self.ifc_file.by_type(ifc_type):
                self.tree.insert('', 'end', element.GlobalId, text=element.Name, values=(ifc_type,))"""
    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())

        for project in self.ifc_file.by_type('IfcProject'):
            project_id = project.GlobalId
            project_item = self.tree.insert('', 'end', project_id, text=f"{project.Name} (IfcProject)")

            for rel_aggregates in project.IsDecomposedBy:
                for site in rel_aggregates.RelatedObjects:
                    if site.is_a('IfcSite'):
                        site_id = site.GlobalId
                        site_item = self.tree.insert(project_item, 'end', site_id, text=f"{site.Name} (IfcSite)")

                        for rel_aggregates_building in site.IsDecomposedBy:
                            for building in rel_aggregates_building.RelatedObjects:
                                if building.is_a('IfcBuilding'):
                                    building_id = building.GlobalId
                                    building_item = self.tree.insert(site_item, 'end', building_id, text=f"{building.Name} (IfcBuilding)")

                                    for rel_aggregates_storey in building.IsDecomposedBy:
                                        for storey in rel_aggregates_storey.RelatedObjects:
                                            if storey.is_a('IfcBuildingStorey'):
                                                storey_id = storey.GlobalId
                                                storey_item = self.tree.insert(building_item, 'end', storey_id, text=f"{storey.Name} (IfcBuildingStorey)")

                                                for rel_contained_elements in storey.ContainsElements:
                                                    for element in rel_contained_elements.RelatedElements:
                                                        element_id = element.GlobalId
                                                        element_item = self.tree.insert(storey_item, 'end', element_id, text=f"{element.Name} (Element)")

        # Expand the root node for better visibility
        self.tree.item(self.tree.focus(), open=True)


        # Expand the root node for better visibility
        self.tree.item(self.tree.focus(), open=True)





    def show_properties(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            element_id = selected_item[0]
            selected_element = self.ifc_file.by_id(element_id)
            properties = self.get_element_properties(selected_element)
            self.display_properties(properties)
    """
    def get_element_properties(self, element):
        properties = {}
        # print("element: ", element)
        # print("element.get_info(): ", element.get_info())
        for attribute in element.get_info():
            # print("attribute: ",attribute)
            if type(attribute) is str:
                properties[attribute] = element.get_info()[attribute]
            else:
                properties[attribute.Name()] = attribute.get_info()
        return properties
    """
    def get_element_properties(self, element):
        properties = element.get_info()

        return properties

    def display_properties(self, properties):
        self.property_text.delete('1.0', tk.END)
        for key, value in properties.items():
            self.property_text.insert(tk.END, f"{key}: {value}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = IfcViewer(root)
    app.load_ifc_file(r"utils\LM_AR_31_V1.ifc")
    # Replace 'path/to/your/ifcfile.ifc' with the actual path to your IFC file
    # app.load_ifc_file('path/to/your/ifcfile.ifc')
	
    root.mainloop()
