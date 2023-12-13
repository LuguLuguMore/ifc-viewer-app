import tkinter as tk
from tkinter import ttk
import ifcopenshell


class IfcViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("IFC Viewer")

        # Frame for IFC tree
        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y)

        # IFC Treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=('Properties'))
        self.tree.heading('#0', text='IFC Elements')
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree.bind("<ButtonRelease-1>", self.show_properties)

        # Frame for Properties
        self.properties_frame = ttk.Frame(self.master)
        self.properties_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.property_label = ttk.Label(self.properties_frame, text="Properties:")
        self.property_label.pack()

        self.property_text = tk.Text(self.properties_frame, wrap='none')
        self.property_text.pack(fill=tk.BOTH, expand=True)

        # Frame for PSETs
        self.pset_frame = ttk.Frame(self.master)
        self.pset_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.pset_label = ttk.Label(self.pset_frame, text="PSETs:")
        self.pset_label.pack()

        self.pset_text = tk.Text(self.pset_frame, wrap='none')
        self.pset_text.pack(fill=tk.BOTH, expand=True)

    def load_ifc_file(self, file_path):
        self.ifc_file = ifcopenshell.open(file_path)
        self.populate_tree()

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
                                                        element_type = element.get_info()["type"]
                                                        element_item = self.tree.insert(storey_item, 'end', element_id, text=f"{element.Name} ({element_type})")

    def show_properties(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            element_id = selected_item[0]
            selected_element = self.ifc_file.by_id(element_id)
            properties = self.get_element_properties(selected_element)
            self.display_properties(properties)

            # Display PSETs
            psets = self.get_element_psets(selected_element)
            self.display_psets(psets)

    def get_element_properties(self, element):
        properties = element.get_info()

        return properties

    def display_properties(self, properties):
        self.property_text.delete('1.0', tk.END)
        for key, value in properties.items():
            self.property_text.insert(tk.END, f"{key}: {value}\n")

    def get_element_psets(self, element):
        psets = []
        for property_set in element.IsDefinedBy:
            if isinstance(property_set.RelatingPropertyDefinition, ifcopenshell.entity_instance) and \
                    property_set.RelatingPropertyDefinition.is_a('IfcPropertySet'):
                pset_name = property_set.RelatingPropertyDefinition.Name
                psets.append((pset_name, property_set.RelatingPropertyDefinition))
        return psets

    def display_psets(self, psets):
        self.pset_text.delete('1.0', tk.END)
        for pset_name, pset_definition in psets:
            self.pset_text.insert(tk.END, f"{pset_name}:\n")
            for property_single_value in pset_definition.HasProperties:
                if isinstance(property_single_value, ifcopenshell.entity_instance) and \
                        property_single_value.is_a('IfcPropertySingleValue'):
                    name = property_single_value.Name
                    value = property_single_value.NominalValue.wrappedValue
                    self.pset_text.insert(tk.END, f"  {name}: {value}\n")
            self.pset_text.insert(tk.END, "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = IfcViewer(root)
    
    # Replace 'path/to/your/ifcfile.ifc' with the actual path to your IFC file
    app.load_ifc_file(r"utils\LM_AR_31_V1.ifc")

    root.mainloop()
